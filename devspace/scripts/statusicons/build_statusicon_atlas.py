from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
STATUSICONS_ROOT = PROJECT_ROOT / "devspace" / "statusicons"

ATLAS_PATH = STATUSICONS_ROOT / "atlas.png"

STATUSICON_SIZE = 24
ATLAS_MAX_WIDTH = 512


@dataclass(frozen=True)
class StatusIcon:
    name: str
    path: Path
    image: Image.Image


def iter_status_icons() -> list[StatusIcon]:
    if not STATUSICONS_ROOT.is_dir():
        raise FileNotFoundError(f"Missing status icon folder: {STATUSICONS_ROOT}")

    icons: list[StatusIcon] = []
    for path in sorted(STATUSICONS_ROOT.glob("affliction_*.png")):
        if path.name == ATLAS_PATH.name:
            continue

        image = Image.open(path).convert("RGBA")
        if image.size != (STATUSICON_SIZE, STATUSICON_SIZE):
            relative_path = path.relative_to(PROJECT_ROOT)
            raise ValueError(f"{relative_path} must be {STATUSICON_SIZE}x{STATUSICON_SIZE}, got {image.size}")

        icons.append(StatusIcon(name=path.stem, path=path, image=image))

    if not icons:
        relative_root = STATUSICONS_ROOT.relative_to(PROJECT_ROOT)
        raise RuntimeError(f"No affliction_*.png files found under {relative_root}")

    return icons


def build_atlas(icons: list[StatusIcon]) -> None:
    columns = max(1, min(ATLAS_MAX_WIDTH // STATUSICON_SIZE, math.ceil(math.sqrt(len(icons)))))
    rows = math.ceil(len(icons) / columns)

    atlas = Image.new("RGBA", (columns * STATUSICON_SIZE, rows * STATUSICON_SIZE), (0, 0, 0, 0))
    for index, icon in enumerate(icons):
        x = index % columns * STATUSICON_SIZE
        y = index // columns * STATUSICON_SIZE
        atlas.alpha_composite(icon.image, (x, y))

    atlas.save(ATLAS_PATH)


def main() -> None:
    icons = iter_status_icons()
    build_atlas(icons)

    print(f"Built {ATLAS_PATH.relative_to(PROJECT_ROOT)} ({len(icons)} status icons)")


if __name__ == "__main__":
    main()
