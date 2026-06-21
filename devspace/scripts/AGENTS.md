# Script Instructions

## Scope
This folder stores development-only automation scripts for the whole project, build pipeline, validation, atlas generation, XML generation, filelist updates, or similar project-wide tasks.

## Script Storage Rules
Store scripts based on their scope.

Global scripts belong under `devspace/scripts`. A script is global when it works on the whole mod, builds or validates the project, creates shared atlases, updates XML/filelist data, or performs similar project-wide automation.

Local scripts belong in a `scripts` folder next to the files or folder tree they operate on. A script is local when it exists for one small, specific task or one narrow asset area. For example, preview-only scripts belong under `devspace/preview/scripts`, and one-texture helper scripts belong under `devspace/textures/<item>/scripts`.

Do not place one-off or narrow local helper scripts in the top-level `devspace/scripts`.

## Build Script
The main mod build script is:

```text
devspace/scripts/build_project/build_project.py
```

The script's README is:

```text
devspace/scripts/build_project/README.md
```

`build_project.py` validates generated item assets, overlays status icons by default, builds final item icon/sprite atlases, writes atlas coordinate CSV files, rebuilds medical XML overrides, and updates root `filelist.xml`.

## Build Pipeline
1. Validate final in-game item assets under `devspace/textures/*/items/*`.
2. Overlay status icons from `devspace/statusicons` onto item icons by default.
3. Build final `Icons.png` and `Sprites.png` atlases and write `icons.csv` and `sprites.csv` coordinate maps.
4. Build item XML files from vanilla Barotrauma XML using `<Override><Items>...`.
5. Update the root `filelist.xml`.

Default outputs:

```text
Items/Medical/Icons.png
Items/Medical/Sprites.png
Items/Medical/medical.xml
Items/Medical/poisons.xml
Items/Medical/buffs.xml
devspace/scripts/build_project/icons.csv
devspace/scripts/build_project/sprites.csv
```

## Build Commands
Validation-only command:

```powershell
python devspace/scripts/build_project/build_project.py --validate-only
```

Dry-run full build command:

```powershell
python devspace/scripts/build_project/build_project.py --all --dry-run
```

Full build command:

```powershell
python devspace/scripts/build_project/build_project.py --all
```

## Important Build Flags
- `--validate-only` - validate item assets without writing atlases, XML, or `filelist.xml`.
- `--all` - run the full build pipeline.
- `--dry-run` - print planned writes without writing files.
- `--strict` - treat warnings as errors.
- `--verbose` - print detailed item validation output.
- `--atlas-out DIR` - write `Icons.png` and `Sprites.png` to a custom directory.
- `--csv-out DIR` - write `icons.csv` and `sprites.csv` to a custom directory.
- `--xml` - build XML overrides without necessarily updating `filelist.xml`.
- `--filelist` - update root `filelist.xml`.
- `--vanilla-medical-dir PATH` - use a custom vanilla Barotrauma medical XML directory.
- `--textures-dir PATH` - use a custom generated texture directory. Default is `devspace/textures`.
- `--statusicons-dir PATH` - use a custom status icon directory. Default is `devspace/statusicons`.
- `--sprite-atlas-width PX` - preferred sprite atlas shelf width before multiple-of-4 padding. Default is `512`.

## Status Icon Overlay
- Status icons are overlaid before item icon atlas packing by default.
- The default status icon mapping file is `devspace/scripts/build_project/statusicons.csv`.
- Use `--add-status-icons STATUS_CSV` to override the default status icon mapping CSV.
- Use `--disable-status-icons` to build item icon atlases without status icon overlays.
- The CSV format is `identifier,statusicon`.
- `identifier` is the in-game item identifier, matching `devspace/textures/<asset>/items/<identifier>/`.
- `statusicon` is the status icon PNG stem in `devspace/statusicons`, for example `opiatewithdrawal` for `devspace/statusicons/opiatewithdrawal.png`.
- Status icons must be 24x24 PNG files.
- Status overlays are applied in memory for atlas building by default; they do not overwrite source item icons.
- Use `--save-status-icons [DIR]` to also save standalone 64x64 icons after overlay.
- If `--save-status-icons` is provided without a directory, save to `devspace/scripts/build_project/status_icons`.

## Build Safety
- Before running a real full build, run `--all --dry-run` first and review warnings.
- If a change affects the future runtime build, follow the dry-run with a real full build unless the dry-run reveals a problem that should be fixed first.
- Do not write generated status-overlay preview icons outside `devspace`.
