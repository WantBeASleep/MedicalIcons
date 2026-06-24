from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATUSICONS_DIR = PROJECT_ROOT / "internal" / "statusicons"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ATLAS_PATH = STATUSICONS_DIR / "atlas.png"
DEFAULT_CSV_PATH = SCRIPT_DIR / "statusicons.csv"
ICON_SIZE = 24


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Barotrauma status icon atlas and CSV coordinate map."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=STATUSICONS_DIR,
        help="Directory containing 24x24 status icon PNGs.",
    )
    parser.add_argument(
        "--atlas",
        type=Path,
        default=DEFAULT_ATLAS_PATH,
        help="Output atlas PNG path.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help="Output CSV path.",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=0,
        help="Atlas columns. Defaults to a near-square layout.",
    )
    return parser.parse_args()


def discover_icons(source_dir: Path) -> list[Path]:
    icons = sorted(
        path
        for path in source_dir.glob("*.png")
        if path.name.lower() != "atlas.png"
    )
    if not icons:
        raise FileNotFoundError(f"No status icon PNG files found in {source_dir}")
    return icons


def validate_icon(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if image.size != (ICON_SIZE, ICON_SIZE):
        raise ValueError(
            f"{path} is {image.size[0]}x{image.size[1]}, expected {ICON_SIZE}x{ICON_SIZE}"
        )
    return image


def atlas_size(icon_count: int, columns: int) -> tuple[int, int, int]:
    if columns <= 0:
        columns = math.ceil(math.sqrt(icon_count))
    rows = math.ceil(icon_count / columns)
    return columns * ICON_SIZE, rows * ICON_SIZE, columns


def build_atlas(
    icons: list[Path], atlas_path: Path, csv_path: Path, requested_columns: int
) -> None:
    width, height, columns = atlas_size(len(icons), requested_columns)
    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rows: list[dict[str, str | int]] = []

    for index, icon_path in enumerate(icons):
        image = validate_icon(icon_path)
        x = index % columns * ICON_SIZE
        y = index // columns * ICON_SIZE
        atlas.alpha_composite(image, (x, y))
        rows.append(
            {
                "name": icon_path.stem,
                "source": str(icon_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "x": x,
                "y": y,
                "width": ICON_SIZE,
                "height": ICON_SIZE,
                "sourcerect": f"{x},{y},{ICON_SIZE},{ICON_SIZE}",
            }
        )
        image.close()

    atlas_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(atlas_path)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["name", "source", "x", "y", "width", "height", "sourcerect"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote atlas: {atlas_path.relative_to(PROJECT_ROOT)}")
    print(f"Wrote CSV: {csv_path.relative_to(PROJECT_ROOT)}")
    print(f"Packed {len(rows)} status icons into {width}x{height}")


def main() -> None:
    args = parse_args()
    icons = discover_icons(args.source_dir)
    build_atlas(icons, args.atlas, args.csv, args.columns)


if __name__ == "__main__":
    main()
