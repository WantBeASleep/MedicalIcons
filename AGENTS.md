# Project Notes

## Overview
This project is a Barotrauma local client-side only mod named `Medical Icons` working by LuaCs bridge.

The project separates development-only files from the final Barotrauma mod files.


## Development Workspace
All development-only files belong under `internal`; do not place sources, references, scripts, temporary files, or working files outside it.

Development areas:

- `internal/fonts` - fonts used by preview/generation scripts.
- `internal/paint.net` - paint.net working files.
- `internal/preview` - development and Workshop previews.
- `internal/scripts` - automation and validation scripts.
- `internal/statusicons` - status icon sources.
- `internal/textures` - item icon/sprite sources and final per-item texture inputs.

## Mod-Facing Files
Everything outside `internal` is mod-facing or publishing-facing; only place files there when Barotrauma needs them at runtime or they are explicit publishing files.

- `filelist.xml` - root Barotrauma mod descriptor.
- `workshop_description_en.bbcode` - English Steam Workshop description, similar to a Workshop-facing README.
- `workshop_description_ru.bbcode` - Russian Steam Workshop description, similar to a Workshop-facing README.

## Build Workflow
The canonical build command is:

```powershell
python internal/scripts/build_project/build_project.py --all
```

The build packs texture/status icon atlases and generates the Lua atlas data file used by the mod.

Run the mod build workflow only when a change affects runtime data or generated assets: item icons/sprites under `internal/textures/*/items/*`, status icon inputs, atlas packing behavior or scripts that generate atlas data.

## Agent Guidelines
- Keep development artifacts inside `internal`.
- Keep the mod root clean and Barotrauma-ready.
- Before adding new root-level files, verify that Barotrauma needs them at runtime.
- Scripts must not hard-code absolute paths or depend on external files outside the Barotrauma install/project tree. Computing paths from the current script, project root, or known Barotrauma directory structure is allowed. If a script needs external support files such as fonts, images, templates, or references, copy those files into the appropriate `internal` folder and load them from there.
- After running any Python script anywhere in this project, remove all generated `__pycache__` folders and `.pyc` files from the mod workspace. The mod may be published to Steam Workshop with source files included, and Workshop publishing does not use `.gitignore` to exclude Python cache artifacts.
