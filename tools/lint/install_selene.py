from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


SELENE_VERSION = "0.31.0"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"
BIN_DIR = PROJECT_ROOT / "bin"
BUILD_DIR = TOOLS_DIR / "_selene_build_src"
SELENE_REPOSITORY = "https://github.com/Kampfkarren/selene.git"


def find_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is not None:
        return executable

    if name == "cargo":
        cargo = Path.home() / ".cargo" / "bin" / "cargo.exe"
        if cargo.is_file():
            return str(cargo)

    raise RuntimeError(f"{name} not found in PATH")


def run_checked(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def remove_tree(path: Path) -> None:
    def on_error(function, failing_path, _exc_info) -> None:
        Path(failing_path).chmod(0o700)
        function(failing_path)

    shutil.rmtree(path, onerror=on_error)


def patch_manifest(manifest_path: Path) -> None:
    manifest = manifest_path.read_text(encoding="utf-8")

    default_before = 'default = ["roblox"]'
    default_after = 'default = ["lua52"]'
    roblox_line = 'roblox = ["selene-lib/roblox", "full_moon/roblox", "ureq"]'
    lua52_line = 'lua52 = ["selene-lib/lua52", "full_moon/lua52"]'

    if default_before not in manifest:
        raise RuntimeError(f"Could not find expected default features in {manifest_path}")
    if roblox_line not in manifest:
        raise RuntimeError(f"Could not find expected roblox feature in {manifest_path}")
    if lua52_line in manifest:
        raise RuntimeError(f"Unexpected existing lua52 feature in {manifest_path}")

    manifest = manifest.replace(default_before, default_after)
    manifest = manifest.replace(roblox_line, f"{roblox_line}\n{lua52_line}")
    manifest_path.write_text(manifest, encoding="utf-8", newline="\n")


def main() -> int:
    git = find_executable("git")
    cargo = find_executable("cargo")

    if BUILD_DIR.exists():
        remove_tree(BUILD_DIR)

    BIN_DIR.mkdir(parents=True, exist_ok=True)

    try:
        run_checked(
            [
                git,
                "clone",
                "--depth",
                "1",
                "--branch",
                SELENE_VERSION,
                SELENE_REPOSITORY,
                str(BUILD_DIR),
            ],
            cwd=PROJECT_ROOT,
        )

        manifest_path = BUILD_DIR / "selene" / "Cargo.toml"
        patch_manifest(manifest_path)

        run_checked(
            [
                cargo,
                "build",
                "--release",
                "-p",
                "selene",
                "--manifest-path",
                str(BUILD_DIR / "Cargo.toml"),
            ],
            cwd=BUILD_DIR,
        )

        shutil.copy2(BUILD_DIR / "target" / "release" / "selene.exe", BIN_DIR / "selene.exe")
    finally:
        if BUILD_DIR.exists():
            remove_tree(BUILD_DIR)

    print(f"Installed Selene {SELENE_VERSION} with Lua 5.2 support to {BIN_DIR / 'selene.exe'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
