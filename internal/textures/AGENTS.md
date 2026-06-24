# Texture Asset Instructions

## Scope
This folder stores all item graphics and source files.

Each item asset set must have its own folder named after the icon/source asset identifier.

Example:

```text
internal/textures/insulin_syringe/
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

## File Meanings
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

The folder names under `internal/textures/<item>/items/` are the in-game item identifiers. Final icon and sprite files that will be used by the game must be stored only in these identifier folders. Root-level `icon.png` and `sprite.png` files in an item asset folder are important preview/scaffold files, but they are not used in game.

When adding a new item, create a dedicated folder under `internal/textures`.

When adding a new in-game item output, create `internal/textures/<item>/items/<identifier>/` and store only that item's final `icon.png` and `sprite.png` there.
