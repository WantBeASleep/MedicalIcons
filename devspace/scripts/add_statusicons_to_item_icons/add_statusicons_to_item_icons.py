from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
DEV_ITEMS_ROOT = PROJECT_ROOT / "devspace" / "items"
STATUSICONS_ROOT = PROJECT_ROOT / "devspace" / "statusicons"
INPUT_CSV = SCRIPT_DIR / "input.csv"

ICON_SIZE = 64
STATUSICON_SIZE = 24


@dataclass(frozen=True)
class OverlayRequest:
    identifier: str
    statusicon: str


def normalize_postfix(postfix: str) -> str:
    if postfix.endswith(".png"):
        postfix = postfix[:-4]
    if "/" in postfix or "\\" in postfix:
        raise ValueError("--output_postfix must be a filename postfix, not a path")
    return postfix


def normalize_statusicon_name(name: str) -> str:
    name = name.strip()
    if name.endswith(".png"):
        name = name[:-4]
    if not name:
        raise ValueError("statusicon value must not be empty")
    if "/" in name or "\\" in name:
        raise ValueError(f"statusicon must be a filename stem, not a path: {name}")
    return name


def load_requests(path: Path) -> list[OverlayRequest]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"{path.relative_to(PROJECT_ROOT)} is empty")

        identifier_field = None
        for candidate in ("identifier", "identefer"):
            if candidate in reader.fieldnames:
                identifier_field = candidate
                break
        if identifier_field is None or "statusicon" not in reader.fieldnames:
            raise ValueError(
                f"{path.relative_to(PROJECT_ROOT)} must have columns: identifier,statusicon"
            )

        requests: list[OverlayRequest] = []
        for row_number, row in enumerate(reader, start=2):
            identifier = (row.get(identifier_field) or "").strip()
            statusicon = normalize_statusicon_name(row.get("statusicon") or "")
            if not identifier:
                raise ValueError(f"Missing identifier in {path.relative_to(PROJECT_ROOT)} row {row_number}")
            requests.append(OverlayRequest(identifier=identifier, statusicon=statusicon))

    if not requests:
        raise RuntimeError(f"No overlay rows found in {path.relative_to(PROJECT_ROOT)}")
    return requests


def find_item_icon_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}

    for item_dir in sorted(DEV_ITEMS_ROOT.iterdir()):
        identifiers_dir = item_dir / "items"
        if not item_dir.is_dir() or not identifiers_dir.is_dir():
            continue

        for identifier_dir in sorted(identifiers_dir.iterdir()):
            if not identifier_dir.is_dir():
                continue

            identifier = identifier_dir.name
            icon_path = identifier_dir / "icon.png"
            if identifier in paths:
                duplicates.setdefault(identifier, [paths[identifier]]).append(icon_path)
                continue
            paths[identifier] = icon_path

    if duplicates:
        lines = [
            f"- {identifier}: {', '.join(str(path.relative_to(PROJECT_ROOT)) for path in icon_paths)}"
            for identifier, icon_paths in sorted(duplicates.items())
        ]
        raise RuntimeError(
            "Cannot resolve item identifiers; duplicates found:\n"
            + "\n".join(lines)
        )
    return paths


def load_statusicon(name: str) -> Image.Image:
    path = STATUSICONS_ROOT / f"{name}.png"
    if not path.is_file():
        raise FileNotFoundError(f"Missing status icon: {path.relative_to(PROJECT_ROOT)}")

    image = Image.open(path).convert("RGBA")
    if image.size != (STATUSICON_SIZE, STATUSICON_SIZE):
        raise ValueError(
            f"{path.relative_to(PROJECT_ROOT)} must be {STATUSICON_SIZE}x{STATUSICON_SIZE}, got {image.size}"
        )
    return image


def build_overlay_icon(icon_path: Path, statusicon: Image.Image) -> Image.Image:
    if not icon_path.is_file():
        raise FileNotFoundError(f"Missing item icon: {icon_path.relative_to(PROJECT_ROOT)}")

    icon = Image.open(icon_path).convert("RGBA")
    if icon.size != (ICON_SIZE, ICON_SIZE):
        raise ValueError(f"{icon_path.relative_to(PROJECT_ROOT)} must be {ICON_SIZE}x{ICON_SIZE}, got {icon.size}")

    out = icon.copy()
    out.alpha_composite(statusicon, (0, 0))
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Overlay status icons onto item icons.")
    parser.add_argument(
        "--input",
        default=str(INPUT_CSV),
        help="CSV file with identifier,statusicon rows. Defaults to this script directory's input.csv.",
    )
    parser.add_argument(
        "--output_postfix",
        "--output-postfix",
        required=True,
        help="Postfix for output files. Example: _statusicon writes icon_statusicon.png.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_postfix = normalize_postfix(args.output_postfix)
    output_name = f"icon{output_postfix}.png"

    requests = load_requests(input_path)
    icon_paths = find_item_icon_paths()
    statusicon_cache: dict[str, Image.Image] = {}

    missing_identifiers = sorted({request.identifier for request in requests if request.identifier not in icon_paths})
    if missing_identifiers:
        raise RuntimeError("Missing item identifiers: " + ", ".join(missing_identifiers))

    written: list[Path] = []
    for request in requests:
        statusicon = statusicon_cache.get(request.statusicon)
        if statusicon is None:
            statusicon = load_statusicon(request.statusicon)
            statusicon_cache[request.statusicon] = statusicon

        icon_path = icon_paths[request.identifier]
        output_path = icon_path.with_name(output_name)
        build_overlay_icon(icon_path, statusicon).save(output_path)
        written.append(output_path)

    for path in written:
        print(f"Wrote {path.relative_to(PROJECT_ROOT)}")
    print(f"Overlayed {len(written)} item icons")


if __name__ == "__main__":
    main()
