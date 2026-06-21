# Preview Instructions

## Scope
This folder stores development-only preview images for the mod, such as Steam Workshop preview images, item showcase images, before/after comparison images, and generated visual review sheets.

Preview files are not used by Barotrauma at runtime. Do not copy preview images into mod-facing folders and do not add them to `filelist.xml`.

Expected structure:

```text
devspace/preview/
  scripts/
  source/
  <preview_name>.png
```

## Preview Scripts
`devspace/preview/scripts` stores preview-only scripts, such as Steam Workshop preview generators and small preview-specific helpers.

Preview-only scripts are local scripts. Do not place preview-only helpers in the top-level `devspace/scripts`.

## Preview Sources
`devspace/preview/source` stores source images used to generate finished Steam Workshop preview images.

Files in this folder are preview-generation inputs only. They are not final Steam Workshop images, are not used by Barotrauma at runtime, and must not be added to `filelist.xml`.

## Preview Image Rules
- Keep only finished Steam Workshop preview images directly inside `devspace/preview`.
- Keep source images used for preview generation inside `devspace/preview/source`.
- Use 1920x1080 PNG files for Steam Workshop preview images unless the user explicitly requests another size.
- Preview images may compose existing item icons, sprites, status icons, backgrounds, labels, and other development-only visual elements.
