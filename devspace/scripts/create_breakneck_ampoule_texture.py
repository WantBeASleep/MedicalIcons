from collections import deque
from pathlib import Path
from shutil import copy2

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "devspace" / "textures" / "breakneck_ampoule"

ICON_RAW = Path(
    r"C:\Users\limanchel\.codex\generated_images\019ee6dd-b99c-7923-bdfa-a8c834c7f5d5\ig_0c8ab3e4961350c0016a3704f89d7881919d0b05af39634ada.png"
)
SPRITE_RAW = Path(
    r"C:\Users\limanchel\.codex\generated_images\019ee6dd-b99c-7923-bdfa-a8c834c7f5d5\ig_0c8ab3e4961350c0016a3705bd197c8191949d6b504d664db2.png"
)


def is_key(pixel):
    r, g, b = pixel[:3]
    return g > 145 and r < 110 and b < 130 and g > r * 1.55 and g > b * 1.45


def remove_connected_key(path):
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    pixels = image.load()
    seen = bytearray(width * height)
    alpha = Image.new("L", image.size, 255)
    alpha_px = alpha.load()
    queue = deque()

    def enqueue(x, y):
        idx = y * width + x
        if not seen[idx] and is_key(pixels[x, y]):
            seen[idx] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        alpha_px[x, y] = 0
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.55))
    image.putalpha(alpha)
    return image


def crop_alpha(image, pad=8):
    bbox = image.getbbox()
    if bbox is None:
        return image
    left, top, right, bottom = bbox
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width, right + pad)
    bottom = min(image.height, bottom + pad)
    return image.crop((left, top, right, bottom))


def save_fit_canvas(image, path, canvas_size, max_size):
    image = crop_alpha(image, 4)
    scale = min(max_size[0] / image.width, max_size[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    canvas.alpha_composite(image, ((canvas_size[0] - size[0]) // 2, (canvas_size[1] - size[1]) // 2))
    canvas.save(path)


def save_tight_sprite(image, path, max_size):
    image = crop_alpha(image, 4)
    scale = min(max_size[0] / image.width, max_size[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    image = crop_alpha(image, 1)
    image.save(path)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    copy2(ICON_RAW, OUT_DIR / "origin.png")

    icon_source = crop_alpha(remove_connected_key(ICON_RAW), 16)
    sprite_source = crop_alpha(remove_connected_key(SPRITE_RAW), 16)

    icon_source.save(OUT_DIR / "icon_source.png")
    sprite_source.save(OUT_DIR / "sprite_source.png")

    save_fit_canvas(icon_source, OUT_DIR / "icon.png", (64, 64), (60, 60))
    save_tight_sprite(sprite_source, OUT_DIR / "sprite.png", (34, 60))


if __name__ == "__main__":
    main()
