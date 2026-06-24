# Script Instructions

## Scope
This folder stores development-only automation scripts for the whole project, build pipeline, validation, atlas generation, filelist updates, or similar project-wide tasks.

## Script Storage Rules
Store scripts based on their scope.

Global scripts belong under `devspace/scripts`. A script is global when it works on the whole mod, builds or validates the project, creates shared atlases or performs similar project-wide automation.

Local scripts belong in a `scripts` folder next to the files or folder tree they operate on. A script is local when it exists for one small, specific task or one narrow asset area. For example, preview-only scripts belong under `devspace/preview/scripts`, and one-texture helper scripts belong under `devspace/textures/<item>/scripts`.

Do not place one-off or narrow local helper scripts in the top-level `devspace/scripts`.
