from collections import deque
from pathlib import Path
from shutil import copy2

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
TEXTURES_DIR = ROOT / "devspace" / "textures"

VARIANTS = {
    "injection_cartridge": Path(
        r"C:\Users\limanchel\.codex\generated_images\019ee6dd-b99c-7923-bdfa-a8c834c7f5d5\ig_0c8ab3e4961350c0016a370db2fd548191ad0c92f395c4eff5.png"
    ),
    "ampoule_cassette": Path(
        r"C:\Users\limanchel\.codex\generated_images\019ee6dd-b99c-7923-bdfa-a8c834c7f5d5\ig_0c8ab3e4961350c0016a370df80d3881918fbbc282bd1a9af7.png"
    ),
    "injection_kit_tray": Path(
        r"C:\Users\limanchel\.codex\generated_images\019ee6dd-b99c-7923-bdfa-a8c834c7f5d5\ig_0c8ab3e4961350c0016a370e3a09d0819183798926afcc8394.png"
    ),
}


def is_key(pixel):
    r, g, b = pixel[:3]
    return g > 145 and r < 115 and b < 135 and g > r * 1.5 and g > b * 1.4


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
    return image.crop(
        (
            max(0, left - pad),
            max(0, top - pad),
            min(image.width, right + pad),
            min(image.height, bottom + pad),
        )
    )


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
    crop_alpha(image, 1).save(path)


def build_variant(name, source_path):
    out_dir = TEXTURES_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    copy2(source_path, out_dir / "origin.png")
    source = crop_alpha(remove_connected_key(source_path), 16)
    source.save(out_dir / "icon_source.png")
    source.save(out_dir / "sprite_source.png")

    save_fit_canvas(source, out_dir / "icon.png", (64, 64), (60, 60))
    save_tight_sprite(source, out_dir / "sprite.png", (60, 60))


def main():
    for name, source_path in VARIANTS.items():
        build_variant(name, source_path)


if __name__ == "__main__":
    main()
