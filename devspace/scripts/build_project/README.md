# build_project

Build script for the Medical Icons Barotrauma local mod.

The script validates generated item assets, optionally overlays status icons on item icons, builds item atlases, writes atlas CSV maps, rebuilds XML overrides, and updates the root `filelist.xml`.

## Location

```text
devspace/scripts/build_project/build_project.py
```

## Pipeline

1. Validate item assets in `devspace/textures/*/items/*`.
2. Optionally overlay status icons from `devspace/statusicons`.
3. Build `icons.png` and `sprites.png` atlases, plus `icons.csv` and `sprites.csv`.
4. Build item XML files from vanilla Barotrauma XML using `<Override><Items>...`, updating visual references and `Body` size from the generated sprite.
5. Update root `filelist.xml`.

## Basic Usage

Validate only:

```powershell
python devspace/scripts/build_project/build_project.py --validate-only
```

Dry-run full build with status icon overlays:

```powershell
python devspace/scripts/build_project/build_project.py --all --dry-run
```

Full build with status icon overlays:

```powershell
python devspace/scripts/build_project/build_project.py --all
```

## Status Icon Overlay

CSV format:

```csv
identifier,statusicon
antidama1,opiatewithdrawal
hyperzine,haste
```

Status icons are overlaid during atlas build by default. The default mapping file is:

```text
devspace/scripts/build_project/statusicons.csv
```

Use a custom mapping file:

```powershell
python devspace/scripts/build_project/build_project.py --all --add-status-icons devspace/statusicon_map.csv
```

Build without status icon overlays:

```powershell
python devspace/scripts/build_project/build_project.py --all --disable-staus-icons
```

Also save standalone 64x64 icons with status overlays:

```powershell
python devspace/scripts/build_project/build_project.py --all --add-status-icons devspace/statusicon_map.csv --save-status-icons
```

Save them to a specific directory:

```powershell
python devspace/scripts/build_project/build_project.py --all --add-status-icons devspace/statusicon_map.csv --save-status-icons devspace/scripts/build_project/status_icons
```

## XML Rules

When building XML, the script updates each item's `InventoryIcon`, `Sprite`, and `Body` dimensions from the generated atlases.

Items generated from these texture asset folders also get `holdangle="10"` on their `MeleeWeapon` or `Holdable` component:

```text
devspace/textures/ampoule
devspace/textures/pocket_injector
devspace/textures/vial
```

## Flags

```text
--validate-only
```

Only validate item assets. Does not write atlases, XML, or `filelist.xml`.

```text
--add-status-icons STATUS_CSV
```

Read `identifier,statusicon` mappings and overlay status icons onto matching item icons before atlas packing.

Default:

```text
devspace/scripts/build_project/statusicons.csv
```

When status icon overlays are enabled, this CSV must exist. If the CSV does not contain a row for a discovered item, the script emits a warning and packs that item's icon without an overlay.

```text
--disable-staus-icons
```

Build item icon atlases without status icon overlays.

```text
--save-status-icons [DIR]
```

Save standalone item icons after status icon overlay.

If `DIR` is omitted, output goes to:

```text
devspace/scripts/build_project/status_icons
```

```text
--atlas-out DIR
```

Directory for `icons.png` and `sprites.png`.

Default:

```text
Items/Medical
```

```text
--csv-out DIR
```

Directory for `icons.csv` and `sprites.csv`.

Default:

```text
devspace/scripts/build_project
```

```text
--xml
```

Build `Items/Medical/medical.xml`, `Items/Medical/poisons.xml`, and `Items/Medical/buffs.xml`.

XML output uses:

```xml
<Override>
  <Items>
    ...
  </Items>
</Override>
```

```text
--filelist
```

Update root `filelist.xml` with required mod-facing files.

```text
--all
```

Run the full pipeline.

```text
--vanilla-medical-dir PATH
```

Path to vanilla Barotrauma medical XML files.

Default:

```text
D:/SteamLibrary/steamapps/common/Barotrauma/Content/Items/Medical
```

```text
--textures-dir PATH
```

Path to generated item texture folders.

Default:

```text
devspace/textures
```

```text
--statusicons-dir PATH
```

Path to 24x24 status icon PNG files.

Default:

```text
devspace/statusicons
```

```text
--sprite-atlas-width PX
```

Preferred sprite atlas shelf width before final multiple-of-4 padding.

Default:

```text
512
```

```text
--dry-run
```

Print planned writes without writing files.

```text
--strict
```

Treat warnings as errors.

```text
--verbose
```

Print detailed validation output for every item.

## Notes

- Final item assets are discovered only from `devspace/textures/<asset>/items/<identifier>/`.
- Root-level `icon.png` and `sprite.png` inside an asset folder are previews and are not packed.
- Status icons must be 24x24 PNG files.
- Item icons must be 64x64 PNG files.
- Sprite atlas dimensions are padded to multiples of 4.
- XML is generated from vanilla XML first. If an item does not exist in vanilla XML, the script tries to reuse an existing item definition from `Items/Medical/*.xml`.
- Generated XML updates each item's `Body width` and `Body height` to match the generated sprite dimensions.
- Items not found in vanilla XML or existing mod XML are skipped during XML generation with a warning. Use `--strict` to make that an error.
