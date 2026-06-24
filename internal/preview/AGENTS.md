# Preview Instructions

## Scope
This folder stores development-only preview images for the mod, such as Steam Workshop preview images, item showcase images, before/after comparison images, and generated visual review sheets.

Preview files are not used by Barotrauma at runtime. Do not copy preview images into mod-facing folders and do not add them to `filelist.xml`.

Expected structure:

```text
internal/preview/
  scripts/
  source/
  <preview_name>.png
```

Preview scripts may use shared font files from `internal/fonts`.

## Preview Scripts
`internal/preview/scripts` stores preview-only scripts, such as Steam Workshop preview generators and small preview-specific helpers.

Preview-only scripts are local scripts. Do not place preview-only helpers in the top-level `internal/scripts`.

Preview scripts should load bundled fonts from `internal/fonts` instead of hard-coded system font paths such as `C:/Windows/Fonts`.

## Preview Sources
`internal/preview/source` stores source images used to generate finished Steam Workshop preview images.

Files in this folder are preview-generation inputs only. They are not final Steam Workshop images, are not used by Barotrauma at runtime, and must not be added to `filelist.xml`.

## Preview Image Rules
- Keep only finished Steam Workshop preview images directly inside `internal/preview`.
- Keep source images used for preview generation inside `internal/preview/source`.
- Use 1920x1080 PNG files for Steam Workshop preview images unless the user explicitly requests another size.
- Preview images may compose existing item icons, sprites, status icons, backgrounds, labels, and other development-only visual elements.
