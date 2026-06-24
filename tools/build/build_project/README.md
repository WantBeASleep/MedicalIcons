# build_project

Build script for the Medical Icons Barotrauma local Lua mod.

The script validates generated item assets, optionally overlays status icons on item icons, builds item icon and sprite atlases, and writes generated Lua atlas metadata to `Lua/limanchel/medical_icons/generated/atlases.lua`.

## Purpose

Use this script after changing item icon or sprite sources under `source/textures`, status icon sources under `source/status_icons`, or atlas generation behavior. A normal run performs the full build by default.

## Location

```text
tools/build/build_project/build_project.py
```

## Pipeline

1. Validate item assets in `source/textures/*/items/*`.
2. Optionally overlay status icons from `source/status_icons`.
3. Build `assets/icons.png` and `assets/sprites.png`.
4. Generate `Lua/limanchel/medical_icons/generated/atlases.lua`.

The build script does not edit `Lua/limanchel/medical_icons/data.lua`. Keep manual runtime constants there, such as `holdAngle`, origins, rotation, depth, and item-specific overrides.

## Usage

Full build with status icon overlays:

```powershell
python tools/build/build_project/build_project.py
```

Validate only:

```powershell
python tools/build/build_project/build_project.py --validate-only
```

Dry-run full build with status icon overlays:

```powershell
python tools/build/build_project/build_project.py --dry-run
```

Build without status icon overlays:

```powershell
python tools/build/build_project/build_project.py --disable-status-icons
```

Use a custom status icon mapping file:

```powershell
python tools/build/build_project/build_project.py --add-status-icons tools/build/build_project/statusicons.csv
```

Save standalone 64x64 icons with status overlays:

```powershell
python tools/build/build_project/build_project.py --save-status-icons
```

Save standalone status-overlaid icons to a specific directory:

```powershell
python tools/build/build_project/build_project.py --save-status-icons tools/build/build_project/status_icons
```

## Options

```text
--validate-only
```

Only validate item assets. Does not write atlases or Lua metadata.

```text
--add-status-icons STATUS_CSV
```

Read `identifier,statusicon` mappings and overlay status icons onto matching item icons before atlas packing.

Default:

```text
tools/build/build_project/statusicons.csv
```

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
tools/build/build_project/status_icons
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
Lua/limanchel/medical_icons/generated/atlases.lua
```

```text
--textures-dir PATH
```

Path to generated item texture folders.

Default:

```text
source/textures
```

```text
--statusicons-dir PATH
```

Path to 24x24 status icon PNG files.

Default:

```text
source/status_icons
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

## Inputs

- `source/textures/*/items/*/icon.png` - source item icons, required to be 64x64 PNG files.
- `source/textures/*/items/*/sprite.png` - source item sprites.
- `tools/build/build_project/statusicons.csv` - default `identifier,statusicon` mapping.
- `source/status_icons/*.png` - 24x24 status icon overlays.

## Outputs

- `assets/icons.png` - packed item icon atlas.
- `assets/sprites.png` - packed item sprite atlas.
- `Lua/limanchel/medical_icons/generated/atlases.lua` - generated atlas paths and item rectangles for Lua runtime code.
- `tools/build/build_project/status_icons/*.png` - optional standalone status-overlaid icons when `--save-status-icons` is used.

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

`texture` comes from `source/textures/<texture>/items/<identifier>`.

## Notes

- Final item assets are discovered only from `source/textures/<texture>/items/<identifier>/`.
- Root-level `icon.png` and `sprite.png` inside a texture folder are previews and are not packed.
- Status icons must be 24x24 PNG files.
- Item icons must be 64x64 PNG files.
- Sprite atlas dimensions are padded to multiples of 4.
- The script no longer generates CSV atlas maps or XML overrides.
