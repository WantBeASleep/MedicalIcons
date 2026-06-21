# Antidote Vial Recolor

`recolor_vial_antidotes.py` generates antidote vial item assets from the base vial artwork.

The script reads:

```text
devspace/textures/vial/icon_source.png
devspace/textures/vial/sprite.png
devspace/textures/vial/masks/mask_source_*.png
```

It uses the vial masks to recolor cap metal, cap rubber, optional cap edge, optional label regions, and the glass/liquid area for each supported antidote identifier.

## Output

- Final in-game assets at `devspace/textures/vial/items/<identifier>/icon.png`.
- Final in-game assets at `devspace/textures/vial/items/<identifier>/sprite.png`.
- Recolored large icon sources in `devspace/textures/vial/antidote_icon_sources/`.
- Mask preview images and `devspace/textures/vial/antidote_vial_preview.png` for visual checking.

## Usage

Run from the project root:

```powershell
python devspace/textures/vial/scripts/recolor_vial_antidotes.py
```
