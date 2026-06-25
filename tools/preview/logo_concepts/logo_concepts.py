from argparse import ArgumentParser
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


SIZE = 268
FRAME_MS = 70
SCRIPT_DIR = Path(__file__).resolve().parent


ICON_KEYS = [
    ("vial/items/antirad/icon.png", "ANTIRAD"),
    ("vial/items/calyxanide/icon.png", "CALYX"),
    ("vial/items/antiparalysis/icon.png", "ANTIPARA"),
    ("ampoule/items/stabilozine/icon.png", "STABIL"),
    ("ampoule/items/adrenaline/icon.png", "ADREN"),
    ("pocket_injector/items/hyperzine/icon.png", "HYPER"),
    ("pocket_injector/items/steroids/icon.png", "STEROID"),
    ("insulin_syringe/items/liquidoxygenite/icon.png", "OXY"),
]


def find_project_root() -> Path:
    for path in [SCRIPT_DIR, *SCRIPT_DIR.parents]:
        if (path / "filelist.xml").exists():
            return path
    raise RuntimeError("Could not find project root marker filelist.xml")


PROJECT_ROOT = find_project_root()


def parse_args():
    parser = ArgumentParser(
        description="Generate animated 268x268 GIF logo concepts from Medical Icons item icons."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print outputs without writing GIF files.",
    )
    parser.add_argument(
        "--output-dir",
        default="preview/logo_concepts",
        help="Output folder, relative to the project root unless absolute.",
    )
    return parser.parse_args()


def resolve_output_dir(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_icons():
    base = PROJECT_ROOT / "source" / "textures"
    icons = []
    for relative, label in ICON_KEYS:
        path = base / relative
        if not path.exists():
            continue
        image = Image.open(path).convert("RGBA")
        icons.append((image, label))
    if len(icons) < 5:
        paths = sorted(base.glob("**/icon.png"))
        icons = [(Image.open(path).convert("RGBA"), path.parent.name.upper()) for path in paths[:8]]
    if not icons:
        raise RuntimeError("No icon.png files found under source/textures")
    return icons


def fit_icon(icon: Image.Image, target: int) -> Image.Image:
    alpha = icon.getchannel("A")
    bbox = alpha.getbbox()
    cropped = icon.crop(bbox) if bbox else icon
    cropped.thumbnail((target, target), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    out.alpha_composite(cropped, ((target - cropped.width) // 2, (target - cropped.height) // 2))
    return out


def tinted(icon: Image.Image, color, amount=0.35) -> Image.Image:
    overlay = Image.new("RGBA", icon.size, color)
    out = Image.blend(icon, overlay, amount)
    out.putalpha(icon.getchannel("A"))
    return out


def background(frame_index=0, pulse=0.0):
    img = Image.new("RGBA", (SIZE, SIZE), (8, 13, 16, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(SIZE):
        t = y / SIZE
        r = int(6 + 10 * t)
        g = int(13 + 18 * t)
        b = int(15 + 22 * t)
        draw.line((0, y, SIZE, y), fill=(r, g, b, 255))
    for x in range(-SIZE, SIZE, 18):
        alpha = 22 + int(10 * pulse)
        draw.line((x + frame_index % 18, 0, x + SIZE + frame_index % 18, SIZE), fill=(35, 77, 82, alpha))
    for y in range(8, SIZE, 18):
        draw.line((0, y, SIZE, y), fill=(31, 63, 66, 20))
    draw.rectangle((7, 7, SIZE - 8, SIZE - 8), outline=(49, 88, 89, 150), width=2)
    draw.rectangle((13, 13, SIZE - 14, SIZE - 14), outline=(6, 11, 13, 190), width=2)
    return img


def paste_center(base: Image.Image, item: Image.Image, x: int, y: int):
    base.alpha_composite(item, (int(x - item.width / 2), int(y - item.height / 2)))


def draw_cross(draw: ImageDraw.ImageDraw, center, size, color):
    x, y = center
    s = size
    w = max(5, size // 3)
    draw.rounded_rectangle((x - w // 2, y - s, x + w // 2, y + s), radius=2, fill=color)
    draw.rounded_rectangle((x - s, y - w // 2, x + s, y + w // 2), radius=2, fill=color)


def draw_pulse(draw: ImageDraw.ImageDraw, y, color, phase=0, width=2):
    pts = [
        (30, y),
        (68, y),
        (78, y - 18),
        (91, y + 23),
        (106, y - 34),
        (126, y + 6),
        (148, y),
        (166, y),
        (178, y - 15),
        (192, y + 12),
        (207, y),
        (238, y),
    ]
    shifted = [((x + phase) % (SIZE + 40) - 20, py) for x, py in pts]
    draw.line(shifted, fill=color, width=width, joint="curve")


def save_gif(frames, path: Path):
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )


def carousel(icons):
    prepared = [fit_icon(icon, 66) for icon, _ in icons[:8]]
    frames = []
    total = 36
    for i in range(total):
        p = i / total
        frame = background(i, abs(sin(p * pi * 2)))
        draw = ImageDraw.Draw(frame, "RGBA")
        draw.ellipse((48, 48, 220, 220), outline=(58, 122, 119, 90), width=2)
        draw.ellipse((78, 78, 190, 190), outline=(109, 42, 45, 70), width=2)
        draw_cross(draw, (134, 134), 28 + int(5 * sin(p * pi * 2)), (167, 41, 47, 210))
        draw_pulse(draw, 213, (106, 205, 190, 150), phase=i * 6, width=2)
        for n, icon in enumerate(prepared):
            angle = p * pi * 2 + n * pi * 2 / len(prepared)
            radius = 76 + 7 * sin(p * pi * 2 + n)
            x = 134 + cos(angle) * radius
            y = 134 + sin(angle) * radius
            scale = 0.82 + 0.22 * (sin(angle + pi / 2) + 1) / 2
            item = icon.resize((int(icon.width * scale), int(icon.height * scale)), Image.Resampling.LANCZOS)
            paste_center(frame, item, x, y)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def scanner(icons):
    prepared = [fit_icon(icon, 116) for icon, _ in icons[:6]]
    frames = []
    total = 42
    for i in range(total):
        icon = prepared[(i // 7) % len(prepared)]
        local = (i % 7) / 6
        frame = background(i, local)
        draw = ImageDraw.Draw(frame, "RGBA")
        scan_y = int(44 + local * 178)
        frame.alpha_composite(icon, ((SIZE - icon.width) // 2, 72))
        draw.line((32, scan_y, 236, scan_y), fill=(118, 232, 207, 230), width=3)
        draw.rectangle((42, 64, 226, 206), outline=(83, 176, 162, 170), width=2)
        draw_pulse(draw, 222, (187, 57, 62, 170), phase=i * 4, width=2)
        draw_cross(draw, (215, 45), 16, (178, 45, 51, 210))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def before_after(icons):
    prepared = [fit_icon(icon, 92) for icon, _ in icons[:5]]
    frames = []
    total = 40
    for i in range(total):
        icon = prepared[(i // 8) % len(prepared)]
        local = (i % 8) / 7
        frame = background(i, local)
        draw = ImageDraw.Draw(frame, "RGBA")
        old = tinted(icon.filter(ImageFilter.GaussianBlur(0.6)), (55, 65, 66, 255), 0.72)
        paste_center(frame, old, 83, 124)
        wipe = min(1.0, local * 1.25)
        new = Image.new("RGBA", icon.size, (0, 0, 0, 0))
        new.alpha_composite(icon.crop((0, 0, int(icon.width * wipe), icon.height)), (0, 0))
        paste_center(frame, new, 185, 124)
        draw.line((134, 53, 134, 197), fill=(91, 143, 139, 130), width=2)
        draw.line((116, 124, 151, 124), fill=(120, 217, 203, 170), width=3)
        draw.polygon(((151, 124), (139, 116), (139, 132)), fill=(120, 217, 203, 170))
        scan_x = int(142 + local * 85)
        draw.line((scan_x, 68, scan_x, 180), fill=(131, 235, 213, 210), width=2)
        draw_cross(draw, (134, 218), 18, (174, 48, 52, 205))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def medkit_burst(icons):
    prepared = [fit_icon(icon, 64) for icon, _ in icons[:7]]
    frames = []
    total = 34
    targets = [(69, 80), (119, 58), (174, 76), (196, 139), (152, 181), (88, 177), (62, 133)]
    for i in range(total):
        p = i / (total - 1)
        frame = background(i, p)
        draw = ImageDraw.Draw(frame, "RGBA")
        draw.rounded_rectangle((64, 86, 204, 190), radius=10, fill=(22, 37, 39, 210), outline=(84, 110, 106, 170), width=3)
        draw.rounded_rectangle((105, 65, 163, 96), radius=8, outline=(83, 110, 108, 160), width=3)
        draw_cross(draw, (134, 136), 28, (171, 43, 48, 205))
        burst = min(1, p * 1.35)
        for n, icon in enumerate(prepared):
            tx, ty = targets[n]
            x = 134 + (tx - 134) * burst
            y = 136 + (ty - 136) * burst
            spin = (p * 16 + n * 9) % 360
            item = icon.rotate(spin, resample=Image.Resampling.BICUBIC, expand=True)
            paste_center(frame, item, x, y)
        draw_pulse(draw, 222, (120, 226, 207, 150), phase=i * 5, width=2)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def liquid_pulse(icons):
    prepared = [fit_icon(icon, 112) for icon, _ in icons[:6]]
    frames = []
    total = 42
    for i in range(total):
        p = i / total
        idx = (i // 7) % len(prepared)
        icon = prepared[idx]
        frame = background(i, abs(sin(p * pi * 2)))
        draw = ImageDraw.Draw(frame, "RGBA")
        glow_color = [(35, 202, 166), (208, 55, 69), (115, 196, 235), (229, 184, 73), (155, 98, 207), (109, 222, 123)][idx % 6]
        glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow, "RGBA")
        r = 44 + int(16 * sin(p * pi * 2) ** 2)
        gdraw.ellipse((134 - r, 127 - r, 134 + r, 127 + r), fill=(*glow_color, 58))
        glow = glow.filter(ImageFilter.GaussianBlur(13))
        frame.alpha_composite(glow)
        paste_center(frame, icon, 134, 124)
        draw_pulse(draw, 211, (*glow_color, 210), phase=i * 4, width=3)
        draw_cross(draw, (45, 45), 18, (178, 45, 51, 210))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def main():
    args = parse_args()
    out_dir = resolve_output_dir(args.output_dir)
    outputs = [
        out_dir / "medical_icons_logo_01_carousel.gif",
        out_dir / "medical_icons_logo_02_scanner.gif",
        out_dir / "medical_icons_logo_03_before_after.gif",
        out_dir / "medical_icons_logo_04_medkit_burst.gif",
        out_dir / "medical_icons_logo_05_liquid_pulse.gif",
    ]
    if args.dry_run:
        for output in outputs:
            print(output.relative_to(PROJECT_ROOT))
        return

    icons = load_icons()
    out_dir.mkdir(parents=True, exist_ok=True)
    concepts = [carousel, scanner, before_after, medkit_burst, liquid_pulse]
    for output, build in zip(outputs, concepts):
        frames = build(icons)
        save_gif(frames, output)
        print(output.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
