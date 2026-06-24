# Lua format tools

This directory contains helper scripts for installing and running StyLua for
the LuaCs runtime code in `Lua/`.

The project uses StyLua with `syntax = "Lua52"` to match the LuaCs/MoonSharp
syntax mode used by Selene.

## `install_stylua.py`

Installs the local StyLua binary used by `run_stylua.py`.

```powershell
python tools\format\install_stylua.py
```

The script:

- downloads the StyLua Windows x86_64 release archive from GitHub;
- extracts `stylua.exe`;
- copies the executable to `bin/stylua.exe`;
- removes the temporary download directory;
- runs the project's Python cache cleanup script.

## `run_stylua.py`

Runs the local StyLua binary against the project's Lua runtime files.

Check formatting without rewriting files:

```powershell
python tools\format\run_stylua.py --check
```

Format files in place:

```powershell
python tools\format\run_stylua.py
```

The script:

- finds the project root from its own location;
- expects StyLua at `bin/stylua.exe`;
- runs StyLua against `Lua/`;
- always passes `--verify`;
- returns StyLua's exit code.

After running this or any other Python script in the project, remove Python
cache artifacts:

```powershell
python tools\build\clean_python_cache\clean_python_cache.py
```
