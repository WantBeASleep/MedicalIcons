from argparse import ArgumentParser
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

import build_medical_icons_logo as base


SIZE = base.SIZE
FRAME_MS = base.FRAME_MS
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = base.PROJECT_ROOT
GAME_ROOT = base.GAME_ROOT
OUT_DIR = PROJECT_ROOT / "preview" / "logo_variants"

TITLE_FONT = base.font("display", 25, "Bangers-Regular.ttf")
LABEL_FONT = base.font("display", 18, "Bangers-Regular.ttf")
SMALL_FONT = base.font("display", 13, "Bangers-Regular.ttf")
SHEET_FONT = base.font("bold", 15)


def parse_args():
    parser = ArgumentParser(description="Build creative animated logo variants for Medical Icons.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned outputs without writing GIF files.")
    return parser.parse_args()


def ease_out(t: float) -> float:
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def ease_in_out(t: float) -> float:
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)


def paste_center(frame: Image.Image, image: Image.Image, x: float, y: float):
    frame.alpha_composite(image, (round(x - image.width / 2), round(y - image.height / 2)))


def scale_icon(icon: Image.Image, factor: float) -> Image.Image:
    size = (max(1, round(icon.width * factor)), max(1, round(icon.height * factor)))
    return icon.resize(size, Image.Resampling.LANCZOS)


def glow_rect(draw: ImageDraw.ImageDraw, box, color, fill=(7, 6, 18, 220), radius=4):
    x0, y0, x1, y1 = box
    for grow, alpha in [(5, 38), (2, 82)]:
        draw.rounded_rectangle(
            (x0 - grow, y0 - grow, x1 + grow, y1 + grow),
            radius=radius + grow,
            outline=(*color, alpha),
            width=2,
        )
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=(*color, 220), width=2)


def draw_label(frame: Image.Image, item):
    draw = ImageDraw.Draw(frame, "RGBA")
    accent = item["accent"]
    glow_rect(draw, (18, 218, 250, 249), accent, fill=(6, 5, 17, 226), radius=4)
    base.add_glow_text(draw, (134, 234), item["label"], (*accent, 255), (*accent, 168), LABEL_FONT, stroke=2)


def draw_title(frame: Image.Image, frame_index: int):
    base.title_layer(frame, frame_index, TITLE_FONT)


def bg_terminal(frame_index: int, accent):
    img = base.draw_background(frame_index, accent, "medical")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((18, 69, 250, 210), outline=(94, 236, 218, 80), width=1)
    for y in (91, 121, 181):
        draw.line((26, y, 242, y), fill=(94, 236, 218, 26), width=1)
    for x in (72, 134, 196):
        draw.line((x, 75, x, 203), fill=(*accent, 22), width=1)
    return img


def bg_hull(frame_index: int, accent):
    img = base.draw_background(frame_index, accent, "hull")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 61, SIZE, 64), fill=(255, 235, 73, 200))
    for x in range(-40, SIZE, 28):
        draw.line((x, 63, x + 15, 63), fill=(255, 45, 153, 220), width=3)
    return img


def bg_abyss(frame_index: int, accent):
    img = base.draw_background(frame_index, accent, "abyss")
    haze = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(haze, "RGBA")
    for n in range(4):
        cx = 42 + n * 63 + sin(frame_index * 0.04 + n) * 5
        cy = 110 + sin(frame_index * 0.06 + n) * 18
        draw.ellipse((cx - 38, cy - 18, cx + 38, cy + 18), fill=(*accent, 13))
    return Image.alpha_composite(img, haze.filter(ImageFilter.GaussianBlur(11)))


def bg_modern(frame_index: int, accent):
    img = Image.new("RGBA", (SIZE, SIZE), (10, 6, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(SIZE):
        t = y / (SIZE - 1)
        draw.line((0, y, SIZE, y), fill=(round(9 + 14 * t), round(5 + 5 * t), round(24 + 26 * t), 255))
    draw.polygon([(0, 61), (0, SIZE), (112, SIZE), (154, 61)], fill=(5, 19, 35, 222))
    draw.polygon([(154, 61), (112, SIZE), (SIZE, SIZE), (SIZE, 61)], fill=(40, 8, 42, 216))
    draw.line((154, 61, 112, SIZE), fill=(255, 236, 74, 255), width=4)
    draw.line((149, 61, 107, SIZE), fill=(255, 51, 159, 210), width=2)
    for n in range(7):
        x = 18 + n * 38 + sin(frame_index * 0.03 + n) * 2
        draw.line((x, 76, x + 28, 205), fill=(*accent, 22), width=1)
    draw.rectangle((5, 5, SIZE - 6, SIZE - 6), outline=(255, 56, 166, 180), width=2)
    draw.rectangle((10, 10, SIZE - 11, SIZE - 11), outline=(54, 237, 220, 126), width=1)
    return img


def variant_hud_scan(item, local, frame_index):
    accent = item["accent"]
    frame = bg_terminal(frame_index, accent)
    draw_title(frame, frame_index)
    draw = ImageDraw.Draw(frame, "RGBA")
    old_icon = base.shadowed_icon(ImageEnhance.Color(item["old"]).enhance(0.45))
    new_icon = base.shadowed_icon(item["new"])
    paste_center(frame, scale_icon(old_icon, 1.02), 68, 149)
    wipe = ease_out(local)
    mask_width = round(new_icon.width * wipe)
    revealed = Image.new("RGBA", new_icon.size, (0, 0, 0, 0))
    revealed.alpha_composite(new_icon.crop((0, 0, mask_width, new_icon.height)), (0, 0))
    paste_center(frame, scale_icon(revealed, 1.08), 202, 149)
    scan_x = 154 + 68 * wipe
    draw.line((scan_x, 84, scan_x - 23, 207), fill=(*accent, 210), width=3)
    draw.line((111, 149, 154, 149), fill=(255, 239, 72, 255), width=4)
    draw.polygon([(164, 149), (149, 138), (149, 160)], fill=(255, 239, 72, 255))
    draw_label(frame, item)
    return frame


def variant_shock_shake(item, local, frame_index):
    accent = item["accent"]
    frame = bg_hull(frame_index, accent)
    draw_title(frame, frame_index)
    draw = ImageDraw.Draw(frame, "RGBA")
    t = ease_out(min(local * 1.35, 1))
    shake = max(0, 1 - local) * sin(local * pi * 18) * 4
    old = base.shadowed_icon(ImageEnhance.Color(item["old"]).enhance(0.35))
    new = base.shadowed_icon(item["new"])
    paste_center(frame, scale_icon(old, 0.9), 54 - 35 * t, 151 + shake)
    paste_center(frame, scale_icon(new, 1.12), 205 + (1 - t) * 82 + shake, 151 - abs(shake))
    if local > 0.72:
        power = (local - 0.72) / 0.28
        for r in (20, 34, 50):
            alpha = round((1 - power) * 90)
            draw.ellipse((205 - r, 151 - r, 205 + r, 151 + r), outline=(*accent, alpha), width=2)
    draw.line((110, 151, 156, 151), fill=(255, 239, 72, 255), width=5)
    draw.polygon([(170, 151), (153, 138), (153, 164)], fill=(255, 239, 72, 255))
    draw_label(frame, item)
    return frame


def variant_rotary_showcase(item, local, frame_index):
    accent = item["accent"]
    frame = bg_abyss(frame_index, accent)
    draw_title(frame, frame_index)
    draw = ImageDraw.Draw(frame, "RGBA")
    spin = local * 360
    old = base.shadowed_icon(item["old"]).rotate(-spin * 0.35, resample=Image.Resampling.BICUBIC, expand=True)
    new = base.shadowed_icon(item["new"]).rotate(sin(local * pi) * 10, resample=Image.Resampling.BICUBIC, expand=True)
    old_alpha = old.getchannel("A").point(lambda a: round(a * (1 - local) * 0.7))
    old.putalpha(old_alpha)
    paste_center(frame, scale_icon(old, 1.2 - local * 0.35), 134 - 46 * local, 149)
    paste_center(frame, scale_icon(new, 0.7 + ease_out(local) * 0.55), 134 + 50 * ease_in_out(local), 149)
    for n in range(3):
        phase = (local + n / 3) % 1
        r = 34 + phase * 52
        draw.arc((134 - r, 149 - r, 134 + r, 149 + r), 210, 330, fill=(*accent, round((1 - phase) * 100)), width=2)
    draw_label(frame, item)
    return frame


def variant_big_modern(item, local, frame_index):
    accent = item["accent"]
    frame = bg_modern(frame_index, accent)
    draw_title(frame, frame_index)
    draw = ImageDraw.Draw(frame, "RGBA")
    old = base.shadowed_icon(ImageEnhance.Color(item["old"]).enhance(0.2))
    new = base.shadowed_icon(item["new"])
    t = ease_out(local)
    paste_center(frame, scale_icon(old, 0.82), 45, 150)
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow, "RGBA")
    gdraw.ellipse((151, 96, 251, 196), fill=(*accent, 42))
    frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    paste_center(frame, scale_icon(new, 0.85 + 0.35 * sin(t * pi / 2)), 202, 149)
    draw.rounded_rectangle((83, 116, 154, 183), radius=5, outline=(255, 238, 75, 205), width=2)
    draw.line((96, 149, 145, 149), fill=(255, 238, 75, 255), width=5)
    draw.polygon([(160, 149), (143, 136), (143, 162)], fill=(255, 238, 75, 255))
    draw_label(frame, item)
    return frame


def variant_warning_flash(item, local, frame_index):
    accent = item["accent"]
    frame = bg_hull(frame_index, accent)
    draw_title(frame, frame_index)
    draw = ImageDraw.Draw(frame, "RGBA")
    flash = 1 if int(local * 18) % 5 == 0 and local < 0.72 else 0
    for y in range(74, 206, 24):
        draw.line((0, y, SIZE, y + 36), fill=(255, 236, 72, 28 + flash * 34), width=8)
        draw.line((0, y + 8, SIZE, y + 44), fill=(255, 48, 153, 20 + flash * 28), width=4)
    old = base.shadowed_icon(ImageEnhance.Color(item["old"]).enhance(0.28))
    new = base.shadowed_icon(item["new"])
    split = 0.5 + sin(local * pi * 3) * 0.02
    old_alpha = old.getchannel("A").point(lambda a: round(a * max(0, 1 - local * 1.25)))
    old.putalpha(old_alpha)
    paste_center(frame, scale_icon(old, 1.05), 74, 149)
    paste_center(frame, scale_icon(new, 0.95 + 0.12 * flash), 200 + sin(local * pi * 10) * 2 * (1 - local), 149)
    draw.rectangle((126, 80, 142, 205), fill=(255, 236, 72, 230))
    draw.rectangle((132, 80, 137, 205), fill=(255, 48, 153, 230))
    draw.line((96, 149, 157, 149), fill=(255, 236, 72, 255), width=5)
    draw.polygon([(172, 149), (153, 136), (153, 162)], fill=(255, 236, 72, 255))
    draw_label(frame, item)
    return frame


def variant_medkit_pop(item, local, frame_index):
    accent = item["accent"]
    frame = bg_terminal(frame_index, accent)
    draw_title(frame, frame_index)
    draw = ImageDraw.Draw(frame, "RGBA")
    t = ease_out(local)
    draw.rounded_rectangle((42, 105, 226, 188), radius=8, fill=(12, 12, 22, 218), outline=(*accent, 180), width=2)
    draw.rounded_rectangle((94, 84, 174, 112), radius=6, outline=(255, 236, 72, 170), width=2)
    draw.rounded_rectangle((122, 119, 146, 172), radius=2, fill=(255, 56, 86, 210))
    draw.rounded_rectangle((99, 134, 169, 156), radius=2, fill=(255, 56, 86, 210))
    old = base.shadowed_icon(ImageEnhance.Color(item["old"]).enhance(0.35))
    new = base.shadowed_icon(item["new"])
    paste_center(frame, scale_icon(old, 0.62), 70, 150)
    pop_y = 149 - sin(t * pi) * 24
    paste_center(frame, scale_icon(new, 0.58 + t * 0.58), 197, pop_y)
    draw.line((99, 150, 151, 150), fill=(255, 236, 72, 255), width=4)
    draw.polygon([(164, 150), (148, 139), (148, 161)], fill=(255, 236, 72, 255))
    draw_label(frame, item)
    return frame


VARIANTS = [
    ("01_baro_hud_scan", "Barotrauma HUD scan/reveal", variant_hud_scan),
    ("02_neon_shock_shake", "Fast impact with landing shake", variant_shock_shake),
    ("03_rotary_showcase", "Rotary old-to-new showcase", variant_rotary_showcase),
    ("04_big_modern", "Modern big-icon workshop read", variant_big_modern),
    ("05_warning_flash", "Hazard flash and glitch energy", variant_warning_flash),
    ("06_medkit_pop", "Medkit pop-out reveal", variant_medkit_pop),
]


def render_variant(items, renderer):
    frames = []
    frames_per_item = 32
    total = frames_per_item * len(items)
    for i in range(total):
        item = items[(i // frames_per_item) % len(items)]
        local = (i % frames_per_item) / (frames_per_item - 1)
        frames.append(renderer(item, local, i).convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def save_gif(frames, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )


def save_comparison(posters):
    cell_w = 178
    cell_h = 206
    cols = 3
    rows = (len(posters) + cols - 1) // cols
    sheet = Image.new("RGBA", (cell_w * cols, cell_h * rows), (7, 6, 16, 255))
    draw = ImageDraw.Draw(sheet, "RGBA")
    for index, (name, label, poster) in enumerate(posters):
        x = (index % cols) * cell_w
        y = (index // cols) * cell_h
        sheet.alpha_composite(poster.resize((cell_w, cell_w), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 8, y + cell_w + 7), name.replace("_", " ").upper(), font=SHEET_FONT, fill=(255, 242, 78, 255))
    sheet.save(OUT_DIR / "medical_icons_logo_creative_comparison.png")


def main():
    args = parse_args()
    for name, label, _renderer in VARIANTS:
        print(OUT_DIR / f"medical_icons_logo_{name}.gif")
        print(OUT_DIR / f"medical_icons_logo_{name}.png")
    if args.dry_run:
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = base.load_item_art()
    posters = []
    for name, label, renderer in VARIANTS:
        frames = render_variant(items, renderer)
        gif_path = OUT_DIR / f"medical_icons_logo_{name}.gif"
        poster_path = OUT_DIR / f"medical_icons_logo_{name}.png"
        save_gif(frames, gif_path)
        poster = frames[8].convert("RGBA")
        poster.save(poster_path)
        posters.append((name, label, poster))
        print(gif_path.relative_to(PROJECT_ROOT))
        print(poster_path.relative_to(PROJECT_ROOT))
    save_comparison(posters)
    print((OUT_DIR / "medical_icons_logo_creative_comparison.png").relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
