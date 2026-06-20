# Antidote Vial Recolor

`recolor_vial_antidotes.py` generates antidote vial item assets from the base vial artwork.

The script reads:

```text
devspace/items/vial/icon_source.png
devspace/items/vial/sprite.png
devspace/items/vial/masks/mask_source_*.png
```

It uses the vial masks to recolor cap metal, cap rubber, optional cap edge, optional label regions, and the glass/liquid area for each supported antidote identifier.

## Output

- Final in-game assets at `devspace/items/vial/items/<identifier>/icon.png`.
- Final in-game assets at `devspace/items/vial/items/<identifier>/sprite.png`.
- Recolored large icon sources in `devspace/items/vial/antidote_icon_sources/`.
- Mask preview images and `devspace/items/vial/antidote_vial_preview.png` for visual checking.

## Usage

Run from the project root:

```powershell
python devspace/scripts/recolor_vial_antidotes/recolor_vial_antidotes.py
```
