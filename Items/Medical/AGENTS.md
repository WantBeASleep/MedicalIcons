# Medical Runtime Instructions

## Scope
This folder contains Barotrauma item files for the medical part of the mod.

File meanings:

- `Icons.png` - atlas containing all final item icons.
- `Sprites.png` - atlas containing all final item sprites.
- `medical.xml` - medical item definitions.
- `poisons.xml` - poison item definitions.
- `buffs.xml` - buff item definitions.

## XML Build Rules
- Use Barotrauma `<Override>` wrappers, not `override="true"` attributes.
- Generated XML files must have this shape:

```xml
<Override>
  <Items>
    ...
  </Items>
</Override>
```

- Build XML from vanilla files in `D:\SteamLibrary\steamapps\common\Barotrauma\Content\Items\Medical` by default.
- Update each item's `InventoryIcon` texture to `%ModDir%/Items/Medical/Icons.png` and its `sourcerect` from `icons.csv`.
- Update each item's `Sprite` texture to `%ModDir%/Items/Medical/Sprites.png` and its `sourcerect` from `sprites.csv`.
- If an item is not found in vanilla XML, the build script may reuse an existing definition from `Items/Medical/*.xml` as a fallback.
- If an item is not found in either vanilla XML or existing mod XML, skip XML generation for that item with a warning; `--strict` turns this into an error.

## Filelist Rules
- `filelist.xml` must include only mod-facing runtime files, not `devspace` files.
- Do not add PNG texture atlas files to `filelist.xml`; Barotrauma loads `Icons.png` and `Sprites.png` through XML texture references.
- Required item file entries are:

```text
%ModDir%/Items/Medical/medical.xml
%ModDir%/Items/Medical/poisons.xml
%ModDir%/Items/Medical/buffs.xml
```
