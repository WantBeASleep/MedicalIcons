# Item XML Override Builder

`update_item_overrides.py` rebuilds mod-facing XML overrides for every generated item asset.

The script discovers overridden item identifiers from:

```text
devspace/items/<item>/items/<identifier>/
```

It reads atlas coordinates from:

```text
devspace/scripts/item_atlases/icons.csv
devspace/scripts/item_atlases/sprites.csv
```

For every discovered identifier, it finds the vanilla Barotrauma item definition under `Content/Items`, copies that definition into an `Override`, and updates:

- `InventoryIcon` to use `%ModDir%/Items/Medical/icons.png`.
- `Sprite` to use `%ModDir%/Items/Medical/sprites.png`.

Other vanilla item behavior is preserved.

## Output

The script writes one mod XML file per vanilla source XML file into:

```text
Items/Medical/
```

For example, vanilla `Content/Items/Medical/medical.xml` becomes:

```text
Items/Medical/medical.xml
```

The script also adds the generated XML files to `filelist.xml` if they are missing.

## Safety Checks

- Each discovered item must have matching entries in both atlas CSV files.
- Each in-game identifier may appear in only one generated asset folder.
- Each identifier must resolve to exactly one vanilla top-level item definition.

If any of these checks fail, the script exits without writing partial XML overrides.

## Usage

Run after rebuilding item atlases:

```powershell
python devspace/scripts/update_item_overrides/update_item_overrides.py
```
