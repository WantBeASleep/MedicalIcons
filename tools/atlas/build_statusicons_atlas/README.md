# Status Icon Atlas Builder

`build_statusicons_atlas.py` builds a PNG atlas from individual status icon PNG files.

The script reads 24x24 source icons from:

```text
source/status_icons/
```

It ignores `atlas.png`, validates that every source icon is exactly 24x24 pixels, and writes:

- `assets/status_icons.png`
- `tools/atlas/build_statusicons_atlas/statusicons.csv`

The CSV contains `name`, `source`, `x`, `y`, `width`, `height`, and `sourcerect`.

## Usage

Run from the project root:

```powershell
python tools/atlas/build_statusicons_atlas/build_statusicons_atlas.py
```
