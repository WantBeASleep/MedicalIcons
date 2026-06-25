from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import math
import sys


SCRIPT_DIR = Path(__file__).resolve().parent


def find_project_root() -> Path:
    for path in [SCRIPT_DIR, *SCRIPT_DIR.parents]:
        if (path / "filelist.xml").exists():
            return path
    raise FileNotFoundError("Could not find project root marker filelist.xml")


PROJECT_ROOT = find_project_root()
VENDOR_DIR = PROJECT_ROOT / "_vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


SIZE = (268, 268)
FONT_DIR = PROJECT_ROOT / "source" / "fonts"
OUTPUT_DIR = PROJECT_ROOT / "preview" / "creative_gif_variants"
BAROTRAUMA_ROOT = PROJECT_ROOT.parents[1]
CONTENT_DIR = BAROTRAUMA_ROOT / "Content"


@dataclass(frozen=True)
class ItemSpec:
    key: str
    label: str
    old_texture: Path
    old_rect: tuple[int, int, int, int]
    new_icon: Path


@dataclass(frozen=True)
class VariantSpec:
    key: str
    label: str
    bg: tuple[int, int, int]
    accent: tuple[int, int, int]
    accent2: tuple[int, int, int]
    text: tuple[int, int, int]
    motion: str
    title_size: int = 33
    label_size: int = 30
    bg_style: str = ""


ITEMS = [
    ItemSpec(
        "morphine",
        "MORPHINE",
        CONTENT_DIR / "Items" / "InventoryIconAtlas.png",
        (256, 448, 64, 64),
        PROJECT_ROOT / "source" / "textures" / "insulin_syringe" / "items" / "antidama1" / "icon.png",
    ),
    ItemSpec(
        "adrenaline",
        "ADRENALINE",
        CONTENT_DIR / "Items" / "InventoryIconAtlas2.png",
        (129, 448, 62, 64),
        PROJECT_ROOT / "source" / "textures" / "ampoule" / "items" / "adrenaline" / "icon.png",
    ),
    ItemSpec(
        "cyanide",
        "CYANIDE",
        CONTENT_DIR / "Items" / "InventoryIconAtlas.png",
        (192, 640, 64, 64),
        PROJECT_ROOT / "source" / "textures" / "dart_syringe" / "items" / "cyanide" / "icon.png",
    ),
    ItemSpec(
        "calyxanide",
        "CALYXANIDE",
        CONTENT_DIR / "Items" / "InventoryIconAtlas.png",
        (897, 449, 63, 63),
        PROJECT_ROOT / "source" / "textures" / "vial" / "items" / "calyxanide" / "icon.png",
    ),
    ItemSpec(
        "meth",
        "METH",
        CONTENT_DIR / "Items" / "InventoryIconAtlas.png",
        (512, 448, 64, 64),
        PROJECT_ROOT / "source" / "textures" / "pocket_injector" / "items" / "meth" / "icon.png",
    ),
]


VARIANTS = [
    VariantSpec("01_barotrauma_sonar", "Barotrauma Sonar", (8, 18, 20), (78, 185, 160), (180, 230, 210), (229, 246, 239), "sonar"),
    VariantSpec("02_neon_snap", "Neon Snap", (17, 12, 28), (42, 230, 235), (255, 68, 150), (245, 250, 255), "snap"),
    VariantSpec("03_comic_shake", "Comic Shake", (24, 20, 15), (255, 202, 64), (236, 66, 62), (255, 241, 196), "shake", 32, 31),
    VariantSpec("04_lab_carousel", "Lab Carousel", (12, 21, 27), (139, 198, 255), (148, 233, 124), (232, 244, 255), "carousel"),
    VariantSpec("05_toxic_glitch", "Toxic Glitch", (9, 15, 11), (166, 255, 74), (255, 54, 54), (235, 255, 208), "glitch"),
    VariantSpec("06_clean_shop", "Clean Workshop", (21, 25, 30), (255, 122, 72), (102, 214, 190), (248, 249, 241), "clean", 31, 29),
    VariantSpec("07_v2_medbay_panel", "V2 Medbay Panel", (9, 16, 20), (54, 218, 224), (255, 124, 59), (242, 252, 253), "snap", bg_style="medbay_panel"),
    VariantSpec("08_v2_emergency_red", "V2 Emergency Red", (22, 9, 10), (255, 84, 66), (255, 205, 72), (255, 245, 222), "snap", bg_style="emergency_red"),
    VariantSpec("09_v2_inventory_slots", "V2 Inventory Slots", (16, 18, 22), (92, 226, 210), (255, 154, 92), (245, 250, 247), "snap", bg_style="inventory_slots"),
    VariantSpec("10_v2_abyss_bio", "V2 Abyss Bio", (6, 18, 24), (60, 229, 185), (130, 105, 255), (230, 255, 242), "snap", bg_style="abyss_bio"),
    VariantSpec("11_v2_xray_lab", "V2 X-Ray Lab", (12, 22, 32), (104, 207, 255), (158, 255, 196), (233, 249, 255), "snap", bg_style="xray_lab"),
    VariantSpec("12_v2_pop_halftone", "V2 Pop Halftone", (24, 13, 35), (44, 236, 238), (255, 64, 157), (253, 249, 255), "snap", bg_style="pop_halftone"),
    VariantSpec("13_v2_sonar_snap", "V2 Sonar Snap", (8, 18, 20), (42, 230, 235), (255, 68, 150), (229, 246, 239), "snap", bg_style="sonar_grid"),
]


def parse_args():
    parser = ArgumentParser(
        description="Build creative 268x268 animated GIF preview variants for the Medical Icons mod."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for generated GIFs and the contact sheet. Defaults to preview/creative_gif_variants.",
    )
    parser.add_argument(
        "--frames-per-item",
        type=int,
        default=14,
        help="Animation frames to render for each item before switching to the next item.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=52,
        help="GIF frame duration in milliseconds.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned output files without writing images.",
    )
    return parser.parse_args()


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_DIR / "Bangers-Regular.ttf"
    if path.exists():
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_font(text: str, max_width: int, start_size: int) -> ImageFont.ImageFont:
    size = start_size
    while size > 12:
        font = load_font(size)
        box = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font, stroke_width=2)
        if box[2] - box[0] <= max_width:
            return font
        size -= 1
    return load_font(size)


def ease_out_back(x: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)


def ease_in_out(x: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * x)


def crop_icon(texture: Path, rect: tuple[int, int, int, int]) -> Image.Image:
    x, y, width, height = rect
    icon = Image.open(texture).convert("RGBA").crop((x, y, x + width, y + height))
    return ImageOps.contain(icon, (64, 64), Image.Resampling.LANCZOS)


def load_icons() -> dict[str, tuple[Image.Image, Image.Image]]:
    icons = {}
    for item in ITEMS:
        if not item.old_texture.exists():
            raise FileNotFoundError(item.old_texture)
        if not item.new_icon.exists():
            raise FileNotFoundError(item.new_icon)
        old_icon = crop_icon(item.old_texture, item.old_rect)
        new_icon = Image.open(item.new_icon).convert("RGBA")
        icons[item.key] = (old_icon, ImageOps.contain(new_icon, (64, 64), Image.Resampling.LANCZOS))
    return icons


def tint_icon(icon: Image.Image, color: tuple[int, int, int], amount: float) -> Image.Image:
    gray = ImageOps.grayscale(icon)
    tinted = ImageOps.colorize(gray, black=(20, 20, 20), white=color).convert("RGBA")
    tinted.putalpha(icon.getchannel("A"))
    return Image.blend(icon, tinted, amount)


def transformed_icon(icon: Image.Image, scale: float, angle: float, alpha: float = 1.0) -> Image.Image:
    size = max(1, int(64 * scale))
    image = icon.resize((size, size), Image.Resampling.LANCZOS)
    image = image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    if alpha < 1.0:
        image.putalpha(image.getchannel("A").point(lambda value: int(value * alpha)))
    return image


def paste_center(base: Image.Image, icon: Image.Image, center: tuple[float, float]):
    x = int(center[0] - icon.width / 2)
    y = int(center[1] - icon.height / 2)
    shadow = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    shadow.putalpha(icon.getchannel("A").filter(ImageFilter.GaussianBlur(5)))
    base.alpha_composite(shadow, (x + 4, y + 6))
    base.alpha_composite(icon, (x, y))


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    stroke: tuple[int, int, int] = (2, 5, 7),
    stroke_width: int = 2,
):
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = xy[0] - (box[2] - box[0]) / 2
    y = xy[1] - (box[3] - box[1]) / 2 - box[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke)


def background(variant: VariantSpec, frame_index: int) -> Image.Image:
    width, height = SIZE
    image = Image.new("RGBA", SIZE, (*variant.bg, 255))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        blend = y / height
        r = int(variant.bg[0] * (1 - blend) + max(0, variant.accent[0] - 80) * blend)
        g = int(variant.bg[1] * (1 - blend) + max(0, variant.accent[1] - 80) * blend)
        b = int(variant.bg[2] * (1 - blend) + max(0, variant.accent[2] - 80) * blend)
        draw.line((0, y, width, y), fill=(r, g, b, 255))

    if variant.bg_style == "sonar_grid":
        for radius in range(40, 210, 42):
            pulse = (radius + frame_index * 5) % 190
            alpha = max(0, 110 - pulse // 2)
            draw.ellipse((134 - pulse, 130 - pulse, 134 + pulse, 130 + pulse), outline=(*variant.accent, alpha), width=2)
        for y in range(8, height, 8):
            draw.line((0, y, width, y), fill=(255, 255, 255, 12))
        sweep = math.radians((frame_index * 14) % 360)
        draw.line((134, 130, 134 + math.cos(sweep) * 130, 130 + math.sin(sweep) * 130), fill=(*variant.accent2, 64), width=2)
    elif variant.bg_style == "medbay_panel":
        for x in range(0, width, 32):
            shade = 26 + (x // 32 % 2) * 8
            draw.rectangle((x, 0, x + 31, height), fill=(shade, shade + 8, shade + 12, 68))
        for y in range(46, height, 34):
            draw.line((0, y, width, y), fill=(*variant.accent, 30), width=1)
        draw.rounded_rectangle((16, 84, 252, 184), radius=8, fill=(0, 0, 0, 58), outline=(*variant.accent, 65), width=2)
        for x in (25, 243):
            for y in (94, 174):
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*variant.accent2, 130))
        draw.rectangle((0, 48, width, 54), fill=(*variant.accent2, 70))
    elif variant.bg_style == "emergency_red":
        offset = (frame_index * 6) % 42
        for x in range(-80, width + 80, 42):
            draw.polygon(
                [(x + offset, 0), (x + 18 + offset, 0), (x - 56 + offset, height), (x - 74 + offset, height)],
                fill=(*variant.accent2, 65),
            )
        draw.rectangle((0, 83, width, 189), fill=(0, 0, 0, 72))
        for y in (86, 186):
            draw.line((0, y, width, y), fill=(*variant.accent, 170), width=3)
        alarm = 30 + int(abs(math.sin(frame_index * 0.7)) * 55)
        draw.rectangle((0, 0, width, height), outline=(*variant.accent, alarm), width=8)
    elif variant.bg_style == "inventory_slots":
        draw.rectangle((0, 0, width, height), fill=(18, 22, 27, 235))
        for row in range(4):
            for col in range(4):
                x = 14 + col * 61
                y = 54 + row * 42
                fill = (30, 36, 42, 150) if (row + col) % 2 else (25, 30, 36, 150)
                draw.rounded_rectangle((x, y, x + 48, y + 32), radius=4, fill=fill, outline=(118, 135, 143, 70))
        draw.rounded_rectangle((13, 83, 120, 186), radius=8, fill=(0, 0, 0, 92), outline=(150, 150, 150, 70))
        draw.rounded_rectangle((148, 83, 255, 186), radius=8, fill=(*variant.accent, 34), outline=(*variant.accent, 130))
    elif variant.bg_style == "abyss_bio":
        for i in range(18):
            x = (i * 37 + frame_index * (2 + i % 3)) % (width + 30) - 15
            y = 62 + ((i * 29 + frame_index * 3) % 150)
            radius = 2 + i % 4
            color = variant.accent if i % 2 else variant.accent2
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 42 + i % 5 * 14))
        for radius in (62, 102, 146):
            wobble = math.sin(frame_index * 0.45 + radius) * 5
            draw.arc((134 - radius, 130 - radius + wobble, 134 + radius, 130 + radius + wobble), 190, 350, fill=(*variant.accent, 44), width=2)
        draw.rectangle((0, 0, width, height), fill=(0, 15, 18, 28))
    elif variant.bg_style == "xray_lab":
        for x in range(0, width, 18):
            draw.line((x, 52, x, 206), fill=(*variant.accent, 18), width=1)
        for y in range(56, 206, 18):
            draw.line((0, y, width, y), fill=(*variant.accent2, 16), width=1)
        sweep = (frame_index * 9) % (width + 70) - 35
        draw.rectangle((sweep, 52, sweep + 20, 210), fill=(*variant.accent, 54))
        draw.ellipse((35, 82, 233, 192), outline=(*variant.accent2, 58), width=2)
        draw.ellipse((72, 102, 196, 174), outline=(*variant.accent, 66), width=2)
    elif variant.bg_style == "pop_halftone":
        offset = frame_index % 10
        for y in range(56, 212, 12):
            for x in range(0, width, 12):
                radius = 2 + ((x + y + offset) // 12) % 3
                color = variant.accent if (x // 12 + y // 12) % 2 else variant.accent2
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 42))
        draw.polygon([(0, 72), (268, 44), (268, 96), (0, 124)], fill=(*variant.accent, 35))
        draw.polygon([(0, 183), (268, 144), (268, 198), (0, 230)], fill=(*variant.accent2, 36))
    elif variant.motion == "sonar":
        for radius in range(40, 210, 42):
            pulse = (radius + frame_index * 5) % 190
            alpha = max(0, 110 - pulse // 2)
            draw.ellipse((134 - pulse, 130 - pulse, 134 + pulse, 130 + pulse), outline=(*variant.accent, alpha), width=2)
        for y in range(8, height, 8):
            draw.line((0, y, width, y), fill=(255, 255, 255, 12))
    elif variant.motion in {"snap", "glitch"}:
        offset = (frame_index * 7) % width
        for x in range(-width, width * 2, 34):
            draw.line((x + offset, 0, x - 80 + offset, height), fill=(*variant.accent, 42), width=3)
        if variant.motion == "glitch":
            for y in range(46, height, 35):
                draw.rectangle((0, y + frame_index % 6, width, y + 4 + frame_index % 6), fill=(*variant.accent2, 48))
    elif variant.motion == "shake":
        for x in range(-40, width + 40, 22):
            draw.polygon([(x, 0), (x + 11, 0), (x - 48, height), (x - 59, height)], fill=(*variant.accent, 18))
    elif variant.motion == "carousel":
        for i in range(9):
            x = (i * 37 + frame_index * 3) % (width + 40) - 20
            y = 74 + int(math.sin((frame_index + i) * 0.55) * 8)
            draw.rounded_rectangle((x, y, x + 18, y + 82), radius=6, fill=(*variant.accent2, 30))
    else:
        draw.rectangle((0, 0, width // 2 - 2, height), fill=(30, 34, 38, 230))
        draw.rectangle((width // 2 + 2, 0, width, height), fill=(22, 42, 39, 230))
        draw.line((width // 2, 58, width // 2, 212), fill=(*variant.accent, 130), width=2)
    return image.filter(ImageFilter.GaussianBlur(0.15))


def draw_badges(draw: ImageDraw.ImageDraw, variant: VariantSpec):
    font = load_font(16)
    draw.rounded_rectangle((33, 59, 111, 79), radius=5, fill=(0, 0, 0, 150), outline=(150, 150, 150, 80))
    draw.rounded_rectangle((157, 59, 235, 79), radius=5, fill=(*variant.accent, 70), outline=(*variant.accent, 150))
    draw_centered_text(draw, (72, 67), "OLD", font, (205, 213, 209), stroke_width=1)
    draw_centered_text(draw, (196, 67), "NEW", font, variant.text, stroke=variant.accent, stroke_width=1)


def render_frame(variant: VariantSpec, item: ItemSpec, icons: dict[str, tuple[Image.Image, Image.Image]], frame: int, frames_per_item: int) -> Image.Image:
    progress = frame / max(1, frames_per_item - 1)
    pulse = math.sin(progress * math.tau)
    image = background(variant, frame)
    draw = ImageDraw.Draw(image)

    title_font = fit_font("MEDICAL ICONS", 244, variant.title_size)
    label_font = fit_font(item.label, 242, variant.label_size)
    draw_centered_text(draw, (134, 24), "MEDICAL ICONS", title_font, variant.text, stroke=(0, 0, 0), stroke_width=3)
    draw_badges(draw, variant)

    old_icon, new_icon = icons[item.key]
    old_icon = tint_icon(old_icon, (168, 180, 178), 0.34)

    left = [72.0, 134.0]
    right = [196.0, 134.0]
    old_scale = 1.32
    new_scale = 1.28
    old_angle = -8
    new_angle = 8
    old_alpha = 0.82
    new_alpha = 1.0

    if variant.motion == "sonar":
        pop = ease_out_back(min(1.0, progress * 1.25))
        new_scale = 0.95 + pop * 0.47 + pulse * 0.03
        old_scale = 1.26 + abs(pulse) * 0.04
        draw.line((106, 134, 160, 134), fill=(*variant.accent, 170), width=3)
        draw.polygon([(160, 134), (148, 126), (148, 142)], fill=(*variant.accent, 185))
    elif variant.motion == "snap":
        snap = ease_out_back(progress)
        left[0] = 46 + snap * 26
        right[0] = 230 - snap * 34
        new_angle = -18 + snap * 28
        new_scale = 0.8 + snap * 0.58
        old_scale = 1.28 + abs(pulse) * 0.04
        old_alpha = 0.55 + 0.28 * (1 - progress)
        for shift, color in [(-4, variant.accent2), (4, variant.accent)]:
            icon = transformed_icon(new_icon, new_scale, new_angle, 0.42)
            paste_center(image, tint_icon(icon, color, 0.65), (right[0] + shift, right[1]))
    elif variant.motion == "shake":
        jitter = math.sin(frame * 2.6) * 4
        left[0] += jitter
        right[0] -= jitter
        left[1] += math.cos(frame * 3.1) * 3
        right[1] -= math.cos(frame * 3.1) * 3
        old_angle = -18 + jitter
        new_angle = 18 - jitter
        new_scale = 1.35 + abs(pulse) * 0.1
        draw.polygon([(119, 102), (149, 116), (130, 129), (154, 146), (114, 137), (132, 122)], fill=(*variant.accent, 190))
    elif variant.motion == "carousel":
        orbit = math.sin(progress * math.tau)
        left[1] += orbit * 10
        right[1] -= orbit * 10
        old_scale = 1.05 - orbit * 0.05
        new_scale = 1.25 + orbit * 0.1
        old_angle = progress * -28
        new_angle = progress * 28
        draw.arc((102, 84, 166, 180), start=int(progress * 360), end=int(progress * 360 + 250), fill=(*variant.accent, 150), width=3)
    elif variant.motion == "glitch":
        glitch = -1 if frame % 4 < 2 else 1
        left[0] += glitch * 2
        right[0] -= glitch * 3
        old_alpha = 0.65
        new_scale = 1.28 + (0.16 if frame % 7 == 0 else 0)
        new_angle = 4 + glitch * 7
        draw.rectangle((115, 105 + frame % 8, 153, 112 + frame % 8), fill=(*variant.accent2, 120))
        draw.rectangle((122, 156 - frame % 6, 160, 162 - frame % 6), fill=(*variant.accent, 110))
    else:
        settle = ease_in_out(progress)
        old_scale = 1.26 - settle * 0.04
        new_scale = 1.12 + settle * 0.22
        draw.rounded_rectangle((18, 88, 120, 184), radius=8, fill=(0, 0, 0, 82), outline=(255, 255, 255, 42))
        draw.rounded_rectangle((148, 88, 250, 184), radius=8, fill=(*variant.accent2, 34), outline=(*variant.accent2, 120))

    paste_center(image, transformed_icon(old_icon, old_scale, old_angle, old_alpha), tuple(left))
    paste_center(image, transformed_icon(new_icon, new_scale, new_angle, new_alpha), tuple(right))

    if variant.motion in {"sonar", "clean"}:
        draw.rounded_rectangle((9, 216, 259, 262), radius=8, fill=(0, 0, 0, 128), outline=(*variant.accent, 90), width=1)
    draw_centered_text(draw, (134, 237), item.label, label_font, variant.text, stroke=(0, 0, 0), stroke_width=3)

    return image.convert("P", palette=Image.Palette.ADAPTIVE)


def build_gif(variant: VariantSpec, icons: dict[str, tuple[Image.Image, Image.Image]], frames_per_item: int) -> list[Image.Image]:
    frames = []
    for item in ITEMS:
        for frame in range(frames_per_item):
            frames.append(render_frame(variant, item, icons, frame, frames_per_item))
    return frames


def build_contact_sheet(output_dir: Path, icons: dict[str, tuple[Image.Image, Image.Image]], frames_per_item: int):
    columns = 3
    rows = math.ceil(len(VARIANTS) / columns)
    sheet = Image.new("RGB", (columns * SIZE[0], rows * SIZE[1]), (8, 10, 12))
    for index, variant in enumerate(VARIANTS):
        frame = render_frame(variant, ITEMS[index % len(ITEMS)], icons, frames_per_item // 2, frames_per_item).convert("RGB")
        x = index % columns * SIZE[0]
        y = index // columns * SIZE[1]
        sheet.paste(frame, (x, y))
    sheet.save(output_dir / "contact_sheet.png")


def validate_inputs():
    missing = []
    for item in ITEMS:
        if not item.old_texture.exists():
            missing.append(item.old_texture)
        if not item.new_icon.exists():
            missing.append(item.new_icon)
    if missing:
        missing_text = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing preview source files:\n{missing_text}")


def main():
    args = parse_args()
    validate_inputs()
    planned = [args.output_dir / f"{variant.key}.gif" for variant in VARIANTS]
    planned.append(args.output_dir / "contact_sheet.png")
    if args.dry_run:
        print("Would write:")
        for path in planned:
            print(f"- {path}")
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    icons = load_icons()
    for variant in VARIANTS:
        frames = build_gif(variant, icons, args.frames_per_item)
        output = args.output_dir / f"{variant.key}.gif"
        frames[0].save(
            output,
            save_all=True,
            append_images=frames[1:],
            duration=args.duration,
            loop=0,
            optimize=True,
            disposal=2,
        )
        print(f"Wrote {output}")
    build_contact_sheet(args.output_dir, icons, args.frames_per_item)
    print(f"Wrote {args.output_dir / 'contact_sheet.png'}")


if __name__ == "__main__":
    main()
