# build_project

Build script for the Medical Icons Barotrauma local Lua mod.

The script validates generated item assets, optionally overlays status icons on item icons, builds item icon and sprite atlases, and writes generated Lua atlas metadata to `lua/limanchel/medical_icons/generated/atlases.lua`.

## Location

```text
devspace/scripts/build_project/build_project.py
```

## Pipeline

1. Validate item assets in `devspace/textures/*/items/*`.
2. Optionally overlay status icons from `devspace/statusicons`.
3. Build `assets/icons.png` and `assets/sprites.png`.
4. Generate `lua/limanchel/medical_icons/generated/atlases.lua`.

The build script does not edit `lua/limanchel/medical_icons/data.lua`. Keep manual runtime constants there, such as `holdAngle`, origins, rotation, depth, and item-specific overrides.

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

## Generated Lua

`atlases.lua` is fully generated and may be overwritten on every build.

Shape:

```lua
local atlases = {
    assets = {
        icons = "assets/icons.png",
        sprites = "assets/sprites.png",
    },

    items = {
        ["adrenaline"] = {
            texture = "ampoule",
            icon = { rect = { 0, 0, 64, 64 } },
            sprite = { rect = { 0, 0, 9, 44 } },
        },
    },
}

return atlases
```

`texture` comes from `devspace/textures/<texture>/items/<identifier>`.

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
python devspace/scripts/build_project/build_project.py --all --disable-status-icons
```

Also save standalone 64x64 icons with status overlays:

```powershell
python devspace/scripts/build_project/build_project.py --all --add-status-icons devspace/statusicon_map.csv --save-status-icons
```

Save them to a specific directory:

```powershell
python devspace/scripts/build_project/build_project.py --all --add-status-icons devspace/statusicon_map.csv --save-status-icons devspace/scripts/build_project/status_icons
```

## Flags

```text
--validate-only
```

Only validate item assets. Does not write atlases or Lua metadata.

```text
--add-status-icons STATUS_CSV
```

Read `identifier,statusicon` mappings and overlay status icons onto matching item icons before atlas packing.

```text
--disable-status-icons
```

Build item icon atlases without status icon overlays.

The legacy misspelled `--disable-staus-icons` spelling is still accepted.

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
assets
```

```text
--atlases-lua FILE
```

Path for generated Lua atlas metadata.

Default:

```text
lua/limanchel/medical_icons/generated/atlases.lua
```

```text
--all
```

Run validation, atlas build, and `atlases.lua` generation.

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

- Final item assets are discovered only from `devspace/textures/<texture>/items/<identifier>/`.
- Root-level `icon.png` and `sprite.png` inside a texture folder are previews and are not packed.
- Status icons must be 24x24 PNG files.
- Item icons must be 64x64 PNG files.
- Sprite atlas dimensions are padded to multiples of 4.
- The script no longer generates CSV atlas maps or XML overrides.
- After each run, Python cache artifacts under the mod workspace are removed.
