# Project Notes

## Overview
This project is a Barotrauma local client-side only mod named `Medical Icons` working through the LuaCs bridge.

## Project Layout
The project is structured as a normal Lua mod workspace.

Runtime and publishing files:

- `filelist.xml` - root Barotrauma mod descriptor.
- `workshop_description_en.bbcode` - English Steam Workshop description, similar to a Workshop-facing README.
- `workshop_description_ru.bbcode` - Russian Steam Workshop description, similar to a Workshop-facing README.
- `Lua/Autorun` - LuaCs autorun entrypoints.
- `Lua/limanchel/medical_icons` - main Lua module namespace.
- `Lua/limanchel/medical_icons/generated` - generated Lua data used by the runtime.
- `assets` - generated runtime atlases and other assets loaded by the mod.

Development and source areas:

- `source/textures` - item icon/sprite sources and final per-item texture inputs.
- `source/status_icons` - status icon source PNGs.
- `source/fonts` - fonts used by preview/generation scripts.
- `source/paint_dotnet` - paint.net working files.
- `preview/source` - source images for preview generation.
- `tools/build` - whole-project build and validation scripts.
- `tools/atlas` - atlas-specific helper scripts.
- `tools/preview` - preview generation scripts.
- `preview` - generated development and Workshop preview images.

## Build Workflow
The canonical build command is:

```powershell
python tools/build/build_project/build_project.py --all
```

The build packs item icon/sprite atlases into `assets` and generates Lua atlas data under `Lua/limanchel/medical_icons/generated`.

Run the mod build workflow when a change affects runtime data or generated assets: item icons/sprites under `source/textures/*/items/*`, status icon inputs, atlas packing behavior, or scripts that generate atlas data.

## Agent Guidelines
- Keep Lua runtime code under `Lua`, preserving the `limanchel/medical_icons` namespace required by the LuaCs loading layout.
- Store generated Lua files under `Lua/limanchel/medical_icons/generated`.
- Store generated runtime atlases directly under `assets`.
- Keep source assets under `source`, scripts under `tools`, and generated previews under `preview`.
- Scripts must not hard-code absolute paths. Compute paths from the current script, project root, or known Barotrauma directory structure.
- Scripts must not depend on external files outside the Barotrauma install/project tree. If a script needs support files such as fonts, images, templates, or references, copy those files into the appropriate project folder and load them from there.
- After running any Python script anywhere in this project, remove all generated `__pycache__` folders and `.pyc` files from the mod workspace. Use `python tools/build/clean_python_cache/clean_python_cache.py` for cleanup, or `python tools/build/clean_python_cache/clean_python_cache.py --dry-run` to preview what would be removed. The mod may be published to Steam Workshop with source files included, and Workshop publishing does not use `.gitignore` to exclude Python cache artifacts.
