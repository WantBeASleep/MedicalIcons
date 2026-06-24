# Antidote Vial Recolor

`recolor_vial_antidotes.py` generates antidote vial item assets from the base vial artwork.

The script reads:

```text
internal/textures/vial/icon_source.png
internal/textures/vial/sprite.png
internal/textures/vial/masks/mask_source_*.png
```

It uses the vial masks to recolor cap metal, cap rubber, optional cap edge, optional label regions, and the glass/liquid area for each supported antidote identifier.

## Output

- Final in-game assets at `internal/textures/vial/items/<identifier>/icon.png`.
- Final in-game assets at `internal/textures/vial/items/<identifier>/sprite.png`.
- Recolored large icon sources in `internal/textures/vial/antidote_icon_sources/`.
- Mask preview images and `internal/textures/vial/antidote_vial_preview.png` for visual checking.

## Usage

Run from the project root:

```powershell
python internal/textures/vial/scripts/recolor_vial_antidotes.py
```
