# Preview GIF Builder

## Purpose

Builds an animated Workshop preview GIF from the archived static preview images in `preview/legacy`.

## Usage

```powershell
python tools/preview/build_preview_gif.py
```

Preview the planned inputs and output without writing:

```powershell
python tools/preview/build_preview_gif.py --dry-run
```

Create a larger GIF:

```powershell
python tools/preview/build_preview_gif.py --width 1280 --height 720
```

## Options

- `--input-dir` - source PNG directory, defaulting to `preview/legacy`.
- `--output` - output GIF path, defaulting to `preview/medical_icons_preview.gif`.
- `--width` - output GIF width in pixels.
- `--height` - output GIF height in pixels.
- `--duration` - duration of each content slide in milliseconds.
- `--transition-frames` - number of crossfade frames between slides.
- `--dry-run` - print planned work without writing files.

## Inputs And Outputs

Reads the existing PNG preview images from `preview/legacy`.

Writes `preview/medical_icons_preview.gif` by default.

## Notes

The script uses Pillow, matching the image dependency already used by the project build script.
