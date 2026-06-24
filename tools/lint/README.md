# Lua lint tools

This directory contains helper scripts for installing and running Selene for the
LuaCs runtime code in `Lua/`.

The project uses Selene with `std = "lua52+selene_std_luacs_client"` for the
local client-side mod code. LuaCsForBarotrauma runs through MoonSharp and
accepts Lua 5.2 syntax such as `goto` labels, while the official Selene 0.31.0
Windows binary is not built with Lua 5.2 parser support enabled.

A server-side Selene config is also available at `selene.server.toml`. It uses
`std = "lua52+selene_std_luacs_server"` with the same lint rules.

## `run_selene.py`

Runs the local Selene binary against the project's Lua runtime files.

```powershell
python tools\lint\run_selene.py
```

The script:

- finds the project root from its own location;
- expects Selene at `bin/selene.exe`;
- runs Selene against `Lua/`;
- returns Selene's exit code.

Use this for normal lint checks after editing Lua files.

## `generate_selene_luacs_client_std.py`

Generates Selene standard library YAML files from
`Barotrauma-Lua-Annotations` type definitions.

```powershell
python tools\lint\generate_selene_luacs_client_std.py --side client
python tools\lint\generate_selene_luacs_client_std.py --side server
```

By default the script expects the annotations repository next to this mod:

```text
../Barotrauma-Lua-Annotations
```

The generated outputs are:

- `selene_std_luacs_client.yml` from `Library/Client`;
- `selene_std_luacs_server.yml` from `Library/Server`.

Use `--annotations-root <path>` when the annotations repository is elsewhere,
and `--output <path>` to write a custom YAML file.

The script intentionally uses the annotation files as the source of truth,
rather than scanning this mod's current Lua code. It converts declared globals,
tables, and simple function parameter counts to Selene's std format. Complex
Barotrauma C# userdata and generated API surfaces are kept permissive with
`any: true`, because Selene's std format is not a full LuaLS or C# type system.

Validate the generated configs with:

```powershell
bin\selene.exe validate-config
bin\selene.exe --config selene.server.toml Lua
```

After running this or any other Python script in the project, remove Python
cache artifacts:

```powershell
python tools\build\clean_python_cache\clean_python_cache.py
```

## `install_selene.py`

Builds the local Selene binary used by `run_selene.py`.

```powershell
python tools\lint\install_selene.py
```

Requirements:

- `git` must be available in `PATH`;
- `cargo` must be available in `PATH`, or installed at
  `%USERPROFILE%\.cargo\bin\cargo.exe`.

The script:

- clones `https://github.com/Kampfkarren/selene.git` at tag `0.31.0`;
- uses `tools/_selene_build_src` as a temporary build directory;
- patches Selene's binary crate manifest before building;
- runs `cargo build --release -p selene`;
- copies the built executable to `bin/selene.exe`;
- removes the temporary build directory, including read-only files under `.git`.

### Selene rebuild patch

Selene 0.31.0's binary crate defaults to the Roblox/Luau build:

```toml
[features]
default = ["roblox"]
tracy-profiling = ["profiling/profile-with-tracy", "tracy-client"]
roblox = ["selene-lib/roblox", "full_moon/roblox", "ureq"]
```

For this project, Roblox support is unnecessary. LuaCs needs Lua 5.2 syntax
support instead. `install_selene.py` changes the manifest to:

```toml
[features]
default = ["lua52"]
tracy-profiling = ["profiling/profile-with-tracy", "tracy-client"]
roblox = ["selene-lib/roblox", "full_moon/roblox", "ureq"]
lua52 = ["selene-lib/lua52", "full_moon/lua52"]
```

This disables the default Roblox feature for the built binary and enables Lua
5.2 support through both Selene's lint library and the `full_moon` parser.
