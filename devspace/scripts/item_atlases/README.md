# Item Atlases Builder

`build_item_atlases.py` builds the Barotrauma mod icon and sprite atlases from item folders in `devspace/items`.

The script writes PNG atlases into the mod runtime folder and writes CSV coordinate maps next to the script.

## Input

Each item is read from a dedicated folder:

```text
devspace/items/<item_identifier>/
  icon.png
  sprite.png
```

Folders are processed in alphabetical order by folder name. The folder name is used as the item `identifier` in the CSV files.

Items without `icon.png` are skipped for the icon atlas. Items without `sprite.png` are skipped for the sprite atlas.

## Output

Default PNG atlas output:

```text
Items/Medical/Icons.png
Items/Medical/Sprites.png
```

Default CSV map output:

```text
devspace/scripts/item_atlases/Icons.csv
devspace/scripts/item_atlases/Sprites.csv
```

The CSV files are development/build artifacts. They are intentionally kept next to the script instead of in `Items/Medical`.

## Usage

Run from the mod root:

```powershell
python devspace\scripts\item_atlases\build_item_atlases.py
```

If the system `python` command is not available, run the script with any Python installation that has Pillow installed.

## CSV Columns

Each CSV row describes one image inside the generated atlas.

```text
identifier,x,y,width,height,sourcerect
```

- `identifier` - item folder name from `devspace/items`.
- `x`, `y`, `width`, `height` - atlas rectangle values.
- `sourcerect` - ready-to-copy Barotrauma rectangle in `x,y,width,height` format.

Example:

```csv
identifier,x,y,width,height,sourcerect
insulin_syringe,0,0,64,64,"0,0,64,64"
```

Use the `sourcerect` value in XML:

```xml
<InventoryIcon texture="%ModDir%/Items/Medical/Icons.png" sourcerect="0,0,64,64" />
<Sprite texture="%ModDir%/Items/Medical/Sprites.png" sourcerect="0,0,15,98" />
```

## Options

```powershell
python devspace\scripts\item_atlases\build_item_atlases.py `
  --items-dir devspace\items `
  --output-dir Items\Medical `
  --csv-dir devspace\scripts\item_atlases `
  --atlas-width 512 `
  --padding 2
```

- `--items-dir` - item source folder. Default: `devspace/items`.
- `--output-dir` - folder where `Icons.png` and `Sprites.png` are written. Default: `Items/Medical`.
- `--csv-dir` - folder where CSV maps are written. Default: the script folder.
- `--icon-atlas-name` - icon atlas filename. Default: `Icons.png`.
- `--sprite-atlas-name` - sprite atlas filename. Default: `Sprites.png`.
- `--icon-csv-name` - icon CSV filename. Default: `Icons.csv`.
- `--sprite-csv-name` - sprite CSV filename. Default: `Sprites.csv`.
- `--atlas-width` - maximum atlas row width in pixels. Default: `512`.
- `--padding` - transparent spacing between packed images. Default: `2`.

## Packing Rules

The script uses simple row packing:

1. Images are placed left to right.
2. If the next image does not fit within `--atlas-width`, a new row starts.
3. The atlas is cropped to the smallest size that contains all placed images.
4. Image dimensions are preserved exactly; sprites are not forced into a fixed canvas.

After changing generated atlas coordinates, update the matching XML `sourcerect` values using the CSV maps.
