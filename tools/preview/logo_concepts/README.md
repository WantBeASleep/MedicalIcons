# Logo Concepts

## Purpose

Generates animated 268x268 GIF logo concepts for the Medical Icons workshop preview.

## Usage

```powershell
python tools/preview/logo_concepts/logo_concepts.py
```

Preview the planned outputs without writing files:

```powershell
python tools/preview/logo_concepts/logo_concepts.py --dry-run
```

## Options

- `--dry-run` prints the GIF files that would be generated without writing them.
- `--output-dir DIR` writes GIFs to a custom project-relative or absolute folder.

## Inputs and outputs

Inputs are read from `source/textures/**/icon.png`.

Outputs are written to `preview/logo_concepts` by default:

- `medical_icons_logo_01_carousel.gif`
- `medical_icons_logo_02_scanner.gif`
- `medical_icons_logo_03_before_after.gif`
- `medical_icons_logo_04_medkit_burst.gif`
- `medical_icons_logo_05_liquid_pulse.gif`

## Notes

The script uses Pillow and computes paths from the project root marker `filelist.xml`.
