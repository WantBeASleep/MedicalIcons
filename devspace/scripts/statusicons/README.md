# Status Icon Atlas Builder

`build_status_icons.py` builds the Barotrauma status icon atlas from individual affliction icons.

The script scans:

```text
devspace/statusicons/*.png
```

It ignores `devspace/statusicons/atlas.png`, validates that every source icon is exactly `24x24`, then places the icons into a transparent atlas.

## Output

The script writes:

```text
devspace/statusicons/atlas.png
```

## Usage

Run from the project root:

```powershell
python devspace/scripts/statusicons/build_status_icons.py
```
