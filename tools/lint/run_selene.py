from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SELENE = PROJECT_ROOT / "bin" / "selene.exe"
LUA_DIR = PROJECT_ROOT / "Lua"


def main() -> int:
    if not SELENE.is_file():
        print(f"Selene executable not found at {SELENE}", file=sys.stderr)
        return 1

    completed = subprocess.run([str(SELENE), str(LUA_DIR)], cwd=PROJECT_ROOT)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
