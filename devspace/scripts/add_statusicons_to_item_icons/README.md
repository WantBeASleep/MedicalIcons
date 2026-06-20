# Item Icon Status Overlay

`add_statusicons_to_item_icons.py` overlays affliction/status icons onto generated item icons.

The script reads `input.csv` from this directory by default. Each row maps an in-game item identifier to a status icon:

```csv
identifier,statusicon
cyanide,poison
radiotoxin,radiationsickness
```

`statusicon` values refer to PNG files under:

```text
devspace/statusicons/
```

The `.png` extension may be omitted.

## Output

For each row, the script finds:

```text
devspace/items/<item>/items/<identifier>/icon.png
```

It overlays the `24x24` status icon at the top-left corner and writes a new icon in the same identifier directory:

```text
icon<postfix>.png
```

For example, `--output_postfix "_statusicon"` writes:

```text
icon_statusicon.png
```

## Usage

Run from the project root:

```powershell
python devspace/scripts/add_statusicons_to_item_icons/add_statusicons_to_item_icons.py --output_postfix "_statusicon"
```

Use another CSV file:

```powershell
python devspace/scripts/add_statusicons_to_item_icons/add_statusicons_to_item_icons.py --input devspace/scripts/add_statusicons_to_item_icons/input.csv --output_postfix "_statusicon"
```
