from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove Python __pycache__ directories and .pyc files from the mod workspace."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print cache artifacts without deleting them.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the final summary.",
    )
    return parser.parse_args()


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def find_cache_dirs() -> list[Path]:
    return sorted(
        path
        for path in PROJECT_ROOT.rglob("__pycache__")
        if path.is_dir()
    )


def find_pyc_files(cache_dirs: list[Path]) -> list[Path]:
    cache_dir_set = {path.resolve() for path in cache_dirs}
    pyc_files: list[Path] = []

    for path in sorted(PROJECT_ROOT.rglob("*.pyc")):
        if any(parent.resolve() in cache_dir_set for parent in path.parents):
            continue
        pyc_files.append(path)

    return pyc_files


def delete_artifacts(cache_dirs: list[Path], pyc_files: list[Path], dry_run: bool, quiet: bool) -> None:
    for path in pyc_files:
        if not quiet:
            print(f"{'Would remove' if dry_run else 'Removing'} file: {rel(path)}")
        if not dry_run:
            path.unlink()

    for path in cache_dirs:
        if not quiet:
            print(f"{'Would remove' if dry_run else 'Removing'} dir: {rel(path)}")
        if not dry_run:
            shutil.rmtree(path)


def main() -> None:
    args = parse_args()
    cache_dirs = find_cache_dirs()
    pyc_files = find_pyc_files(cache_dirs)

    delete_artifacts(cache_dirs, pyc_files, args.dry_run, args.quiet)

    action = "Found" if args.dry_run else "Removed"
    print(f"{action} {len(cache_dirs)} __pycache__ directorie(s) and {len(pyc_files)} standalone .pyc file(s).")


if __name__ == "__main__":
    main()
