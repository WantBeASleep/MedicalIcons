from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class AtlasEntry:
    identifier: str
    image_path: Path
    image: Image.Image


@dataclass(frozen=True)
class PlacedEntry:
    identifier: str
    image_path: Path
    x: int
    y: int
    width: int
    height: int

    @property
    def sourcerect(self) -> str:
        return f"{self.x},{self.y},{self.width},{self.height}"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_entries(items_dir: Path, image_name: str) -> list[AtlasEntry]:
    if not items_dir.exists():
        raise FileNotFoundError(f"Items directory not found: {items_dir}")

    entries: list[AtlasEntry] = []
    for item_dir in sorted(path for path in items_dir.iterdir() if path.is_dir()):
        image_path = item_dir / image_name
        if not image_path.exists():
            continue

        image = Image.open(image_path).convert("RGBA")
        if image.width < 1 or image.height < 1:
            raise ValueError(f"Image has invalid size: {image_path}")

        entries.append(
            AtlasEntry(
                identifier=item_dir.name,
                image_path=image_path,
                image=image,
            )
        )

    if not entries:
        raise ValueError(f"No {image_name} files found in {items_dir}")

    return entries


def place_entries(entries: list[AtlasEntry], max_width: int, padding: int) -> tuple[list[PlacedEntry], tuple[int, int]]:
    if max_width < 1:
        raise ValueError("Atlas max width must be 1 or greater.")
    if padding < 0:
        raise ValueError("Padding cannot be negative.")

    placed: list[PlacedEntry] = []
    cursor_x = 0
    cursor_y = 0
    row_height = 0
    atlas_width = 0

    for entry in entries:
        image_width, image_height = entry.image.size
        if image_width > max_width:
            raise ValueError(f"{entry.image_path} is wider than the atlas max width ({max_width}px).")

        if cursor_x and cursor_x + image_width > max_width:
            cursor_x = 0
            cursor_y += row_height + padding
            row_height = 0

        placed.append(
            PlacedEntry(
                identifier=entry.identifier,
                image_path=entry.image_path,
                x=cursor_x,
                y=cursor_y,
                width=image_width,
                height=image_height,
            )
        )

        atlas_width = max(atlas_width, cursor_x + image_width)
        cursor_x += image_width + padding
        row_height = max(row_height, image_height)

    atlas_height = cursor_y + row_height
    return placed, (atlas_width, atlas_height)


def build_atlas(
    entries: list[AtlasEntry],
    output_atlas_path: Path,
    output_csv_path: Path,
    max_width: int,
    padding: int,
) -> list[PlacedEntry]:
    placed, atlas_size = place_entries(entries, max_width=max_width, padding=padding)
    atlas = Image.new("RGBA", atlas_size, (0, 0, 0, 0))

    images_by_identifier = {entry.identifier: entry.image for entry in entries}
    for entry in placed:
        atlas.alpha_composite(images_by_identifier[entry.identifier], (entry.x, entry.y))

    output_atlas_path.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output_atlas_path)

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with output_csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "identifier",
                "x",
                "y",
                "width",
                "height",
                "sourcerect",
            ],
        )
        writer.writeheader()
        for entry in placed:
            writer.writerow(
                {
                    "identifier": entry.identifier,
                    "x": entry.x,
                    "y": entry.y,
                    "width": entry.width,
                    "height": entry.height,
                    "sourcerect": entry.sourcerect,
                }
            )

    return placed


def build_item_atlases(
    items_dir: Path,
    output_dir: Path,
    csv_dir: Path,
    icon_atlas_name: str,
    sprite_atlas_name: str,
    icon_csv_name: str,
    sprite_csv_name: str,
    atlas_width: int,
    padding: int,
) -> None:
    icon_entries = load_entries(items_dir, "icon.png")
    sprite_entries = load_entries(items_dir, "sprite.png")

    icon_rows = build_atlas(
        entries=icon_entries,
        output_atlas_path=output_dir / icon_atlas_name,
        output_csv_path=csv_dir / icon_csv_name,
        max_width=atlas_width,
        padding=padding,
    )
    sprite_rows = build_atlas(
        entries=sprite_entries,
        output_atlas_path=output_dir / sprite_atlas_name,
        output_csv_path=csv_dir / sprite_csv_name,
        max_width=atlas_width,
        padding=padding,
    )

    print(f"Wrote {len(icon_rows)} icons to {output_dir / icon_atlas_name}")
    print(f"Wrote icon map to {csv_dir / icon_csv_name}")
    print(f"Wrote {len(sprite_rows)} sprites to {output_dir / sprite_atlas_name}")
    print(f"Wrote sprite map to {csv_dir / sprite_csv_name}")


def main() -> None:
    root = project_root()
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Build Barotrauma item icon and sprite atlases from devspace/items."
    )
    parser.add_argument("--items-dir", type=Path, default=root / "devspace" / "items")
    parser.add_argument("--output-dir", type=Path, default=root / "Items" / "Medical")
    parser.add_argument("--csv-dir", type=Path, default=script_dir)
    parser.add_argument("--icon-atlas-name", default="Icons.png")
    parser.add_argument("--sprite-atlas-name", default="Sprites.png")
    parser.add_argument("--icon-csv-name", default="Icons.csv")
    parser.add_argument("--sprite-csv-name", default="Sprites.csv")
    parser.add_argument("--atlas-width", type=int, default=512)
    parser.add_argument("--padding", type=int, default=2)
    args = parser.parse_args()

    build_item_atlases(
        items_dir=args.items_dir,
        output_dir=args.output_dir,
        csv_dir=args.csv_dir,
        icon_atlas_name=args.icon_atlas_name,
        sprite_atlas_name=args.sprite_atlas_name,
        icon_csv_name=args.icon_csv_name,
        sprite_csv_name=args.sprite_csv_name,
        atlas_width=args.atlas_width,
        padding=args.padding,
    )


if __name__ == "__main__":
    main()
