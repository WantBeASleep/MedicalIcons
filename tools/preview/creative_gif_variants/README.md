# Creative GIF Preview Variants

## Purpose

Builds multiple 268x268 animated GIF concepts for the `Medical Icons` Workshop preview.

The variants compare the vanilla syringe-like item icon on the left with the modded replacement icon on the right. Each GIF cycles through morphine, adrenaline, cyanide, calyxanide, and methamphetamine with large Bangers title and item labels.

## Usage

```powershell
python tools/preview/creative_gif_variants/build_creative_gif_variants.py
```

Preview planned outputs without writing:

```powershell
python tools/preview/creative_gif_variants/build_creative_gif_variants.py --dry-run
```

Render slower item beats:

```powershell
python tools/preview/creative_gif_variants/build_creative_gif_variants.py --frames-per-item 18 --duration 58
```

## Options

- `--output-dir` - directory for generated GIFs and contact sheet, defaulting to `preview/creative_gif_variants`.
- `--frames-per-item` - animation frames rendered before advancing to the next item.
- `--duration` - GIF frame duration in milliseconds.
- `--dry-run` - print planned output files without writing images.

## Inputs And Outputs

Reads vanilla atlas images from the local Barotrauma install and modded item icons from `source/textures`.

Writes:

- `preview/creative_gif_variants/01_barotrauma_sonar.gif`
- `preview/creative_gif_variants/02_neon_snap.gif`
- `preview/creative_gif_variants/03_comic_shake.gif`
- `preview/creative_gif_variants/04_lab_carousel.gif`
- `preview/creative_gif_variants/05_toxic_glitch.gif`
- `preview/creative_gif_variants/06_clean_shop.gif`
- `preview/creative_gif_variants/07_v2_medbay_panel.gif`
- `preview/creative_gif_variants/08_v2_emergency_red.gif`
- `preview/creative_gif_variants/09_v2_inventory_slots.gif`
- `preview/creative_gif_variants/10_v2_abyss_bio.gif`
- `preview/creative_gif_variants/11_v2_xray_lab.gif`
- `preview/creative_gif_variants/12_v2_pop_halftone.gif`
- `preview/creative_gif_variants/13_v2_sonar_snap.gif`
- `preview/creative_gif_variants/contact_sheet.png`

## Notes

The script resolves paths from its own location and the project root marker `filelist.xml`. It does not hard-code the project directory.
