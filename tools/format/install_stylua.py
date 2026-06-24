from __future__ import annotations

import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path


STYLUA_VERSION = "2.5.2"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = PROJECT_ROOT / "tools"
BIN_DIR = PROJECT_ROOT / "bin"
DOWNLOAD_DIR = TOOLS_DIR / "_stylua_download"
ARCHIVE_PATH = DOWNLOAD_DIR / "stylua-windows-x86_64.zip"
STYLUA_URL = (
    "https://github.com/JohnnyMorganz/StyLua/releases/download/"
    f"v{STYLUA_VERSION}/stylua-windows-x86_64.zip"
)


def remove_tree(path: Path) -> None:
    def on_error(function, failing_path, _exc_info) -> None:
        Path(failing_path).chmod(0o700)
        function(failing_path)

    shutil.rmtree(path, onerror=on_error)


def run_checked(command: list[str]) -> None:
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> int:
    if DOWNLOAD_DIR.exists():
        remove_tree(DOWNLOAD_DIR)

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Downloading StyLua {STYLUA_VERSION} from {STYLUA_URL}")
        urllib.request.urlretrieve(STYLUA_URL, ARCHIVE_PATH)

        with zipfile.ZipFile(ARCHIVE_PATH) as archive:
            archive.extract("stylua.exe", DOWNLOAD_DIR)

        shutil.copy2(DOWNLOAD_DIR / "stylua.exe", BIN_DIR / "stylua.exe")
    finally:
        if DOWNLOAD_DIR.exists():
            remove_tree(DOWNLOAD_DIR)

    run_checked([sys.executable, "tools/build/clean_python_cache/clean_python_cache.py"])

    print(f"Installed StyLua {STYLUA_VERSION} to {BIN_DIR / 'stylua.exe'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, OSError, zipfile.BadZipFile) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
