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
  paint.net/
  preview/
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

#### `devspace/paint.net`
Stores development-only paint.net files used for visual editing work.

Use this folder for `.pdn` working files and other paint.net-specific visual sources. Files in this folder are not used by Barotrauma at runtime and must not be copied into mod-facing folders or added to `filelist.xml`.

#### Script Storage Rules
Store scripts based on their scope.

Global scripts belong under `devspace/scripts`. A script is global when it works on the whole mod, builds or validates the project, creates shared atlases, updates XML/filelist data, or performs similar project-wide automation.

Local scripts belong in a `scripts` folder next to the files or folder tree they operate on. A script is local when it exists for one small, specific task or one narrow asset area. For example, preview-only scripts belong under `devspace/preview/scripts`, and one-texture helper scripts belong under `devspace/textures/<item>/scripts`.

Do not place one-off or narrow local helper scripts in the top-level `devspace/scripts`.

#### `devspace/preview`
Stores development-only preview images for the mod, such as Steam Workshop preview images, item showcase images, before/after comparison images, and generated visual review sheets.

Preview files are not used by Barotrauma at runtime. Do not copy preview images into mod-facing folders and do not add them to `filelist.xml`.

Expected structure:

```text
devspace/preview/
  scripts/
  source/
  <preview_name>.png
```

#### `devspace/preview/scripts`
Stores preview-only scripts, such as Steam Workshop preview generators and small preview-specific helpers.

#### `devspace/preview/source`
Stores source images used to generate finished Steam Workshop preview images.

Files in this folder are preview-generation inputs only. They are not final Steam Workshop images, are not used by Barotrauma at runtime, and must not be added to `filelist.xml`.

Preview image rules:

- Keep only finished Steam Workshop preview images directly inside `devspace/preview`.
- Keep source images used for preview generation inside `devspace/preview/source`.
- Use 1920x1080 PNG files for Steam Workshop preview images unless the user explicitly requests another size.
- Preview images may compose existing item icons, sprites, status icons, backgrounds, labels, and other development-only visual elements.

#### `devspace/scripts`
Stores development-only automation scripts for the whole project, build pipeline, validation, atlas generation, XML generation, filelist updates, or similar project-wide tasks.

- `build_project.py` - validates generated item assets, overlays status icons by default, builds final item icon/sprite atlases, writes atlas coordinate CSV files, rebuilds medical XML overrides, and updates root `filelist.xml`.

#### `devspace/statusicons`
Stores Barotrauma status affliction icons.

Expected structure:

```text
devspace/statusicons/
  <affliction_name>.png
```

File meanings:

- `<affliction_name>.png` - individual Barotrauma affliction status icon, 24x24 pixels.

When extracting vanilla affliction icons, apply the icon's XML `color`/`iconcolors` tint or the user-requested target palette before saving the 24x24 PNG. Do not save raw grayscale mask icons unless the user explicitly asks for an uncolored source mask.

### Barotrauma Mod Files
Everything outside `devspace` is mod-facing or publishing-facing.

Do not store files outside `devspace` unless they are required for the mod to work in Barotrauma.

Expected mod-facing structure:

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

File meanings:

- `filelist.xml` - root Barotrauma mod descriptor.
- `workshop_description_en.bbcode` - English Steam Workshop description, similar to a Workshop-facing README.
- `workshop_description_ru.bbcode` - Russian Steam Workshop description, similar to a Workshop-facing README.
- `Items/Medical` - Barotrauma item files for the medical part of the mod.
- `Items/Medical/Icons.png` - atlas containing all final item icons.
- `Items/Medical/Sprites.png` - atlas containing all final item sprites.
- `Items/Medical/medical.xml` - medical item definitions.
- `Items/Medical/poisons.xml` - poison item definitions.
- `Items/Medical/buffs.xml` - buff item definitions.

## Mod Build Workflow

Run the mod build workflow whenever a project change affects the future runtime build of the mod. This includes changes to final item icons or sprites under `devspace/textures/*/items/*`, status icon overlay inputs, build scripts, XML generation rules, atlas packing behavior, or any other source that changes the generated `Items/Medical` outputs.

Do not run the mod build workflow for changes that only affect documentation, `devspace/preview`, `devspace/paint.net`, Steam Workshop descriptions, or other publishing/development-only files unless the user explicitly asks to rebuild.

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
2. Overlay status icons from `devspace/statusicons` onto item icons by default.
3. Build final `Icons.png` and `Sprites.png` atlases and write `icons.csv` and `sprites.csv` coordinate maps.
4. Build item XML files from vanilla Barotrauma XML using `<Override><Items>...`.
5. Update the root `filelist.xml`.

Default outputs:

```text
Items/Medical/Icons.png
Items/Medical/Sprites.png
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
- `--atlas-out DIR` - write `Icons.png` and `Sprites.png` to a custom directory.
- `--csv-out DIR` - write `icons.csv` and `sprites.csv` to a custom directory.
- `--xml` - build XML overrides without necessarily updating `filelist.xml`.
- `--filelist` - update root `filelist.xml`.
- `--vanilla-medical-dir PATH` - use a custom vanilla Barotrauma medical XML directory.
- `--textures-dir PATH` - use a custom generated texture directory. Default is `devspace/textures`.
- `--statusicons-dir PATH` - use a custom status icon directory. Default is `devspace/statusicons`.
- `--sprite-atlas-width PX` - preferred sprite atlas shelf width before multiple-of-4 padding. Default is `512`.

Status icon overlay:

- Status icons are overlaid before item icon atlas packing by default.
- The default status icon mapping file is `devspace/scripts/build_project/statusicons.csv`.
- Use `--add-status-icons STATUS_CSV` to override the default status icon mapping CSV.
- Use `--disable-status-icons` to build item icon atlases without status icon overlays.
- The CSV format is `identifier,statusicon`.
- `identifier` is the in-game item identifier, matching `devspace/textures/<asset>/items/<identifier>/`.
- `statusicon` is the status icon PNG stem in `devspace/statusicons`, for example `opiatewithdrawal` for `devspace/statusicons/opiatewithdrawal.png`.
- Status icons must be 24x24 PNG files.
- Status overlays are applied in memory for atlas building by default; they do not overwrite source item icons.
- Use `--save-status-icons [DIR]` to also save standalone 64x64 icons after overlay.
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
- Update each item's `InventoryIcon` texture to `%ModDir%/Items/Medical/Icons.png` and its `sourcerect` from `icons.csv`.
- Update each item's `Sprite` texture to `%ModDir%/Items/Medical/Sprites.png` and its `sourcerect` from `sprites.csv`.
- If an item is not found in vanilla XML, the build script may reuse an existing definition from `Items/Medical/*.xml` as a fallback.
- If an item is not found in either vanilla XML or existing mod XML, skip XML generation for that item with a warning; `--strict` turns this into an error.

Filelist rules:

- `filelist.xml` must include only mod-facing runtime files, not `devspace` files.
- Do not add PNG texture atlas files to `filelist.xml`; Barotrauma loads `Icons.png` and `Sprites.png` through XML texture references.
- Required item file entries are:

```text
%ModDir%/Items/Medical/medical.xml
%ModDir%/Items/Medical/poisons.xml
%ModDir%/Items/Medical/buffs.xml
```

Build safety:

- Before running a real full build, run `--all --dry-run` first and review warnings.
- If a change affects the future runtime build, follow the dry-run with a real full build unless the dry-run reveals a problem that should be fixed first.
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
- After running any Python script, remove all generated `__pycache__` folders and `.pyc` files from the mod workspace. The mod may be published to Steam Workshop with source files included, and Workshop publishing does not use `.gitignore` to exclude Python cache artifacts.
- When adding a new item, create a dedicated folder under `devspace/textures`.
- When adding a new in-game item output, create `devspace/textures/<item>/items/<identifier>/` and store only that item's final `icon.png` and `sprite.png` there.
- When changing icon or sprite layout, update the relevant atlas and XML references together only if the user explicitly asked to build or update the mod-facing files.
