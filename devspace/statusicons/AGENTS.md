# Status Icon Instructions

## Scope
This folder stores Barotrauma status affliction icons.

Expected structure:

```text
devspace/statusicons/
  <name>.png
```

## File Meanings
- `<name>.png` - individual Barotrauma affliction status icon, 24x24 pixels.

## Color Rules
When extracting vanilla affliction icons, apply the icon's XML `color`/`iconcolors` tint or the user-requested target palette before saving the 24x24 PNG.

Do not save raw grayscale mask icons unless the user explicitly asks for an uncolored source mask.
