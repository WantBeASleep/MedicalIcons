# Project Notes

## Overview
This project is a Barotrauma local mod named `Medical Icons`.

The mod contains medical item icons, sprites, and source images.
The project separates development-only files from the final Barotrauma mod files.

## Project Location
The intended project folder is:

`D:\SteamLibrary\steamapps\common\Barotrauma\LocalMods\Medical Icons`

## Directory Structure

### Development Workspace
All development-only assets must be stored inside `devspace`.

Do not place development sources, references, scripts, temporary files, or working files outside `devspace`.

Expected structure:

```text
devspace/
  reference/
  scripts/
  statusicons/
  textures/
```

#### `devspace/textures`
Stores all item graphics and source files.

Each item asset set must have its own folder named after the icon/source asset identifier.

Example:

```text
devspace/textures/insulin_syringe/
```

Each item folder contains source files for the generated artwork and an `items` subfolder for final in-game item assets:

```text
origin.png
icon_source.png
icon.png
sprite_source.png
sprite.png
masks/
items/
  antidama1/
    icon.png
    sprite.png
```

File meanings:

- `origin.png` - generation reference image used to create the item icon; this is not an original Barotrauma style reference.
- `icon_source.png` - large high-resolution source image for the icon.
- `icon.png` - non-game preview/scaffold icon used to evaluate the generated icon's shape and style before creating final in-game item icons.
- `sprite_source.png` - large high-resolution source image for the sprite.
- `sprite.png` - non-game preview/scaffold sprite used to evaluate the generated sprite's shape and style before creating final in-game item sprites.
- `masks/` - optional development-only folder for manual recoloring masks for this item. Create this folder only when a manual mask is required because simple/automatic recoloring does not produce acceptable results.
- `items/` - contains one folder per in-game item that uses this generated artwork.
- `items/<identifier>/` - folder named after the in-game item identifier, for example `items/antidama1/`.
- `items/<identifier>/icon.png` - final 64x64 icon for that in-game item.
- `items/<identifier>/sprite.png` - final sprite displayed in game for that in-game item.

The folder names under `devspace/textures/<item>/items/` are the in-game item identifiers. Final icon and sprite files that will be used by the game must be stored only in these identifier folders. Root-level `icon.png` and `sprite.png` files in an item asset folder are important preview/scaffold files, but they are not used in game.

#### `devspace/reference`
Stores original Barotrauma sprites and icons used as visual references.

Use this folder when matching the original Barotrauma icon and sprite style.

#### `devspace/scripts`
Stores development-only automation scripts.

Current project scripts:

```text
devspace/scripts/
  build_project/
    build_project.py
    README.md
  build_statusicons_atlas/
    build_statusicons_atlas.py
  recolor_dart_syringe_poisons/
    recolor_dart_syringe_poisons.py
  recolor_vial_antidotes/
    recolor_vial_antidotes.py
```

- `build_project.py` - validates generated item assets, optionally overlays status icons, builds final item icon/sprite atlases, writes atlas coordinate CSV files, rebuilds medical XML overrides, and updates root `filelist.xml`.
- `build_statusicons_atlas.py` - builds `devspace/statusicons/atlas.png` from 24x24 status icons and writes status icon coordinates to `devspace/scripts/build_statusicons_atlas/statusicons.csv`.
- `recolor_dart_syringe_poisons.py` - recolors dart syringe poison item assets.
- `recolor_vial_antidotes.py` - recolors vial antidote item assets.

#### `devspace/statusicons`
Stores Barotrauma status affliction icons.

Expected structure:

```text
devspace/statusicons/
  <affliction_name>.png
  atlas.png
```

File meanings:

- `<affliction_name>.png` - individual Barotrauma affliction status icon, 24x24 pixels.
- `atlas.png` - atlas containing all affliction status icons.

When extracting vanilla affliction icons, apply the icon's XML `color`/`iconcolors` tint or the user-requested target palette before saving the 24x24 PNG. Do not save raw grayscale mask icons unless the user explicitly asks for an uncolored source mask.

`devspace/scripts/build_statusicons_atlas/build_statusicons_atlas.py` builds `devspace/statusicons/atlas.png` from all status icon PNG files in `devspace/statusicons/`, excluding `atlas.png`. The script validates that each source icon is exactly 24x24 pixels and writes `statusicons.csv` with atlas coordinates in its own script directory.

### Barotrauma Mod Files
Everything outside `devspace` is part of the actual Barotrauma mod.

Do not store files outside `devspace` unless they are required for the mod to work in Barotrauma.

Expected mod-facing structure:

```text
filelist.xml
Items/
  Medical/
    icons.png
    sprites.png
    medical.xml
    poisons.xml
    buffs.xml
```

File meanings:

- `filelist.xml` - root Barotrauma mod descriptor.
- `Items/Medical` - Barotrauma item files for the medical part of the mod.
- `Items/Medical/icons.png` - atlas containing all final item icons.
- `Items/Medical/sprites.png` - atlas containing all final item sprites.
- `Items/Medical/medical.xml` - medical item definitions.
- `Items/Medical/poisons.xml` - poison item definitions.
- `Items/Medical/buffs.xml` - buff item definitions.

## Mod Build Workflow

Only run the mod build workflow when the user explicitly asks to build, rebuild, update atlases, update XML, or otherwise prepare the mod-facing Barotrauma files. Do not automatically build atlases, copy atlas files into `Items/Medical`, or edit mod XML after ordinary icon/sprite generation requests.

The main mod build script is:

```text
devspace/scripts/build_project/build_project.py
```

The script's README is:

```text
devspace/scripts/build_project/README.md
```

Build pipeline:

1. Validate final in-game item assets under `devspace/textures/*/items/*`.
2. Optionally overlay status icons from `devspace/statusicons` onto item icons.
3. Build final `icons.png` and `sprites.png` atlases and write `icons.csv` and `sprites.csv` coordinate maps.
4. Build item XML files from vanilla Barotrauma XML using `<Override><Items>...`.
5. Update the root `filelist.xml`.

Default outputs:

```text
Items/Medical/icons.png
Items/Medical/sprites.png
Items/Medical/medical.xml
Items/Medical/poisons.xml
Items/Medical/buffs.xml
devspace/scripts/build_project/icons.csv
devspace/scripts/build_project/sprites.csv
```

Validation-only command:

```powershell
python devspace/scripts/build_project/build_project.py --validate-only
```

Dry-run full build command:

```powershell
python devspace/scripts/build_project/build_project.py --all --dry-run
```

Full build command:

```powershell
python devspace/scripts/build_project/build_project.py --all
```

Important build flags:

- `--validate-only` - validate item assets without writing atlases, XML, or `filelist.xml`.
- `--all` - run the full build pipeline.
- `--dry-run` - print planned writes without writing files.
- `--strict` - treat warnings as errors.
- `--verbose` - print detailed item validation output.
- `--atlas-out DIR` - write `icons.png` and `sprites.png` to a custom directory.
- `--csv-out DIR` - write `icons.csv` and `sprites.csv` to a custom directory.
- `--xml` - build XML overrides without necessarily updating `filelist.xml`.
- `--filelist` - update root `filelist.xml`.
- `--vanilla-medical-dir PATH` - use a custom vanilla Barotrauma medical XML directory.
- `--textures-dir PATH` - use a custom generated texture directory. Default is `devspace/textures`.
- `--statusicons-dir PATH` - use a custom status icon directory. Default is `devspace/statusicons`.
- `--sprite-atlas-width PX` - preferred sprite atlas shelf width before multiple-of-4 padding. Default is `512`.

Status icon overlay:

- Use `--add-status-icons STATUS_CSV` to overlay status icons before item icon atlas packing.
- The CSV format is `identifier,statusicon`.
- `identifier` is the in-game item identifier, matching `devspace/textures/<asset>/items/<identifier>/`.
- `statusicon` is the status icon PNG stem in `devspace/statusicons`, for example `opiatewithdrawal` for `devspace/statusicons/opiatewithdrawal.png`.
- Status icons must be 24x24 PNG files.
- Status overlays are applied in memory for atlas building by default; they do not overwrite source item icons.
- Use `--save-status-icons [DIR]` with `--add-status-icons` to also save standalone 64x64 icons after overlay.
- If `--save-status-icons` is provided without a directory, save to `devspace/scripts/build_project/status_icons`.

XML build rules:

- Use Barotrauma `<Override>` wrappers, not `override="true"` attributes.
- Generated XML files must have this shape:

```xml
<Override>
  <Items>
    ...
  </Items>
</Override>
```

- Build XML from vanilla files in `D:\SteamLibrary\steamapps\common\Barotrauma\Content\Items\Medical` by default.
- Update each item's `InventoryIcon` texture to `%ModDir%/Items/Medical/icons.png` and its `sourcerect` from `icons.csv`.
- Update each item's `Sprite` texture to `%ModDir%/Items/Medical/sprites.png` and its `sourcerect` from `sprites.csv`.
- If an item is not found in vanilla XML, the build script may reuse an existing definition from `Items/Medical/*.xml` as a fallback.
- If an item is not found in either vanilla XML or existing mod XML, skip XML generation for that item with a warning; `--strict` turns this into an error.

Filelist rules:

- `filelist.xml` must include only mod-facing runtime files, not `devspace` files.
- Do not add PNG texture atlas files to `filelist.xml`; Barotrauma loads `icons.png` and `sprites.png` through XML texture references.
- Required item file entries are:

```text
%ModDir%/Items/Medical/medical.xml
%ModDir%/Items/Medical/poisons.xml
%ModDir%/Items/Medical/buffs.xml
```

Build safety:

- For ordinary icon/sprite generation requests, create or update only files under `devspace/textures` unless the user explicitly asks to build/update mod-facing files.
- Before running a real full build, prefer running `--all --dry-run` first and review warnings.
- Do not write generated status-overlay preview icons outside `devspace`.

## Icon Generation Rules

1. Strictly match the Barotrauma icon style.
2. Use the original Barotrauma icon atlases in `devspace/reference` as the primary visual reference.
3. Always generate or preserve a large source version first.
4. Create final `items/<identifier>/icon.png` files from `icon_source.png`.
5. Always keep `icon_source.png`; never keep only the final 64x64 icon.
6. Final icons must be 64x64 pixels.
7. The icon artwork itself must fit within a 60x60 pixel area inside the 64x64 file.
8. Icon artwork must be rotated 45 degrees clockwise.
9. Save the non-Barotrauma generation reference used for the icon as `origin.png` in the item's folder.

## Sprite Generation Rules

1. Strictly match the Barotrauma sprite style.
2. Use original Barotrauma sprites in `devspace/reference` as the primary visual reference.
3. Always generate or preserve a large source version first.
4. Create final `items/<identifier>/sprite.png` files from `sprite_source.png`.
5. Always keep `sprite_source.png`; never keep only the final in-game sprite.
6. Do not force final sprites into a 64x64 canvas; Barotrauma item sprites use their own rectangular `sourcerect` sizes.
7. Choose the final sprite size by comparing the item's silhouette and proportions against the observed `Medicines.png` sprite statistics, not by forcing one fixed size.
8. Treat the median medical sprite size, approximately 37x69 pixels, as a scale reference for typical narrow vertical medical items such as bottles, vials, ampoules, syringes, and injectors.
9. Choose sprite orientation from the physical shape of the item: use vertical orientation for tall or narrow items, and horizontal orientation for flat, wide, bag-like, strip-like, or pack-like items.
10. Keep the final sprite tightly cropped to the visible item with transparent padding only where needed for Barotrauma-style readability and atlas spacing.
11. Final sprite atlas textures must have width and height that are multiples of 4 pixels so Barotrauma can compress them without texture dimension warnings.
12. When changing a sprite's final dimensions, update the corresponding XML `Sprite` `sourcerect` to match the exact atlas rectangle.

## Sprite Reference Findings

The original Barotrauma medical item XML files in `D:\SteamLibrary\steamapps\common\Barotrauma\Content\Items\Medical` reference `Medicines.png` with per-item `Sprite` `sourcerect` rectangles.

Observed from `devspace/reference/Medicines.png`:

- The atlas size is 512x512 pixels.
- 42 medical `Sprite` rectangles reference `Medicines.png`.
- The average sprite size is approximately 39x64 pixels.
- The median sprite size is 37x69 pixels.
- The most common sprite size is 37x69 pixels.
- 39 of 42 medical sprites are vertical.
- 3 of 42 medical sprites are horizontal.
- Common vertical dimensions cluster around narrow, tall rectangles near the median rather than a single required size.
- Existing horizontal sprites are wider, tighter rectangles whose dimensions follow the item's silhouette rather than the vertical medical-item median.
- Sprite orientation is determined by the object's in-game shape, not by a fixed icon format.
- Use these values as references for scale, proportions, and orientation decisions during generation; do not treat them as a closed list of allowed sprite sizes.

## Agent Guidelines

- Keep development artifacts inside `devspace`.
- Keep the mod root clean and Barotrauma-ready.
- Before adding new root-level files, verify that Barotrauma needs them at runtime.
- Make visual changes to icons, sprites, and source images by regenerating the visual asset, not by manually editing or patching the bitmap.
- When adding a new item, create a dedicated folder under `devspace/textures`.
- When adding a new in-game item output, create `devspace/textures/<item>/items/<identifier>/` and store only that item's final `icon.png` and `sprite.png` there.
- When changing icon or sprite layout, update the relevant atlas and XML references together only if the user explicitly asked to build or update the mod-facing files.
