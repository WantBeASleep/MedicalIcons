from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]


TARGETS: dict[str, tuple[str, tuple[int, int]]] = {
    "antidama1": ("insulin_syringe", (26, 42)),
    "antidama2": ("insulin_syringe", (26, 42)),
    "antinarc": ("vial", (26, 42)),
    "antiparalysis": ("vial", (26, 42)),
    "antipsychosis": ("vial", (26, 42)),
    "antirad": ("vial", (26, 42)),
    "calyxanide": ("vial", (26, 42)),
    "cyanideantidote": ("vial", (26, 42)),
    "deliriumineantidote": ("vial", (26, 42)),
    "morbusineantidote": ("vial", (26, 42)),
    "sufforinantidote": ("vial", (26, 42)),
}


def resize_to_canvas(source: Image.Image, canvas_size: tuple[int, int]) -> Image.Image:
    source = source.convert("RGBA")
    bbox = source.getbbox()
    if bbox is None:
        return Image.new("RGBA", canvas_size, (0, 0, 0, 0))

    cropped = source.crop(bbox)
    max_art_size = (max(1, canvas_size[0] - 2), max(1, canvas_size[1] - 2))
    scale = min(max_art_size[0] / cropped.width, max_art_size[1] / cropped.height)
    rendered_size = (
        max(1, round(cropped.width * scale)),
        max(1, round(cropped.height * scale)),
    )
    rendered = cropped.resize(rendered_size, Image.Resampling.LANCZOS)

    out = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    out.alpha_composite(
        rendered,
        ((canvas_size[0] - rendered_size[0]) // 2, (canvas_size[1] - rendered_size[1]) // 2),
    )
    return out


def main() -> None:
    for identifier, (asset_dir, canvas_size) in TARGETS.items():
        path = PROJECT_ROOT / "devspace" / "textures" / asset_dir / "items" / identifier / "sprite.png"
        sprite = Image.open(path)
        resized = resize_to_canvas(sprite, canvas_size)
        resized.save(path)
        print(f"{identifier}: {sprite.width}x{sprite.height} -> {resized.width}x{resized.height}")


if __name__ == "__main__":
    main()
