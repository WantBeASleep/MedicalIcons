from argparse import ArgumentParser
from math import pi, sin
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


SIZE = 268
FRAME_MS = 30
SCRIPT_DIR = Path(__file__).resolve().parent
BACKGROUND_STYLES = ("medical", "hull", "abyss")

ITEMS = [
    {
        "id": "antidama1",
        "label": "MORPHINE",
        "new_icon": "insulin_syringe/items/antidama1/icon.png",
        "xml": "Content/Items/Medical/medical.xml",
        "accent": (255, 58, 66),
    },
    {
        "id": "adrenaline",
        "label": "ADRENALINE",
        "new_icon": "ampoule/items/adrenaline/icon.png",
        "xml": "Content/Items/Medical/medical.xml",
        "accent": (93, 221, 255),
    },
    {
        "id": "cyanide",
        "label": "CYANIDE",
        "new_icon": "dart_syringe/items/cyanide/icon.png",
        "xml": "Content/Items/Medical/poisons.xml",
        "accent": (28, 184, 214),
    },
    {
        "id": "calyxanide",
        "label": "CALYXANIDE",
        "new_icon": "vial/items/calyxanide/icon.png",
        "xml": "Content/Items/Medical/medical.xml",
        "accent": (185, 190, 194),
    },
    {
        "id": "meth",
        "label": "METH",
        "new_icon": "pocket_injector/items/meth/icon.png",
        "xml": "Content/Items/Medical/buffs.xml",
        "accent": (211, 54, 137),
    },
]


def find_project_root() -> Path:
    for path in [SCRIPT_DIR, *SCRIPT_DIR.parents]:
        if (path / "filelist.xml").exists():
            return path
    raise RuntimeError("Could not find project root marker filelist.xml")


PROJECT_ROOT = find_project_root()
GAME_ROOT = PROJECT_ROOT.parents[1]


def parse_args():
    parser = ArgumentParser(description="Build the 268x268 animated GIF logo for Medical Icons.")
    parser.add_argument(
        "--output",
        default="preview/medical_icons_logo.gif",
        help="Output GIF path, relative to the project root unless absolute.",
    )
    parser.add_argument(
        "--poster",
        default="preview/medical_icons_logo_poster.png",
        help="Poster PNG path for quick inspection. Use an empty value to skip.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned output paths without writing.")
    parser.add_argument(
        "--background-style",
        choices=BACKGROUND_STYLES,
        default="medical",
        help="Background treatment to use for the main GIF.",
    )
    parser.add_argument(
        "--variant-posters",
        default="preview/medical_icons_logo_background_variants.png",
        help="Contact sheet with poster frames for all background variants. Use an empty value to skip.",
    )
    parser.add_argument(
        "--font-file",
        default="",
        help="Display font file under source/fonts, for example fight.ttf or Bangers-Regular.ttf.",
    )
    return parser.parse_args()


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def parse_rect(value: str) -> tuple[int, int, int, int]:
    parts = [int(float(part.strip())) for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Invalid sourcerect: {value}")
    return tuple(parts)


def content_path(texture: str, xml_path: Path) -> Path:
    normalized = texture.replace("\\", "/")
    if normalized.startswith("Content/"):
        return GAME_ROOT / normalized
    return xml_path.parent / normalized


def vanilla_icon(item: dict) -> Image.Image:
    xml_path = GAME_ROOT / item["xml"]
    root = ET.parse(xml_path).getroot()
    for element in root.iter():
        if element.attrib.get("identifier") == item["id"]:
            icon = element.find("InventoryIcon")
            if icon is None:
                continue
            texture = Image.open(content_path(icon.attrib["texture"], xml_path)).convert("RGBA")
            x, y, w, h = parse_rect(icon.attrib["sourcerect"])
            return texture.crop((x, y, x + w, y + h))
    raise RuntimeError(f"Could not find vanilla InventoryIcon for {item['id']}")


def trim_alpha(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    return image.crop(bbox) if bbox else image


def fit_icon(image: Image.Image, size: int) -> Image.Image:
    image = trim_alpha(image)
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return out


def load_item_art():
    loaded = []
    for item in ITEMS:
        old_icon = fit_icon(vanilla_icon(item), 74)
        new_icon = fit_icon(Image.open(PROJECT_ROOT / "source" / "textures" / item["new_icon"]).convert("RGBA"), 82)
        loaded.append({**item, "old": old_icon, "new": new_icon})
    return loaded


def font(name: str, size: int, preferred_file: str = "") -> ImageFont.FreeTypeFont:
    fonts = PROJECT_ROOT / "source" / "fonts"
    preferred = [fonts / preferred_file] if preferred_file else []
    candidates = {
        "display": [
            fonts / "Bangers-Regular.ttf",
            fonts / "fight.ttf",
            fonts / "fightthis.ttf",
            fonts / "hotline_miami.ttf",
            fonts / "pricedow.ttf",
            fonts / "pricedown.ttf",
            fonts / "bangers.ttf",
            fonts / "bahnschrift.ttf",
            fonts / "arialbd.ttf",
        ],
        "bold": [fonts / "bahnschrift.ttf", fonts / "arialbd.ttf"],
        "regular": [fonts / "segoeui.ttf", fonts / "arial.ttf"],
    }[name]
    for path in [*preferred, *candidates]:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


TITLE_FONT_WIDE = font("display", 25)
LABEL_FONT = font("display", 17)


def add_glow_text(draw: ImageDraw.ImageDraw, xy, text: str, main, glow, font_obj, anchor="mm", stroke=2):
    x, y = xy
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        draw.text((x + dx, y + dy), text, fill=glow, font=font_obj, anchor=anchor, stroke_width=stroke)
    draw.text((x, y), text, fill=main, font=font_obj, anchor=anchor, stroke_width=1, stroke_fill=(18, 0, 31, 255))


def glow_text_image(text: str, font_obj, main, glow, max_width: int, stroke=2) -> Image.Image:
    temp = Image.new("RGBA", (max_width * 2, 58), (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp, "RGBA")
    bbox = draw.textbbox((0, 0), text, font=font_obj, stroke_width=stroke)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    layer = Image.new("RGBA", (width + 14, height + 14), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer, "RGBA")
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        ldraw.text((7 - bbox[0] + dx, 7 - bbox[1] + dy), text, fill=glow, font=font_obj, stroke_width=stroke)
    ldraw.text(
        (7 - bbox[0], 7 - bbox[1]),
        text,
        fill=main,
        font=font_obj,
        stroke_width=1,
        stroke_fill=(18, 0, 31, 255),
    )
    if layer.width > max_width:
        target = (max_width, max(1, round(layer.height * max_width / layer.width)))
        layer = layer.resize(target, Image.Resampling.LANCZOS)
    return layer


def crop_texture(path: Path, size: tuple[int, int], offset=(0, 0), tint=(0, 0, 0), alpha=255) -> Image.Image:
    texture = Image.open(path).convert("RGBA")
    scale = max(size[0] / texture.width, size[1] / texture.height)
    texture = texture.resize((round(texture.width * scale), round(texture.height * scale)), Image.Resampling.LANCZOS)
    x = min(max(offset[0], 0), max(texture.width - size[0], 0))
    y = min(max(offset[1], 0), max(texture.height - size[1], 0))
    texture = texture.crop((x, y, x + size[0], y + size[1]))
    texture = ImageEnhance.Contrast(texture).enhance(1.25)
    shade = Image.new("RGBA", size, (*tint, alpha))
    return Image.alpha_composite(texture, shade)


def draw_background(frame_index: int, accent, style: str):
    img = Image.new("RGBA", (SIZE, SIZE), (13, 9, 27, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(SIZE):
        t = y / (SIZE - 1)
        draw.line((0, y, SIZE, y), fill=(int(14 + 25 * t), int(6 + 12 * t), int(34 + 18 * t), 255))

    if style == "medical":
        texture = crop_texture(
            GAME_ROOT / "Content" / "UI" / "Health" / "MedUIExtra.png",
            (SIZE, SIZE),
            offset=(48 + (frame_index % 12), 36),
            tint=(5, 0, 20),
            alpha=128,
        )
    elif style == "hull":
        texture = crop_texture(
            GAME_ROOT / "Content" / "Map" / "SubmarineDeco.png",
            (SIZE, SIZE),
            offset=(0, 115),
            tint=(13, 9, 20),
            alpha=92,
        )
    else:
        texture = crop_texture(
            GAME_ROOT / "Content" / "Map" / "background.png",
            (SIZE, SIZE),
            offset=(80 + frame_index % 10, 30),
            tint=(1, 8, 21),
            alpha=132,
        )
    img = Image.alpha_composite(img, texture)
    draw = ImageDraw.Draw(img, "RGBA")

    left_poly = [(0, 62), (0, SIZE), (102, SIZE), (166, 62)]
    right_poly = [(166, 62), (102, SIZE), (SIZE, SIZE), (SIZE, 62)]
    if style == "hull":
        draw.polygon(left_poly, fill=(7, 13, 22, 176))
        draw.polygon(right_poly, fill=(34, 15, 31, 166))
    elif style == "abyss":
        draw.polygon(left_poly, fill=(5, 15, 31, 186))
        draw.polygon(right_poly, fill=(29, 10, 44, 178))
    else:
        draw.polygon(left_poly, fill=(8, 18, 34, 188))
        draw.polygon(right_poly, fill=(39, 9, 41, 180))
    draw.line((166, 62, 102, SIZE), fill=(255, 241, 84, 255), width=4)
    draw.line((160, 62, 96, SIZE), fill=(255, 55, 158, 220), width=2)

    for n in range(5):
        y = 82 + n * 34
        draw.line((11, y, 82, y + 12), fill=(55, 242, 222, 34), width=1)
        draw.line((186, y + 8, 256, y - 4), fill=(*accent, 28), width=1)

    draw.rectangle((5, 5, SIZE - 6, SIZE - 6), outline=(255, 56, 166, 180), width=2)
    draw.rectangle((10, 10, SIZE - 11, SIZE - 11), outline=(54, 237, 220, 130), width=1)
    return img


def shadowed_icon(icon: Image.Image, shadow_color=(0, 0, 0, 185)):
    alpha = icon.getchannel("A").filter(ImageFilter.GaussianBlur(3))
    shadow = Image.new("RGBA", icon.size, shadow_color)
    shadow.putalpha(alpha)
    out = Image.new("RGBA", (icon.width + 12, icon.height + 12), (0, 0, 0, 0))
    out.alpha_composite(shadow, (8, 8))
    out.alpha_composite(icon, (6, 5))
    return out


def paste_center(base: Image.Image, image: Image.Image, x: float, y: float):
    base.alpha_composite(image, (round(x - image.width / 2), round(y - image.height / 2)))


def draw_arrow(draw: ImageDraw.ImageDraw, center, glow_alpha):
    x, y = center
    draw.line((x - 20, y, x + 17, y), fill=(0, 0, 0, 210), width=8)
    draw.polygon([(x + 26, y), (x + 10, y - 13), (x + 10, y + 13)], fill=(0, 0, 0, 210))
    draw.line((x - 20, y, x + 17, y), fill=(255, 242, 78, 255), width=4)
    draw.polygon([(x + 25, y), (x + 9, y - 11), (x + 9, y + 11)], fill=(255, 242, 78, 255))
    draw.line((x - 22, y + 7, x + 17, y + 7), fill=(255, 50, 164, glow_alpha), width=2)


def title_layer(frame: Image.Image, frame_index: int, title_font):
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    sway = sin(frame_index * 0.16)
    bob = sin(frame_index * 0.22 + 0.8)
    title_angle = sway * 0.65
    title = glow_text_image(
        "QoL - MEDICAL ICONS",
        title_font,
        (255, 242, 78, 255),
        (255, 44, 160, 168),
        246,
        stroke=2,
    )
    title = title.rotate(title_angle, resample=Image.Resampling.BICUBIC, expand=True)
    overlay.alpha_composite(title, (round((SIZE - title.width) / 2 + sway * 1.2), round(14 + bob * 0.7)))
    draw.line((19, 58, 249, 58), fill=(255, 242, 78, 220), width=2)
    frame.alpha_composite(overlay)


def item_positions(local_t: float):
    ease = 1 - (1 - min(local_t, 1)) ** 3
    bounce = sin(local_t * pi) * 5
    old_x = 66 - (1 - ease) * 64
    new_x = 202 + (1 - ease) * 72
    y = 154 - bounce
    return old_x, y, new_x, y


def render_frames(items, background_style: str, title_font=TITLE_FONT_WIDE, label_font=LABEL_FONT):
    frames = []
    frames_per_item = 32
    total = frames_per_item * len(items)
    for i in range(total):
        item = items[(i // frames_per_item) % len(items)]
        local = (i % frames_per_item) / (frames_per_item - 1)
        accent = item["accent"]
        frame = draw_background(i, accent, background_style)
        draw = ImageDraw.Draw(frame, "RGBA")
        title_layer(frame, i, title_font)

        old_x, old_y, new_x, new_y = item_positions(local)
        old_icon = shadowed_icon(ImageEnhance.Color(item["old"]).enhance(0.65))
        new_icon = shadowed_icon(item["new"])
        old_icon.putalpha(ImageEnhance.Brightness(old_icon.getchannel("A")).enhance(0.75))
        paste_center(frame, old_icon, old_x, old_y)
        paste_center(frame, new_icon, new_x, new_y)

        glow_alpha = int(125 + 100 * sin(local * pi))
        draw_arrow(draw, (134, 155), glow_alpha)
        draw.rounded_rectangle((21, 218, 247, 249), radius=4, fill=(8, 7, 22, 226), outline=(*accent, 210), width=2)
        add_glow_text(draw, (134, 234), item["label"], (*accent, 255), (*accent, 168), label_font, stroke=2)

        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128))
    return frames


def save_variant_posters(items, path: Path, title_font=TITLE_FONT_WIDE, label_font=LABEL_FONT):
    cells = []
    for style in BACKGROUND_STYLES:
        cells.append(
            render_frames(items, style, title_font, label_font)[4]
            .convert("RGBA")
            .resize((178, 178), Image.Resampling.LANCZOS)
        )
    sheet = Image.new("RGBA", (178 * len(cells), 178), (7, 6, 16, 255))
    for index, cell in enumerate(cells):
        sheet.alpha_composite(cell, (index * 178, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def main():
    args = parse_args()
    output = project_path(args.output)
    poster = project_path(args.poster) if args.poster else None
    variant_posters = project_path(args.variant_posters) if args.variant_posters else None
    if args.dry_run:
        print(output.relative_to(PROJECT_ROOT))
        if poster:
            print(poster.relative_to(PROJECT_ROOT))
        return

    items = load_item_art()
    title_font = font("display", 25, args.font_file)
    label_font = font("display", 17, args.font_file)
    frames = render_frames(items, args.background_style, title_font, label_font)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0, disposal=2, optimize=False)
    if poster:
        poster.parent.mkdir(parents=True, exist_ok=True)
        render_frames(items, args.background_style, title_font, label_font)[4].convert("RGBA").save(poster)
    if variant_posters:
        save_variant_posters(items, variant_posters, title_font, label_font)
    print(output.relative_to(PROJECT_ROOT))
    if poster:
        print(poster.relative_to(PROJECT_ROOT))
    if variant_posters:
        print(variant_posters.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
