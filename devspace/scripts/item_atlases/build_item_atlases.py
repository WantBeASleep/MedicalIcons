from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
ITEMS_ROOT = PROJECT_ROOT / "devspace" / "items"
MEDICAL_DIR = PROJECT_ROOT / "Items" / "Medical"

ICON_ATLAS = SCRIPT_DIR / "icons.png"
SPRITE_ATLAS = SCRIPT_DIR / "sprites.png"
ICON_CSV = SCRIPT_DIR / "icons.csv"
SPRITE_CSV = SCRIPT_DIR / "sprites.csv"
MEDICAL_ICON_ATLAS = MEDICAL_DIR / "icons.png"
MEDICAL_SPRITE_ATLAS = MEDICAL_DIR / "sprites.png"

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
    image: object
    width: int
    height: int
    source_width: int
    source_height: int


@dataclass(frozen=True)
class BuildOptions:
    icon_suffix: str
    sprite_suffix: str
    copy_to_medical: bool


def round_up(value: int, multiple: int) -> int:
    return math.ceil(value / multiple) * multiple


def asset_filename(base_name: str, suffix: str) -> str:
    return f"{base_name}{suffix}.png"


def normalize_suffix(suffix: str, option_name: str) -> str:
    if suffix.endswith(".png"):
        suffix = suffix[:-4]
    if "/" in suffix or "\\" in suffix:
        raise ValueError(f"{option_name} must be a filename suffix, not a path")
    return suffix


def iter_item_assets(options: BuildOptions) -> list[ItemAsset]:
    assets: list[ItemAsset] = []
    missing_errors: list[str] = []
    icon_name = asset_filename("icon", options.icon_suffix)
    sprite_name = asset_filename("sprite", options.sprite_suffix)

    for item_dir in sorted(ITEMS_ROOT.iterdir()):
        identifiers_dir = item_dir / "items"
        if not item_dir.is_dir() or not identifiers_dir.is_dir():
            continue

        for identifier_dir in sorted(identifiers_dir.iterdir()):
            if not identifier_dir.is_dir():
                continue

            icon_path = identifier_dir / icon_name
            sprite_path = identifier_dir / sprite_name
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


def build_icon_atlas(assets: list[ItemAsset], output_paths: list[Path]) -> list[AtlasEntry]:
    from PIL import Image

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

    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atlas.save(output_path)
    return entries


def build_sprite_atlas(assets: list[ItemAsset], output_paths: list[Path]) -> list[AtlasEntry]:
    from PIL import Image

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

    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        atlas.save(output_path)
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


def parse_args() -> BuildOptions:
    parser = argparse.ArgumentParser(description="Build item icon and sprite atlases.")
    parser.add_argument(
        "--icons_suf",
        "--icons-suf",
        dest="icon_suffix",
        default="",
        help="Suffix for source icon files. Example: --icons_suf _statusicon reads icon_statusicon.png.",
    )
    parser.add_argument(
        "--sprites_suf",
        "--sprites-suf",
        dest="sprite_suffix",
        default="",
        help="Suffix for source sprite files. Example: --sprites_suf _large reads sprite_large.png.",
    )
    parser.add_argument(
        "--mod-output",
        "--copy-to-medical",
        dest="copy_to_medical",
        action="store_true",
        help="Also write icons.png and sprites.png directly to Items/Medical for the playable mod.",
    )
    args = parser.parse_args()
    return BuildOptions(
        icon_suffix=normalize_suffix(args.icon_suffix, "--icons_suf"),
        sprite_suffix=normalize_suffix(args.sprite_suffix, "--sprites_suf"),
        copy_to_medical=args.copy_to_medical,
    )


def main() -> None:
    options = parse_args()
    assets = iter_item_assets(options)
    icon_outputs = [ICON_ATLAS]
    sprite_outputs = [SPRITE_ATLAS]
    if options.copy_to_medical:
        icon_outputs.append(MEDICAL_ICON_ATLAS)
        sprite_outputs.append(MEDICAL_SPRITE_ATLAS)

    icon_entries = build_icon_atlas(assets, icon_outputs)
    sprite_entries = build_sprite_atlas(assets, sprite_outputs)
    write_csv(ICON_CSV, icon_entries)
    write_csv(SPRITE_CSV, sprite_entries)

    print(f"Built {ICON_ATLAS.relative_to(PROJECT_ROOT)} ({len(icon_entries)} icons)")
    print(f"Built {SPRITE_ATLAS.relative_to(PROJECT_ROOT)} ({len(sprite_entries)} sprites)")
    if options.copy_to_medical:
        print(f"Built {MEDICAL_ICON_ATLAS.relative_to(PROJECT_ROOT)}")
        print(f"Built {MEDICAL_SPRITE_ATLAS.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {ICON_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {SPRITE_CSV.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
