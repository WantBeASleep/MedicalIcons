from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
BBCODE_PATH = ROOT / "workshop_description_ru.bbcode"
OUT_PATH = ROOT / "devspace" / "preview" / "workshop_item_replacements_ru.png"

GITHUB_PREFIX = (
    "https://raw.githubusercontent.com/WantBeASleep/MedicalIcons/master/"
)


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fonts_dir = Path("C:/Windows/Fonts")
    for filename in (name, "arial.ttf"):
        path = fonts_dir / filename
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def parse_cells(row: str, tag: str) -> list[str]:
    return re.findall(rf"\[{tag}\](.*?)\[/{tag}\]", row, flags=re.S)


def extract_table_rows(bbcode: str) -> tuple[list[str], list[list[str]]]:
    table_match = re.search(r"\[table[^\]]*\](.*?)\[/table\]", bbcode, flags=re.S)
    if not table_match:
        raise ValueError("No [table] block found in BBCode")

    row_blocks = re.findall(r"\[tr\](.*?)\[/tr\]", table_match.group(1), flags=re.S)
    if not row_blocks:
        raise ValueError("No [tr] rows found in table")

    headers = [cell.strip() for cell in parse_cells(row_blocks[0], "th")]
    rows = [[cell.strip() for cell in parse_cells(block, "td")] for block in row_blocks[1:]]
    return headers, rows


def cell_text_or_image(cell: str) -> str | Path:
    image_match = re.search(r"\[img\](.*?)\[/img\]", cell, flags=re.S)
    if not image_match:
        return cell

    url = image_match.group(1).strip()
    if not url.startswith(GITHUB_PREFIX):
        raise ValueError(f"Unsupported image URL: {url}")

    relative = url[len(GITHUB_PREFIX) :].replace("/", "\\")
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    return image.getchannel("A").getbbox()


def fit_image(path: Path, max_width: int, max_height: int) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    bbox = alpha_bbox(image)
    if bbox:
        image = image.crop(bbox)
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    width, height = text_size(draw, text, font)
    draw.text((x0 + (x1 - x0 - width) / 2, y0 + (y1 - y0 - height) / 2 - 1), text, font=font, fill=fill)


def main() -> None:
    bbcode = BBCODE_PATH.read_text(encoding="utf-8")
    headers, rows = extract_table_rows(bbcode)
    parsed_rows = [[cell_text_or_image(cell) for cell in row] for row in rows]

    title_font = load_font("arialbd.ttf", 30)
    header_font = load_font("arialbd.ttf", 18)
    body_font = load_font("arial.ttf", 17)

    columns = [245, 170, 92, 92]
    margin = 28
    header_height = 42
    row_height = 78
    title_height = 58
    footer_height = 22
    table_width = sum(columns)
    image_width = table_width + margin * 2
    image_height = title_height + header_height + row_height * len(parsed_rows) + footer_height + margin

    bg = (14, 18, 22)
    header_bg = (34, 45, 54)
    row_bg_a = (23, 29, 34)
    row_bg_b = (28, 35, 40)
    grid = (72, 89, 97)
    title_fill = (230, 238, 236)
    text_fill = (210, 222, 220)
    muted_fill = (165, 183, 180)

    canvas = Image.new("RGB", (image_width, image_height), bg)
    draw = ImageDraw.Draw(canvas)

    title = "QoL - Medical Icons: Item replacements"
    draw.text((margin, 18), title, font=title_font, fill=title_fill)

    table_x = margin
    y = title_height

    draw.rectangle((table_x, y, table_x + table_width, y + header_height), fill=header_bg)
    x = table_x
    for header, width in zip(headers, columns):
        draw_centered_text(draw, (x, y, x + width, y + header_height), header, header_font, title_fill)
        x += width

    y += header_height
    for index, row in enumerate(parsed_rows):
        row_bg = row_bg_a if index % 2 == 0 else row_bg_b
        draw.rectangle((table_x, y, table_x + table_width, y + row_height), fill=row_bg)

        x = table_x
        for col_index, (cell, width) in enumerate(zip(row, columns)):
            if isinstance(cell, Path):
                art = fit_image(cell, 64, 64)
                px = x + (width - art.width) // 2
                py = y + (row_height - art.height) // 2
                canvas.paste(art, (px, py), art)
            else:
                fill = text_fill if col_index == 0 else muted_fill
                draw_centered_text(draw, (x, y, x + width, y + row_height), str(cell), body_font, fill)
            x += width

        y += row_height

    # Crisp grid lines over the alternating rows.
    x = table_x
    for width in [0, *columns]:
        draw.line((x, title_height, x, y), fill=grid, width=1)
        x += width
    draw.line((table_x + table_width, title_height, table_x + table_width, y), fill=grid, width=1)
    for line_index in range(len(parsed_rows) + 2):
        ly = title_height + header_height + row_height * (line_index - 1) if line_index else title_height
        if title_height <= ly <= y:
            draw.line((table_x, ly, table_x + table_width, ly), fill=grid, width=1)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT_PATH)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
