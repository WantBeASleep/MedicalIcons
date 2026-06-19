# Project Notes

## Overview
This project is a Barotrauma local mod named `Medical Icons`.

The mod contains medical item icons, sprites, source images, and build assets.
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
  items/
  mapping.csv
  reference/
  scripts/
```

#### `devspace/items`
Stores all item graphics and source files.

Each item must have its own folder named after the icon/item identifier.

Example:

```text
devspace/items/insulin_syringe/
```

Each item folder contains exactly these five files:

```text
origin.png
icon_source.png
icon.png
sprite_source.png
sprite.png
```

File meanings:

- `origin.png` - generation reference image used to create the item icon; this is not an original Barotrauma style reference.
- `icon_source.png` - large high-resolution source image for the icon.
- `icon.png` - final 64x64 icon.
- `sprite_source.png` - large high-resolution source image for the sprite.
- `sprite.png` - final sprite displayed in game.

#### `devspace/reference`
Stores original Barotrauma sprites and icons used as visual references.

Use this folder when matching the original Barotrauma icon and sprite style.

#### `devspace/scripts`
Stores scripts used to build or package the mod.

All scripts must be written strictly in Python.

Each script must live in its own dedicated subfolder inside `devspace/scripts`.

Examples include scripts that combine icons into `Icons.png` and sprites into `Sprites.png` atlases so Barotrauma can reference individual assets from them.

#### `devspace/mapping.csv`
Stores the mapping between original Barotrauma item identifiers and replacement mod item identifiers.

Use only identifiers in this file; do not store paths.

Expected columns:

```csv
original_identifier,mod_identifier
```

Whenever XML files are updated to replace an original game item with a mod item, update `devspace/mapping.csv` in the same change so it remains the source of truth for item replacement mappings.

### Barotrauma Mod Files
Everything outside `devspace` is part of the actual Barotrauma mod.

Do not store files outside `devspace` unless they are required for the mod to work in Barotrauma.

Expected mod-facing structure:

```text
filelist.xml
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
- `Items/Medical` - Barotrauma item files for the medical part of the mod.
- `Items/Medical/Icons.png` - atlas containing all final item icons.
- `Items/Medical/Sprites.png` - atlas containing all final item sprites.
- `Items/Medical/medical.xml` - medical item definitions.
- `Items/Medical/poisons.xml` - poison item definitions.
- `Items/Medical/buffs.xml` - buff item definitions.

## Atlas Build Rules

All icon and sprite atlas builds must be done only through:

```text
devspace/scripts/item_atlases/build_item_atlases.py
```

Do not manually assemble, edit, or replace `Items/Medical/Icons.png` or `Items/Medical/Sprites.png` outside this script.

The atlas build script writes the final runtime atlases to:

```text
Items/Medical/Icons.png
Items/Medical/Sprites.png
```

The atlas build script writes coordinate maps next to the script:

```text
devspace/scripts/item_atlases/Icons.csv
devspace/scripts/item_atlases/Sprites.csv
```

`Icons.csv` and `Sprites.csv` store the required item names and atlas coordinates. Each row maps an item identifier to its generated `sourcerect` values for the corresponding icon or sprite atlas.

## Icon Generation Rules

1. Strictly match the Barotrauma icon style.
2. Use the original Barotrauma icon atlases in `devspace/reference` as the primary visual reference.
3. Always generate or preserve a large source version first.
4. Create the final `icon.png` from `icon_source.png`.
5. Always keep `icon_source.png`; never keep only the final 64x64 icon.
6. Final icons must be 64x64 pixels.
7. The icon artwork itself must fit within a 60x60 pixel area inside the 64x64 file.
8. Icon artwork must be rotated 45 degrees clockwise.
9. Save the non-Barotrauma generation reference used for the icon as `origin.png` in the item's folder.

## Sprite Generation Rules

1. Strictly match the Barotrauma sprite style.
2. Use original Barotrauma sprites in `devspace/reference` as the primary visual reference.
3. Always generate or preserve a large source version first.
4. Create the final `sprite.png` from `sprite_source.png`.
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
- Prefer scripts in `devspace/scripts` for repeatable atlas generation and packaging.
- Write all scripts strictly in Python.
- Store each script in its own dedicated folder under `devspace/scripts`; do not place standalone script files directly in `devspace/scripts`.
- Build `Items/Medical/Icons.png` and `Items/Medical/Sprites.png` only by running `devspace/scripts/item_atlases/build_item_atlases.py`.
- Make visual changes to icons, sprites, and source images by regenerating the visual asset, not by manually editing or patching the bitmap.
- When adding a new item, create a dedicated folder under `devspace/items`.
- When changing icon or sprite layout, update the relevant atlas and XML references together.
- When changing XML item replacements, update `devspace/mapping.csv` together with the XML change.
