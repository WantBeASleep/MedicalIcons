# clean_python_cache

Remove Python cache artifacts from the Medical Icons mod workspace.

## Location

```text
tools/build/clean_python_cache/clean_python_cache.py
```

## Basic Usage

Preview cache artifacts without deleting them:

```powershell
python tools/build/clean_python_cache/clean_python_cache.py --dry-run
```

Remove all `__pycache__` directories and standalone `.pyc` files under the project root:

```powershell
python tools/build/clean_python_cache/clean_python_cache.py
```

Use this after running any Python script in the project, before packaging or publishing the mod.
