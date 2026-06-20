from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "devspace" / "statusicons"
OUT = STATUS / "concepts"
OUT.mkdir(parents=True, exist_ok=True)


def load(name: str) -> Image.Image:
    return Image.open(STATUS / name).convert("RGBA")


def alpha_composite(base: Image.Image, layer: Image.Image) -> Image.Image:
    out = base.copy()
    out.alpha_composite(layer)
    return out


def tint_alpha(source: Image.Image, color: tuple[int, int, int], strength: float = 1.0) -> Image.Image:
    src = source.convert("RGBA")
    px = src.load()
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    opx = out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = max(r, g, b) / 255
            nr = int(r * (1 - strength) + color[0] * lum * strength)
            ng = int(g * (1 - strength) + color[1] * lum * strength)
            nb = int(b * (1 - strength) + color[2] * lum * strength)
            opx[x, y] = (min(255, nr), min(255, ng), min(255, nb), a)
    return out


def diagonal_mix(a: Image.Image, b: Image.Image) -> Image.Image:
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    for y in range(a.height):
        for x in range(a.width):
            source = a if x + y < 23 else b
            out.putpixel((x, y), source.getpixel((x, y)))
    return out


def outline_alpha(img: Image.Image, color=(8, 13, 17, 190)) -> Image.Image:
    alpha = img.getchannel("A")
    grown = ImageOps.expand(alpha, border=1, fill=0).filter(ImageFilter.MaxFilter(3)).crop((1, 1, 25, 25))
    outline = Image.new("RGBA", img.size, color)
    outline.putalpha(Image.eval(grown, lambda p: min(190, p)))
    return alpha_composite(outline, img)


def tiny_pulse(color=(230, 152, 68, 205)) -> Image.Image:
    img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(4, 15), (8, 15), (10, 12), (12, 18), (15, 10), (17, 15), (21, 15)]
    d.line(pts, fill=color, width=2, joint="curve")
    d.point([(10, 11), (15, 9), (12, 19)], fill=(255, 212, 112, 190))
    return img


def paste_scaled(canvas: Image.Image, img: Image.Image, x: int, y: int, scale: int = 8) -> None:
    big = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
    canvas.alpha_composite(big, (x, y))


try:
    from PIL import ImageFilter
except ImportError as exc:
    raise SystemExit(exc)


haste = load("haste.png")
vigor = load("vigor.png")
combat = load("combatstimulant.png")
adrenaline = load("adrenalinerush.png")

variant_1 = alpha_composite(haste, tiny_pulse())

variant_2 = diagonal_mix(tint_alpha(haste, (110, 205, 230), 0.35), tint_alpha(vigor, (230, 151, 62), 0.55))

variant_3 = tint_alpha(combat, (220, 150, 63), 0.32)

vigor_small = vigor.resize((18, 18), Image.Resampling.LANCZOS)
variant_4 = haste.copy()
badge = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
badge.alpha_composite(vigor_small, (5, 3))
badge.putalpha(Image.eval(badge.getchannel("A"), lambda p: int(p * 0.52)))
variant_4 = alpha_composite(badge, variant_4)

variants = [
    ("haste", haste),
    ("vigor", vigor),
    ("combat", combat),
    ("adrenaline", adrenaline),
    ("A pulse", variant_1),
    ("B split", variant_2),
    ("C stimulant", variant_3),
    ("D ghost", variant_4),
]

for name, img in variants[4:]:
    img.save(OUT / f"hyperzine_{name.split()[0].lower()}.png")

scale = 8
tile_w = 24 * scale
tile_h = 24 * scale
pad_x = 24
pad_y = 34
label_h = 26
cols = 4
rows = 2
canvas = Image.new(
    "RGBA",
    (cols * tile_w + (cols + 1) * pad_x, rows * (tile_h + label_h) + (rows + 1) * pad_y),
    (14, 17, 19, 255),
)
d = ImageDraw.Draw(canvas)
font = ImageFont.load_default()

for i, (label, img) in enumerate(variants):
    col = i % cols
    row = i // cols
    x = pad_x + col * (tile_w + pad_x)
    y = pad_y + row * (tile_h + label_h + pad_y)
    d.rectangle((x - 1, y - 1, x + tile_w, y + tile_h), outline=(46, 55, 60, 255))
    paste_scaled(canvas, img, x, y, scale)
    d.text((x, y + tile_h + 8), label, fill=(207, 214, 216, 255), font=font)

canvas.save(OUT / "hyperzine_concepts.png")
print(OUT / "hyperzine_concepts.png")
