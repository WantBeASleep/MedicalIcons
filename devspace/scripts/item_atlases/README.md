# Item Atlas Builder

`build_item_atlases.py` builds development atlases from final per-item assets.

The script scans:

```text
devspace/items/<item>/items/<identifier>/
```

Each identifier folder must contain:

```text
icon.png
sprite.png
```

## Output

The script writes four files into this directory:

- `icons.png` - icon atlas built from all `icon.png` files.
- `sprites.png` - sprite atlas built from all `sprite.png` files.
- `icons.csv` - icon atlas coordinates and source item identifiers.
- `sprites.csv` - sprite atlas coordinates and source item identifiers.

CSV columns:

```csv
item,identifier,source,x,y,width,height,sourcerect
```

`sourcerect` is formatted for Barotrauma XML as:

```text
x,y,width,height
```

## Rules

- Icons must be `64x64`.
- Individual source sprite files keep their own dimensions.
- During atlas generation, each sprite is copied into a transparent rectangle whose width and height are rounded up to multiples of 4.
- The generated `sprites.png` atlas is also padded so its total width and height are multiples of 4.
- `sprites.csv` stores the padded atlas rectangle for each sprite. This means `sourcerect` may include transparent padding on the right or bottom.

## Usage

Run from the project root:

```powershell
python devspace/scripts/item_atlases/build_item_atlases.py
```
