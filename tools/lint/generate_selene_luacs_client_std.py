from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANNOTATIONS_ROOT = PROJECT_ROOT.parent / "Barotrauma-Lua-Annotations"
DEFAULT_SIDE = "client"

IDENTIFIER_RE = r"[A-Za-z_][A-Za-z0-9_]*"
ASSIGNMENT_RE = re.compile(rf"^({IDENTIFIER_RE}(?:\.{IDENTIFIER_RE})*)\s*=")
FUNCTION_RE = re.compile(rf"^function\s+({IDENTIFIER_RE}(?:\.{IDENTIFIER_RE})*)\s*\(([^)]*)\)")
ASSIGNED_FUNCTION_RE = re.compile(rf"^({IDENTIFIER_RE}(?:\.{IDENTIFIER_RE})*)\s*=\s*function\s*\(([^)]*)\)")
FIELD_RE = re.compile(rf"^\s*({IDENTIFIER_RE})\s*=\s*(.*)$")
PARAM_RE = re.compile(r"^---@param\s+([A-Za-z_][A-Za-z0-9_]*|\.\.\.)")


def std_entry() -> dict[str, object]:
    return {"property": "read-only", "any": True}


def function_entry(params: list[str]) -> dict[str, object]:
    entry: dict[str, object] = {"property": "read-only"}
    if params:
        entry["args"] = [{"type": "..."} for _ in params]
    return entry


def split_params(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",")]


def set_path(root: dict[str, object], path: str, value: dict[str, object]) -> None:
    parts = path.split(".")
    current = root
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {"property": "read-only"}
            current[part] = child
        current = child
    existing = current.get(parts[-1])
    if isinstance(existing, dict):
        existing.update(value)
    else:
        current[parts[-1]] = value


def parse_table(lines: list[str], start_index: int) -> tuple[dict[str, object], int]:
    entry: dict[str, object] = {"property": "read-only"}
    index = start_index + 1

    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("}"):
            return entry, index

        match = FIELD_RE.match(line)
        if match:
            field_name = match.group(1)
            assigned_value = match.group(2)
            if "{" in assigned_value and "}" not in assigned_value:
                child, index = parse_table(lines, index)
                entry[field_name] = child
            else:
                entry[field_name] = std_entry()

        index += 1

    return entry, index


def parse_lua_file(path: Path, globals_map: dict[str, object]) -> None:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    pending_params: list[str] = []
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.strip()

        param_match = PARAM_RE.match(line)
        if param_match:
            pending_params.append(param_match.group(1))
            index += 1
            continue

        function_match = FUNCTION_RE.match(line) or ASSIGNED_FUNCTION_RE.match(line)
        if function_match:
            name = function_match.group(1)
            params = pending_params or split_params(function_match.group(2))
            set_path(globals_map, name, function_entry(params))
            pending_params = []
            index += 1
            continue

        assignment_match = ASSIGNMENT_RE.match(line)
        if assignment_match:
            name = assignment_match.group(1)
            if name in {"math", "string"}:
                pending_params = []
                index += 1
                continue
            if line.endswith("{") or line.endswith("= {"):
                entry, new_index = parse_table(lines, index)
                if len(entry) == 1:
                    entry.update(std_entry())
                set_path(globals_map, name, entry)
                index = new_index + 1
                pending_params = []
                continue
            set_path(globals_map, name, std_entry())
            pending_params = []

        index += 1


def sort_mapping(value: object) -> object:
    if not isinstance(value, dict):
        return value
    ordered: dict[str, object] = {}
    for key in sorted(value):
        child = value[key]
        if isinstance(child, dict):
            child = sort_mapping(child)
        ordered[key] = child
    return ordered


def yaml_scalar(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def dump_yaml(value: object, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, dict):
                lines.append(f"{prefix}{key}:")
                lines.extend(dump_yaml(child, indent + 2))
            elif isinstance(child, list):
                lines.append(f"{prefix}{key}:")
                lines.extend(dump_yaml(child, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(child)}")
        return lines
    if isinstance(value, list):
        lines = []
        for child in value:
            if isinstance(child, dict):
                lines.append(f"{prefix}-")
                lines.extend(dump_yaml(child, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(child)}")
        return lines
    return [f"{prefix}{yaml_scalar(value)}"]


def build_std(library: Path, side: str) -> dict[str, object]:
    if not library.is_dir():
        raise FileNotFoundError(f"{side.title()} annotations directory not found: {library}")

    globals_map: dict[str, object] = {}
    for path in sorted(library.rglob("*.lua")):
        parse_lua_file(path, globals_map)

    # These are LuaCs runtime constants in the annotation global.lua.
    globals_map["CLIENT"] = {"property": "read-only"}
    globals_map["SERVER"] = {"property": "read-only"}

    return {"globals": sort_mapping(globals_map)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Selene client std from Barotrauma-Lua-Annotations type defs."
    )
    parser.add_argument(
        "--annotations-root",
        type=Path,
        default=DEFAULT_ANNOTATIONS_ROOT,
        help="Path to Barotrauma-Lua-Annotations.",
    )
    parser.add_argument(
        "--side",
        choices=("client", "server"),
        default=DEFAULT_SIDE,
        help="Annotation side to convert.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output Selene std YAML path.",
    )
    args = parser.parse_args()

    side_dir_name = args.side.title()
    library = args.annotations_root / "Library" / side_dir_name
    output = args.output or PROJECT_ROOT / f"selene_std_luacs_{args.side}.yml"

    std = build_std(library, args.side)
    header = [
        "---",
        f"# Generated from Barotrauma-Lua-Annotations/Library/{side_dir_name}.",
        "# Source of truth: Lua annotation type definitions, not this mod's Lua code.",
    ]
    output_lines = header + dump_yaml(std)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
