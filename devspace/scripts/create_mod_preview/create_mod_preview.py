from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
TEXTURES = ROOT / "devspace" / "textures"
OUT_DIR = ROOT / "devspace" / "preview"
HOST_IMAGE = Path(r"C:\Users\LIMANC~1\AppData\Local\Temp\codex-clipboard-7436dffc-ea1f-4a66-a2af-6a1a15f46b80.png")

W = H = 1024
TITLE = "QoL - Medical Icons"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\bahnschrift.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


FONT_TITLE = font(70, True)
FONT_SUB = font(31, False)
FONT_SMALL = font(24, True)


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def gradient_bg(seed: int, mood: str) -> Image.Image:
    random.seed(seed)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    px = img.load()
    if mood == "green":
        top = (13, 31, 29)
        bot = (34, 58, 53)
        glow = (49, 151, 122)
    elif mood == "red":
        top = (25, 22, 20)
        bot = (50, 37, 31)
        glow = (166, 63, 45)
    else:
        top = (14, 21, 28)
        bot = (28, 41, 50)
        glow = (75, 137, 161)
    for y in range(H):
        t = y / (H - 1)
        base = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        for x in range(W):
            dx = (x - W * 0.65) / W
            dy = (y - H * 0.38) / H
            g = max(0.0, 1.0 - math.sqrt(dx * dx + dy * dy) * 2.2)
            px[x, y] = rgba(tuple(min(255, int(base[i] + glow[i] * g * 0.45)) for i in range(3)))

    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(0, H, 64):
        draw.line((0, y, W, y), fill=(255, 255, 255, 9), width=1)
    for x in range(0, W, 64):
        draw.line((x, 0, x, H), fill=(255, 255, 255, 6), width=1)
    for _ in range(350):
        x, y = random.randrange(W), random.randrange(H)
        a = random.randrange(8, 28)
        img.putpixel((x, y), (255, 245, 220, a))
    return img.filter(ImageFilter.GaussianBlur(0.25))


def shadow(size: tuple[int, int], radius: int = 18, alpha: int = 120) -> Image.Image:
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=24, fill=(0, 0, 0, alpha))
    return im.filter(ImageFilter.GaussianBlur(radius))


def paste_with_shadow(base: Image.Image, obj: Image.Image, xy: tuple[int, int], scale: float = 1.0, blur: int = 14) -> None:
    if scale != 1.0:
        obj = obj.resize((max(1, int(obj.width * scale)), max(1, int(obj.height * scale))), Image.Resampling.LANCZOS)
    alpha = obj.getchannel("A")
    sh = Image.new("RGBA", obj.size, (0, 0, 0, 120))
    sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(sh, (xy[0] + 10, xy[1] + 14))
    base.alpha_composite(obj, xy)


def chroma_extract(crop: tuple[int, int, int, int]) -> Image.Image:
    src = Image.open(HOST_IMAGE).convert("RGBA").crop(crop)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp = src.load()
    op = out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = sp[x, y]
            green = g > 145 and r < 95 and b < 95
            gray = abs(r - g) < 12 and abs(g - b) < 12 and 170 < r < 230
            if not green and not gray:
                op[x, y] = (r, g, b, a)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out


def load_icons() -> list[tuple[str, Image.Image]]:
    icons: list[tuple[str, Image.Image]] = []
    for path in sorted(TEXTURES.glob("*/items/*/icon.png")):
        name = path.parent.name
        icons.append((name, Image.open(path).convert("RGBA")))
    return icons


def icon_card(icon: Image.Image, size: int = 112, label: str | None = None) -> Image.Image:
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(card, "RGBA")
    d.rounded_rectangle((4, 4, size - 5, size - 5), radius=18, fill=(15, 18, 18, 204), outline=(194, 222, 203, 70), width=2)
    d.rounded_rectangle((8, 8, size - 9, size - 9), radius=14, outline=(255, 255, 255, 26), width=1)
    icon_big = icon.resize((80, 80), Image.Resampling.NEAREST)
    card.alpha_composite(icon_big, ((size - 80) // 2, 15))
    if label:
        text = label[:10].upper()
        f = font(12, True)
        bbox = d.textbbox((0, 0), text, font=f)
        d.text(((size - (bbox[2] - bbox[0])) // 2, size - 22), text, font=f, fill=(198, 215, 204, 205))
    return card


def draw_title(draw: ImageDraw.ImageDraw, x: int, y: int, align: str = "left") -> None:
    bbox = draw.textbbox((0, 0), TITLE, font=FONT_TITLE)
    tw = bbox[2] - bbox[0]
    if align == "center":
        x = (W - tw) // 2
    for ox, oy, fill in [(5, 6, (0, 0, 0, 160)), (0, 0, (238, 231, 208, 255))]:
        draw.text((x + ox, y + oy), TITLE, font=FONT_TITLE, fill=fill)


def draw_badge(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, color: tuple[int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=18, fill=rgba(color, 198), outline=(255, 255, 255, 70), width=2)
    bbox = draw.textbbox((0, 0), text, font=FONT_SMALL)
    draw.text((box[0] + (box[2] - box[0] - bbox[2] + bbox[0]) // 2, box[1] + 11), text, font=FONT_SMALL, fill=(246, 241, 220, 255))


def variant_hero(icons: list[tuple[str, Image.Image]], medic: Image.Image, nosyringe: Image.Image) -> Image.Image:
    img = gradient_bg(7, "green")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title(d, 296, 86)
    d.text((301, 170), "clearer medicine at a glance", font=FONT_SUB, fill=(184, 217, 201, 235))
    paste_with_shadow(img, medic, (62, 56), scale=0.78, blur=10)
    paste_with_shadow(img, nosyringe, (806, 172), scale=0.48, blur=10)
    draw_badge(d, (306, 242, 709, 302), "ONE SYRINGE LOOK -> MANY ICONS", (45, 112, 91))

    chosen_names = ["stabilozine", "antirad", "combatstimulant", "cyanide", "pomegrenadeextract", "antiparalysis", "hyperzine", "opium", "liquidoxygenite"]
    by_name = {n: im for n, im in icons}
    chosen = [(n, by_name[n]) for n in chosen_names if n in by_name]
    positions = [(174, 366), (322, 342), (470, 366), (618, 342), (766, 366), (248, 548), (396, 576), (544, 548), (692, 576)]
    for (name, icon), pos in zip(chosen, positions):
        card = icon_card(icon, 126, None)
        paste_with_shadow(img, card, pos, 1, 8)
    d.rounded_rectangle((95, 820, 930, 904), radius=28, fill=(8, 13, 13, 178), outline=(255, 255, 255, 36), width=2)
    d.text((151, 845), "Barotrauma-style medical inventory icons", font=FONT_SUB, fill=(235, 231, 209, 245))
    return img


def variant_before_after(icons: list[tuple[str, Image.Image]], medic: Image.Image, nosyringe: Image.Image) -> Image.Image:
    img = gradient_bg(11, "red")
    d = ImageDraw.Draw(img, "RGBA")
    draw_title(d, 0, 60, "center")
    d.rounded_rectangle((76, 194, 470, 876), radius=30, fill=(19, 18, 17, 195), outline=(177, 84, 65, 105), width=3)
    d.rounded_rectangle((554, 194, 948, 876), radius=30, fill=(14, 22, 21, 205), outline=(106, 185, 147, 112), width=3)
    d.text((171, 226), "BEFORE", font=font(44, True), fill=(224, 154, 127, 245))
    d.text((674, 226), "AFTER", font=font(44, True), fill=(180, 231, 198, 245))
    paste_with_shadow(img, nosyringe, (178, 328), scale=1.15, blur=10)
    d.line((170, 665, 376, 665), fill=(221, 65, 43, 230), width=14)
    d.text((142, 705), "same-looking syringes", font=FONT_SUB, fill=(211, 190, 176, 220))
    d.polygon([(575, 514), (524, 480), (524, 503), (484, 503), (484, 525), (524, 525), (524, 548)], fill=(231, 220, 185, 230))
    chosen = icons[0:0]
    for wanted in ["adrenaline", "stabilozine", "antinarc", "cyanide", "hyperzine", "pressurestabilizer", "antibiotics", "antirad"]:
        for n, im in icons:
            if n == wanted:
                chosen.append((n, im))
                break
    positions = [(602, 315), (737, 315), (602, 450), (737, 450), (602, 585), (737, 585), (602, 720), (737, 720)]
    for (name, icon), pos in zip(chosen, positions):
        paste_with_shadow(img, icon_card(icon, 112, None), pos, 1, 7)
    paste_with_shadow(img, medic, (55, 45), scale=0.43, blur=8)
    return img


def variant_showcase(icons: list[tuple[str, Image.Image]], medic: Image.Image, nosyringe: Image.Image) -> Image.Image:
    img = gradient_bg(19, "blue")
    d = ImageDraw.Draw(img, "RGBA")
    paste_with_shadow(img, medic, (78, 54), scale=0.52, blur=8)
    paste_with_shadow(img, nosyringe, (820, 58), scale=0.44, blur=8)
    draw_title(d, 0, 118, "center")
    d.text((319, 216), "inventory clarity for every medic", font=FONT_SUB, fill=(190, 217, 224, 230))

    chosen = icons[:]
    random.Random(3).shuffle(chosen)
    chosen = chosen[:30]
    x0, y0 = 108, 318
    gap = 13
    size = 104
    for idx, (name, icon) in enumerate(chosen):
        col = idx % 6
        row = idx // 6
        card = icon_card(icon, size, None)
        paste_with_shadow(img, card, (x0 + col * (size + gap), y0 + row * (size + gap)), 1, 6)
    d.rounded_rectangle((184, 893, 840, 950), radius=20, fill=(12, 18, 23, 190), outline=(255, 255, 255, 38), width=2)
    d.text((260, 907), "ampoules / vials / injectors / antidotes / toxins", font=font(26, False), fill=(232, 231, 212, 235))
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    medic = chroma_extract((50, 75, 320, 355)).resize((270, 270), Image.Resampling.LANCZOS)
    nosyringe = chroma_extract((390, 180, 565, 355)).resize((190, 190), Image.Resampling.LANCZOS)
    medic.save(OUT_DIR / "medic_class_logo_extracted.png")
    nosyringe.save(OUT_DIR / "no_standard_syringe_extracted.png")

    icons = load_icons()
    variants = {
        "qol_medical_icons_preview_hero.png": variant_hero(icons, medic, nosyringe),
        "qol_medical_icons_preview_before_after.png": variant_before_after(icons, medic, nosyringe),
        "qol_medical_icons_preview_showcase.png": variant_showcase(icons, medic, nosyringe),
    }
    for name, image in variants.items():
        image.save(OUT_DIR / name)
        image.resize((512, 512), Image.Resampling.LANCZOS).save(OUT_DIR / name.replace(".png", "_512.png"))


if __name__ == "__main__":
    main()
