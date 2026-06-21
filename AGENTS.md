# Project Notes

## Overview
This project is a Barotrauma local mod named `Medical Icons`.

The mod contains medical item icons, sprites, source images, generated atlases, XML overrides, and Steam Workshop publishing text. The project separates development-only files from the final Barotrauma mod files.

## Project Location
The intended project folder is:

```text
D:\SteamLibrary\steamapps\common\Barotrauma\LocalMods\Medical Icons
```

## Instruction Layout
Use the nearest `AGENTS.md` for the files you are working on. This root file contains only project-wide rules.

Area-specific instructions live here:

- `devspace/textures/AGENTS.md` - item icon and sprite source assets, final per-item `icon.png` and `sprite.png` files, visual generation rules, sprite sizing references.
- `devspace/preview/AGENTS.md` - development-only preview images and Steam Workshop preview generation.
- `devspace/scripts/AGENTS.md` - global project automation, build pipeline, validation, XML generation, and filelist updates.
- `devspace/statusicons/AGENTS.md` - 24x24 Barotrauma affliction status icons.
- `devspace/paint.net/AGENTS.md` - paint.net working files and visual editing sources.
- `Items/Medical/AGENTS.md` - mod-facing medical atlases and XML override outputs.

## Development Workspace
All development-only assets must be stored inside `devspace`.

Do not place development sources, references, scripts, temporary files, or working files outside `devspace`.

Expected development structure:

```text
devspace/
  fonts/
  paint.net/
  preview/
  reference/
  scripts/
  statusicons/
  textures/
```

`devspace/reference` stores original Barotrauma sprites and icons used as visual references. Use this folder when matching the original Barotrauma icon and sprite style.

`devspace/fonts` stores font files used by development-only preview generation scripts. These fonts are not used by Barotrauma at runtime and must not be added to `filelist.xml`.

## Mod-Facing Files
Everything outside `devspace` is mod-facing or publishing-facing.

Do not store files outside `devspace` unless they are required for the mod to work in Barotrauma or are explicit publishing files.

Expected mod-facing and publishing-facing structure:

```text
filelist.xml
workshop_description_en.bbcode
workshop_description_ru.bbcode
Items/
  Medical/
    Icons.png
    Sprites.png
    medical.xml
    poisons.xml
    buffs.xml
```

Root file meanings:

- `filelist.xml` - root Barotrauma mod descriptor.
- `workshop_description_en.bbcode` - English Steam Workshop description, similar to a Workshop-facing README.
- `workshop_description_ru.bbcode` - Russian Steam Workshop description, similar to a Workshop-facing README.
- `Items/Medical` - Barotrauma item files for the medical part of the mod.

## Build Workflow Trigger
Run the mod build workflow whenever a project change affects the future runtime build of the mod. This includes changes to final item icons or sprites under `devspace/textures/*/items/*`, status icon overlay inputs, build scripts, XML generation rules, atlas packing behavior, or any other source that changes the generated `Items/Medical` outputs.

Do not run the mod build workflow for changes that only affect documentation, `devspace/preview`, `devspace/paint.net`, Steam Workshop descriptions, or other publishing/development-only files unless the user explicitly asks to rebuild.

When changing icon or sprite layout, update the relevant atlas and XML references together only if the user explicitly asked to build or update the mod-facing files.

## Agent Guidelines
- Keep development artifacts inside `devspace`.
- Keep the mod root clean and Barotrauma-ready.
- Before adding new root-level files, verify that Barotrauma needs them at runtime.
- Scripts must not hard-code absolute paths or depend on external files outside the Barotrauma install/project tree. Computing paths from the current script, project root, or known Barotrauma directory structure is allowed. If a script needs external support files such as fonts, images, templates, or references, copy those files into the appropriate `devspace` folder and load them from there.
- Make visual changes to icons, sprites, and source images by regenerating the visual asset, not by manually editing or patching the bitmap.
- After running any Python script anywhere in this project, remove all generated `__pycache__` folders and `.pyc` files from the mod workspace. The mod may be published to Steam Workshop with source files included, and Workshop publishing does not use `.gitignore` to exclude Python cache artifacts.
