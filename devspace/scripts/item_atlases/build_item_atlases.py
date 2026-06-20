from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
ITEMS_ROOT = PROJECT_ROOT / "devspace" / "items"

ICON_ATLAS = SCRIPT_DIR / "icons.png"
SPRITE_ATLAS = SCRIPT_DIR / "sprites.png"
ICON_CSV = SCRIPT_DIR / "icons.csv"
SPRITE_CSV = SCRIPT_DIR / "sprites.csv"

ICON_SIZE = 64
SPRITE_ATLAS_MAX_WIDTH = 512


@dataclass(frozen=True)
class ItemAsset:
    item: str
    identifier: str
    folder: Path
    icon_path: Path
    sprite_path: Path


@dataclass(frozen=True)
class AtlasEntry:
    item: str
    identifier: str
    source: str
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class SpriteAsset:
    item_asset: ItemAsset
    image: Image.Image
    width: int
    height: int
    source_width: int
    source_height: int


def round_up(value: int, multiple: int) -> int:
    return math.ceil(value / multiple) * multiple


def iter_item_assets() -> list[ItemAsset]:
    assets: list[ItemAsset] = []
    missing_errors: list[str] = []
    for item_dir in sorted(ITEMS_ROOT.iterdir()):
        identifiers_dir = item_dir / "items"
        if not item_dir.is_dir() or not identifiers_dir.is_dir():
            continue

        for identifier_dir in sorted(identifiers_dir.iterdir()):
            if not identifier_dir.is_dir():
                continue

            icon_path = identifier_dir / "icon.png"
            sprite_path = identifier_dir / "sprite.png"
            missing = [p.name for p in (icon_path, sprite_path) if not p.is_file()]
            if missing:
                joined = ", ".join(missing)
                missing_errors.append(f"{identifier_dir.relative_to(PROJECT_ROOT)} is missing: {joined}")
                continue

            assets.append(
                ItemAsset(
                    item=item_dir.name,
                    identifier=identifier_dir.name,
                    folder=identifier_dir,
                    icon_path=icon_path,
                    sprite_path=sprite_path,
                )
            )

    if missing_errors:
        joined_errors = "\n".join(f"- {error}" for error in missing_errors)
        raise FileNotFoundError(f"Cannot build item atlases; required item asset files are missing:\n{joined_errors}")

    if not assets:
        raise RuntimeError(f"No item assets found under {ITEMS_ROOT}")

    return assets


def build_icon_atlas(assets: list[ItemAsset]) -> list[AtlasEntry]:
    columns = max(1, math.ceil(math.sqrt(len(assets))))
    rows = math.ceil(len(assets) / columns)
    atlas = Image.new("RGBA", (columns * ICON_SIZE, rows * ICON_SIZE), (0, 0, 0, 0))
    entries: list[AtlasEntry] = []

    for index, asset in enumerate(assets):
        icon = Image.open(asset.icon_path).convert("RGBA")
        if icon.size != (ICON_SIZE, ICON_SIZE):
            raise ValueError(f"{asset.icon_path} must be {ICON_SIZE}x{ICON_SIZE}, got {icon.size}")

        x = index % columns * ICON_SIZE
        y = index // columns * ICON_SIZE
        atlas.alpha_composite(icon, (x, y))
        entries.append(
            AtlasEntry(
                item=asset.item,
                identifier=asset.identifier,
                source=str(asset.icon_path.relative_to(PROJECT_ROOT)),
                x=x,
                y=y,
                width=ICON_SIZE,
                height=ICON_SIZE,
            )
        )

    atlas.save(ICON_ATLAS)
    return entries


def build_sprite_atlas(assets: list[ItemAsset]) -> list[AtlasEntry]:
    loaded: list[SpriteAsset] = []
    for asset in assets:
        sprite = Image.open(asset.sprite_path).convert("RGBA")
        source_width, source_height = sprite.size
        padded_width = round_up(source_width, 4)
        padded_height = round_up(source_height, 4)
        if (padded_width, padded_height) != sprite.size:
            padded = Image.new("RGBA", (padded_width, padded_height), (0, 0, 0, 0))
            padded.alpha_composite(sprite, (0, 0))
            sprite = padded
        loaded.append(
            SpriteAsset(
                item_asset=asset,
                image=sprite,
                width=padded_width,
                height=padded_height,
                source_width=source_width,
                source_height=source_height,
            )
        )

    x = 0
    y = 0
    row_height = 0
    placements: list[tuple[SpriteAsset, int, int]] = []

    for sprite_asset in loaded:
        width = sprite_asset.width
        height = sprite_asset.height
        asset = sprite_asset.item_asset
        if width > SPRITE_ATLAS_MAX_WIDTH:
            raise ValueError(f"{asset.sprite_path} width exceeds atlas max width {SPRITE_ATLAS_MAX_WIDTH}")

        if x and x + width > SPRITE_ATLAS_MAX_WIDTH:
            x = 0
            y += row_height
            row_height = 0

        placements.append((sprite_asset, x, y))
        x += width
        row_height = max(row_height, height)

    atlas_width = round_up(max((px + sprite_asset.width for sprite_asset, px, _ in placements), default=1), 4)
    atlas_height = round_up(max((py + sprite_asset.height for sprite_asset, _, py in placements), default=1), 4)
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    entries: list[AtlasEntry] = []

    for sprite_asset, px, py in placements:
        asset = sprite_asset.item_asset
        atlas.alpha_composite(sprite_asset.image, (px, py))
        entries.append(
            AtlasEntry(
                item=asset.item,
                identifier=asset.identifier,
                source=str(asset.sprite_path.relative_to(PROJECT_ROOT)),
                x=px,
                y=py,
                width=sprite_asset.width,
                height=sprite_asset.height,
            )
        )

    atlas.save(SPRITE_ATLAS)
    return entries


def write_csv(path: Path, entries: list[AtlasEntry]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["item", "identifier", "source", "x", "y", "width", "height", "sourcerect"],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "item": entry.item,
                    "identifier": entry.identifier,
                    "source": entry.source,
                    "x": entry.x,
                    "y": entry.y,
                    "width": entry.width,
                    "height": entry.height,
                    "sourcerect": f"{entry.x},{entry.y},{entry.width},{entry.height}",
                }
            )


def main() -> None:
    assets = iter_item_assets()
    icon_entries = build_icon_atlas(assets)
    sprite_entries = build_sprite_atlas(assets)
    write_csv(ICON_CSV, icon_entries)
    write_csv(SPRITE_CSV, sprite_entries)

    print(f"Built {ICON_ATLAS.relative_to(PROJECT_ROOT)} ({len(icon_entries)} icons)")
    print(f"Built {SPRITE_ATLAS.relative_to(PROJECT_ROOT)} ({len(sprite_entries)} sprites)")
    print(f"Wrote {ICON_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {SPRITE_CSV.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
