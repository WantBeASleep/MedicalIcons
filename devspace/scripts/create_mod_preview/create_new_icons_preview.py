from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
TEXTURES = ROOT / "devspace" / "textures"
OUT_DIR = ROOT / "devspace" / "preview"
STATUS_CSV = ROOT / "devspace" / "scripts" / "build_project" / "statusicons.csv"
STATUS_ICON_OUT = ROOT / "devspace" / "scripts" / "build_project" / "status_icons"

W = H = 1024
TITLE = "QoL - Medical Icons"
ICON_NAMES = ["ampoule", "dart_syringe", "insulin_syringe", "pocket_injector", "vial"]


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


def rgba(color: tuple[int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], alpha


def gradient_bg(seed: int = 11) -> Image.Image:
    random.seed(seed)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    px = img.load()
    top = (25, 22, 20)
    bot = (50, 37, 31)
    glow = (166, 63, 45)
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


def draw_title(draw: ImageDraw.ImageDraw, y: int = 63) -> None:
    bbox = draw.textbbox((0, 0), TITLE, font=FONT_TITLE)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    for ox, oy, fill in [(5, 6, (0, 0, 0, 160)), (0, 0, (238, 231, 208, 255))]:
        draw.text((x + ox, y + oy), TITLE, font=FONT_TITLE, fill=fill)


def paste_with_shadow(base: Image.Image, obj: Image.Image, xy: tuple[int, int], blur: int = 16) -> None:
    alpha = obj.getchannel("A")
    sh = Image.new("RGBA", obj.size, (0, 0, 0, 150))
    sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(sh, (xy[0] + 13, xy[1] + 18))
    base.alpha_composite(obj, xy)


def icon_card(icon: Image.Image, size: int = 176) -> Image.Image:
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(card, "RGBA")
    d.rounded_rectangle(
        (5, 5, size - 6, size - 6),
        radius=22,
        fill=(12, 18, 18, 222),
        outline=(194, 222, 203, 76),
        width=2,
    )
    d.rounded_rectangle((11, 11, size - 12, size - 12), radius=16, outline=(255, 255, 255, 26), width=1)
    icon_big = icon.resize((132, 132), Image.Resampling.NEAREST)
    card.alpha_composite(icon_big, ((size - icon_big.width) // 2, (size - icon_big.height) // 2))
    return card


def item_card(icon: Image.Image, size: int = 212) -> Image.Image:
    card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(card, "RGBA")
    d.rounded_rectangle(
        (5, 5, size - 6, size - 6),
        radius=24,
        fill=(12, 18, 18, 224),
        outline=(194, 222, 203, 82),
        width=2,
    )
    d.rounded_rectangle((12, 12, size - 13, size - 13), radius=18, outline=(255, 255, 255, 28), width=1)

    icon_big = icon.resize((150, 150), Image.Resampling.NEAREST)
    card.alpha_composite(icon_big, ((size - icon_big.width) // 2, (size - icon_big.height) // 2 + 4))
    return card


def load_icons() -> list[Image.Image]:
    return [Image.open(TEXTURES / name / "icon.png").convert("RGBA") for name in ICON_NAMES]


def load_status_map() -> dict[str, str]:
    with STATUS_CSV.open(newline="", encoding="utf-8") as f:
        return {row["identifier"]: row["statusicon"] for row in csv.DictReader(f)}


def texture_items(texture_name: str, status_map: dict[str, str]) -> list[tuple[str, Image.Image]]:
    items_dir = TEXTURES / texture_name / "items"
    items: list[tuple[str, Image.Image]] = []
    for item_dir in sorted(items_dir.iterdir()):
        if not item_dir.is_dir():
            continue
        if item_dir.name not in status_map:
            continue
        icon_path = STATUS_ICON_OUT / f"{item_dir.name}.png"
        if not icon_path.exists():
            icon_path = item_dir / "icon.png"
        if not icon_path.exists():
            continue
        icon = Image.open(icon_path).convert("RGBA")
        items.append((item_dir.name, icon))
    return items[:5]


def draw_texture_preview(texture_name: str, status_map: dict[str, str]) -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img, "RGBA")
    draw_title(d)

    items = texture_items(texture_name, status_map)
    positions_by_count = {
        1: [(406, 407)],
        2: [(294, 407), (518, 407)],
        3: [(184, 407), (406, 407), (628, 407)],
        4: [(294, 296), (518, 296), (294, 520), (518, 520)],
        5: [(184, 296), (406, 296), (628, 296), (294, 520), (518, 520)],
    }
    for (_identifier, icon), pos in zip(items, positions_by_count[len(items)]):
        paste_with_shadow(img, item_card(icon), pos)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = gradient_bg()
    d = ImageDraw.Draw(img, "RGBA")
    draw_title(d)

    positions = [
        (222, 296),
        (423, 296),
        (624, 296),
        (323, 520),
        (524, 520),
    ]
    for icon, pos in zip(load_icons(), positions):
        paste_with_shadow(img, icon_card(icon), pos)

    out = OUT_DIR / "qol_medical_icons_preview_new_icons.png"
    img.save(out)

    status_map = load_status_map()
    for texture_name in ICON_NAMES:
        preview = draw_texture_preview(texture_name, status_map)
        preview.save(OUT_DIR / f"qol_medical_icons_preview_{texture_name}_items.png")


if __name__ == "__main__":
    main()
