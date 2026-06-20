from __future__ import annotations

import argparse
import csv
import math
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEXTURES_DIR = PROJECT_ROOT / "devspace" / "textures"
DEFAULT_STATUSICONS_DIR = PROJECT_ROOT / "devspace" / "statusicons"
DEFAULT_ATLAS_OUT_DIR = PROJECT_ROOT / "Items" / "Medical"
DEFAULT_CSV_OUT_DIR = SCRIPT_DIR
DEFAULT_STATUS_ICON_OUT_DIR = SCRIPT_DIR / "status_icons"
DEFAULT_VANILLA_MEDICAL_DIR = PROJECT_ROOT.parents[1] / "Content" / "Items" / "Medical"
DEFAULT_VANILLA_ITEMS_DIR = PROJECT_ROOT.parents[1] / "Content" / "Items"
DEFAULT_FILELIST = PROJECT_ROOT / "filelist.xml"
MOD_ICON_TEXTURE = "%ModDir%/Items/Medical/icons.png"
MOD_SPRITE_TEXTURE = "%ModDir%/Items/Medical/sprites.png"
ICON_SIZE = 64
STATUS_ICON_SIZE = 24
XML_NAMES = ("medical.xml", "poisons.xml", "buffs.xml")
EXTRA_VANILLA_ITEMS = {
    "huskeggs": ("CreatureLoot/creatureloot.xml", "poisons.xml"),
    "combatstimulantsyringe": ("Jobgear/Medic/medic_talent_items.xml", "buffs.xml"),
    "pressurestabilizer": ("Jobgear/Medic/medic_talent_items.xml", "buffs.xml"),
    "sulphuricacidsyringe": ("Jobgear/Medic/medic_talent_items.xml", "buffs.xml"),
}


@dataclass(frozen=True)
class ItemAsset:
    identifier: str
    asset_name: str
    item_dir: Path
    icon_path: Path
    sprite_path: Path
    icon_size: tuple[int, int]
    sprite_size: tuple[int, int]


@dataclass(frozen=True)
class AtlasEntry:
    identifier: str
    source: Path
    x: int
    y: int
    width: int
    height: int

    @property
    def sourcerect(self) -> str:
        return f"{self.x},{self.y},{self.width},{self.height}"


@dataclass
class BuildContext:
    args: argparse.Namespace
    items: list[ItemAsset]
    icon_entries: dict[str, AtlasEntry]
    sprite_entries: dict[str, AtlasEntry]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Medical Icons item assets, build atlases, update XML overrides, and refresh filelist.xml."
    )
    parser.add_argument("--validate-only", action="store_true", help="Only validate source item assets.")
    parser.add_argument(
        "--add-status-icons",
        type=Path,
        metavar="STATUS_CSV",
        help="CSV mapping item identifier to status icon name. Columns: identifier,statusicon.",
    )
    parser.add_argument(
        "--save-status-icons",
        nargs="?",
        const=DEFAULT_STATUS_ICON_OUT_DIR,
        type=Path,
        metavar="DIR",
        help="Save 64x64 item icons after status icon overlay. Default: devspace/scripts/build_project/status_icons.",
    )
    parser.add_argument(
        "--atlas-out",
        type=Path,
        default=DEFAULT_ATLAS_OUT_DIR,
        help="Directory for icons.png and sprites.png. Default: Items/Medical.",
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=DEFAULT_CSV_OUT_DIR,
        help="Directory for icons.csv and sprites.csv. Default: devspace/scripts/build_project.",
    )
    parser.add_argument("--xml", action="store_true", help="Build mod XML overrides from vanilla item XML.")
    parser.add_argument("--filelist", action="store_true", help="Update root filelist.xml entries.")
    parser.add_argument("--all", action="store_true", help="Run validation, atlas build, XML build, and filelist update.")
    parser.add_argument(
        "--vanilla-medical-dir",
        type=Path,
        default=DEFAULT_VANILLA_MEDICAL_DIR,
        help="Vanilla Barotrauma Content/Items/Medical directory.",
    )
    parser.add_argument(
        "--textures-dir",
        type=Path,
        default=DEFAULT_TEXTURES_DIR,
        help="Directory with devspace texture item asset folders.",
    )
    parser.add_argument(
        "--statusicons-dir",
        type=Path,
        default=DEFAULT_STATUSICONS_DIR,
        help="Directory with 24x24 status icon PNGs.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and report planned writes without writing files.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed item and output information.")
    parser.add_argument(
        "--sprite-atlas-width",
        type=int,
        default=512,
        help="Preferred sprite atlas shelf width before final multiple-of-4 padding. Default: 512.",
    )
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def warn(ctx: BuildContext | None, message: str) -> None:
    if ctx is not None:
        ctx.warnings.append(message)
    print(f"WARNING: {message}")


def ensure_project_dirs(args: argparse.Namespace) -> None:
    required = [args.textures_dir, args.statusicons_dir, PROJECT_ROOT / "Items" / "Medical"]
    missing = [rel(path) for path in required if not path.is_dir()]
    if missing:
        fail(f"Missing required directories: {', '.join(missing)}")


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def discover_items(textures_dir: Path) -> list[ItemAsset]:
    if not textures_dir.is_dir():
        fail(f"Textures directory not found: {rel(textures_dir)}")

    items: list[ItemAsset] = []
    seen: dict[str, Path] = {}
    for asset_dir in sorted(path for path in textures_dir.iterdir() if path.is_dir()):
        items_dir = asset_dir / "items"
        if not items_dir.is_dir():
            continue

        for item_dir in sorted(path for path in items_dir.iterdir() if path.is_dir()):
            identifier = item_dir.name
            if identifier in seen:
                fail(f"Duplicate item identifier '{identifier}' in {rel(seen[identifier])} and {rel(item_dir)}")
            seen[identifier] = item_dir

            icon_path = item_dir / "icon.png"
            sprite_path = item_dir / "sprite.png"
            if not icon_path.is_file():
                fail(f"Missing icon.png for '{identifier}' in {rel(item_dir)}")
            if not sprite_path.is_file():
                fail(f"Missing sprite.png for '{identifier}' in {rel(item_dir)}")

            icon_size = image_size(icon_path)
            sprite_size = image_size(sprite_path)
            if icon_size != (ICON_SIZE, ICON_SIZE):
                fail(f"{rel(icon_path)} is {icon_size[0]}x{icon_size[1]}, expected {ICON_SIZE}x{ICON_SIZE}")
            if sprite_size[0] <= 0 or sprite_size[1] <= 0:
                fail(f"{rel(sprite_path)} has invalid size {sprite_size[0]}x{sprite_size[1]}")

            items.append(
                ItemAsset(
                    identifier=identifier,
                    asset_name=asset_dir.name,
                    item_dir=item_dir,
                    icon_path=icon_path,
                    sprite_path=sprite_path,
                    icon_size=icon_size,
                    sprite_size=sprite_size,
                )
            )

    if not items:
        fail(f"No item folders found under {rel(textures_dir)}")
    return items


def read_status_icon_map(csv_path: Path, item_ids: set[str], statusicons_dir: Path) -> dict[str, str]:
    if not csv_path.is_file():
        fail(f"Status icon CSV not found: {rel(csv_path)}")

    mapping: dict[str, str] = {}
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            fail(f"Status icon CSV is empty: {rel(csv_path)}")
        normalized = {name.strip().lower(): name for name in reader.fieldnames}
        id_key = normalized.get("identifier") or normalized.get("identefer") or normalized.get("id")
        status_key = normalized.get("statusicon") or normalized.get("status_icon") or normalized.get("icon")
        if id_key is None or status_key is None:
            fail("Status icon CSV must contain identifier,statusicon columns")

        for line_number, row in enumerate(reader, start=2):
            identifier = (row.get(id_key) or "").strip()
            statusicon = (row.get(status_key) or "").strip()
            if not identifier and not statusicon:
                continue
            if not identifier or not statusicon:
                fail(f"Incomplete status icon CSV row {line_number}: {row}")
            if identifier not in item_ids:
                fail(f"Status icon CSV references unknown item identifier '{identifier}' on row {line_number}")
            if identifier in mapping:
                fail(f"Duplicate status icon mapping for '{identifier}' on row {line_number}")
            icon_path = statusicons_dir / f"{statusicon}.png"
            if not icon_path.is_file():
                fail(f"Status icon '{statusicon}' for '{identifier}' not found at {rel(icon_path)}")
            if image_size(icon_path) != (STATUS_ICON_SIZE, STATUS_ICON_SIZE):
                fail(f"{rel(icon_path)} must be {STATUS_ICON_SIZE}x{STATUS_ICON_SIZE}")
            mapping[identifier] = statusicon

    return mapping


def load_icon_with_status_overlay(item: ItemAsset, statusicon: str | None, statusicons_dir: Path) -> Image.Image:
    icon = Image.open(item.icon_path).convert("RGBA")
    if statusicon is not None:
        overlay = Image.open(statusicons_dir / f"{statusicon}.png").convert("RGBA")
        icon.alpha_composite(overlay, (0, 0))
        overlay.close()
    return icon


def atlas_dimension(value: int) -> int:
    return max(4, math.ceil(value / 4) * 4)


def build_icon_atlas(
    items: list[ItemAsset],
    status_map: dict[str, str],
    args: argparse.Namespace,
) -> tuple[Image.Image, list[AtlasEntry]]:
    columns = math.ceil(math.sqrt(len(items)))
    rows = math.ceil(len(items) / columns)
    atlas = Image.new("RGBA", (atlas_dimension(columns * ICON_SIZE), atlas_dimension(rows * ICON_SIZE)), (0, 0, 0, 0))
    entries: list[AtlasEntry] = []

    for index, item in enumerate(items):
        x = index % columns * ICON_SIZE
        y = index // columns * ICON_SIZE
        icon = load_icon_with_status_overlay(item, status_map.get(item.identifier), args.statusicons_dir)
        atlas.alpha_composite(icon, (x, y))
        entries.append(AtlasEntry(item.identifier, item.icon_path, x, y, ICON_SIZE, ICON_SIZE))
        icon.close()

    return atlas, entries


def build_sprite_atlas(items: list[ItemAsset], atlas_width: int) -> tuple[Image.Image, list[AtlasEntry]]:
    if atlas_width <= 0:
        fail("--sprite-atlas-width must be greater than 0")
    atlas_width = atlas_dimension(atlas_width)
    x = 0
    y = 0
    row_height = 0
    placements: list[AtlasEntry] = []

    for item in items:
        width, height = item.sprite_size
        if width > atlas_width:
            fail(f"{rel(item.sprite_path)} is wider than --sprite-atlas-width ({width} > {atlas_width})")
        if x > 0 and x + width > atlas_width:
            x = 0
            y += row_height
            row_height = 0
        placements.append(AtlasEntry(item.identifier, item.sprite_path, x, y, width, height))
        x += width
        row_height = max(row_height, height)

    atlas_height = atlas_dimension(y + row_height)
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    for item, entry in zip(items, placements):
        sprite = Image.open(item.sprite_path).convert("RGBA")
        atlas.alpha_composite(sprite, (entry.x, entry.y))
        sprite.close()

    return atlas, placements


def write_entries_csv(path: Path, entries: list[AtlasEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["identifier", "source", "x", "y", "width", "height", "sourcerect"],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "identifier": entry.identifier,
                    "source": rel(entry.source),
                    "x": entry.x,
                    "y": entry.y,
                    "width": entry.width,
                    "height": entry.height,
                    "sourcerect": entry.sourcerect,
                }
            )


def save_status_overlay_icons(items: list[ItemAsset], status_map: dict[str, str], args: argparse.Namespace) -> None:
    if args.save_status_icons is None:
        return
    if not status_map:
        fail("--save-status-icons requires --add-status-icons with at least one mapping")

    out_dir = args.save_status_icons
    if args.dry_run:
        print(f"DRY RUN: would write status-overlaid icons to {rel(out_dir)}")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        statusicon = status_map.get(item.identifier)
        if statusicon is None:
            continue
        icon = load_icon_with_status_overlay(item, statusicon, args.statusicons_dir)
        icon.save(out_dir / f"{item.identifier}.png")
        icon.close()


def write_atlases(ctx: BuildContext, status_map: dict[str, str]) -> None:
    icon_atlas, icon_entries = build_icon_atlas(ctx.items, status_map, ctx.args)
    sprite_atlas, sprite_entries = build_sprite_atlas(ctx.items, ctx.args.sprite_atlas_width)
    ctx.icon_entries = {entry.identifier: entry for entry in icon_entries}
    ctx.sprite_entries = {entry.identifier: entry for entry in sprite_entries}

    icons_path = ctx.args.atlas_out / "icons.png"
    sprites_path = ctx.args.atlas_out / "sprites.png"
    icons_csv_path = ctx.args.csv_out / "icons.csv"
    sprites_csv_path = ctx.args.csv_out / "sprites.csv"

    if ctx.args.dry_run:
        print(f"DRY RUN: would write {rel(icons_path)} ({icon_atlas.width}x{icon_atlas.height})")
        print(f"DRY RUN: would write {rel(sprites_path)} ({sprite_atlas.width}x{sprite_atlas.height})")
        print(f"DRY RUN: would write {rel(icons_csv_path)}")
        print(f"DRY RUN: would write {rel(sprites_csv_path)}")
    else:
        ctx.args.atlas_out.mkdir(parents=True, exist_ok=True)
        ctx.args.csv_out.mkdir(parents=True, exist_ok=True)
        icon_atlas.save(icons_path)
        sprite_atlas.save(sprites_path)
        write_entries_csv(icons_csv_path, icon_entries)
        write_entries_csv(sprites_csv_path, sprite_entries)

    print(f"Packed {len(icon_entries)} icons into {icon_atlas.width}x{icon_atlas.height}")
    print(f"Packed {len(sprite_entries)} sprites into {sprite_atlas.width}x{sprite_atlas.height}")
    icon_atlas.close()
    sprite_atlas.close()


def indent_xml(element: ET.Element, level: int = 0) -> None:
    space = "\n" + level * "  "
    child_space = "\n" + (level + 1) * "  "
    children = list(element)
    if children:
        if not element.text or not element.text.strip():
            element.text = child_space
        for child in children:
            indent_xml(child, level + 1)
        if not children[-1].tail or not children[-1].tail.strip():
            children[-1].tail = space
    if level and (not element.tail or not element.tail.strip()):
        element.tail = space


def item_identifier(element: ET.Element) -> str | None:
    for key, value in element.attrib.items():
        if key.lower() == "identifier":
            return value
    return None


def find_child_case_insensitive(element: ET.Element, tag: str) -> ET.Element | None:
    tag_lower = tag.lower()
    for child in element:
        if child.tag.lower() == tag_lower:
            return child
    return None


def set_visual_element(item: ET.Element, tag: str, texture: str, entry: AtlasEntry) -> None:
    child = find_child_case_insensitive(item, tag)
    if child is None:
        child = ET.Element(tag)
        item.insert(0, child)
    child.set("texture", texture)
    child.set("sourcerect", entry.sourcerect)
    if "origin" not in {key.lower(): value for key, value in child.attrib.items()}:
        child.set("origin", "0.5,0.5")


def parse_vanilla_items(vanilla_dir: Path) -> tuple[dict[str, tuple[str, ET.Element]], dict[str, list[ET.Element]]]:
    item_map: dict[str, tuple[str, ET.Element]] = {}
    by_file: dict[str, list[ET.Element]] = {name: [] for name in XML_NAMES}

    for xml_name in XML_NAMES:
        xml_path = vanilla_dir / xml_name
        if not xml_path.is_file():
            fail(f"Vanilla XML not found: {xml_path}")
        root = ET.parse(xml_path).getroot()
        if root.tag.lower() != "items":
            fail(f"{xml_path} root is <{root.tag}>, expected <Items>")
        for child in root:
            identifier = item_identifier(child)
            if identifier is None:
                continue
            if identifier in item_map:
                fail(f"Duplicate vanilla item identifier '{identifier}'")
            item_map[identifier] = (xml_name, child)
            by_file[xml_name].append(child)

    for identifier, (relative_xml_path, output_xml_name) in EXTRA_VANILLA_ITEMS.items():
        xml_path = DEFAULT_VANILLA_ITEMS_DIR / Path(relative_xml_path)
        if not xml_path.is_file():
            fail(f"Extra vanilla XML not found for '{identifier}': {xml_path}")
        root = ET.parse(xml_path).getroot()
        if root.tag.lower() != "items":
            fail(f"{xml_path} root is <{root.tag}>, expected <Items>")
        source_element = None
        for child in root:
            if item_identifier(child) == identifier:
                source_element = child
                break
        if source_element is None:
            fail(f"Extra vanilla item '{identifier}' not found in {xml_path}")
        if identifier in item_map:
            fail(f"Duplicate vanilla item identifier '{identifier}'")
        item_map[identifier] = (output_xml_name, source_element)
        by_file[output_xml_name].append(source_element)

    return item_map, by_file


def parse_mod_items(mod_dir: Path) -> dict[str, tuple[str, ET.Element]]:
    item_map: dict[str, tuple[str, ET.Element]] = {}
    for xml_name in XML_NAMES:
        xml_path = mod_dir / xml_name
        if not xml_path.is_file():
            continue
        if xml_path.stat().st_size == 0:
            continue
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError:
            continue
        items_root = root.find("Items") if root.tag.lower() == "override" else root
        if items_root is None:
            continue
        for child in items_root:
            identifier = item_identifier(child)
            if identifier is not None and identifier not in item_map:
                item_map[identifier] = (xml_name, child)
    return item_map


def build_xml(ctx: BuildContext) -> None:
    if not ctx.icon_entries or not ctx.sprite_entries:
        write_atlases(ctx, {})

    vanilla_items, _ = parse_vanilla_items(ctx.args.vanilla_medical_dir)
    mod_items = parse_mod_items(PROJECT_ROOT / "Items" / "Medical")
    outputs: dict[str, list[ET.Element]] = {name: [] for name in XML_NAMES}

    for item in ctx.items:
        source = vanilla_items.get(item.identifier)
        if source is None:
            source = mod_items.get(item.identifier)
            if source is None:
                message = f"No vanilla or existing mod XML item found for '{item.identifier}'"
                if ctx.args.strict:
                    fail(message)
                warn(ctx, message)
                continue
            warn(ctx, f"No vanilla XML item found for '{item.identifier}', using existing mod XML fallback")

        xml_name, source_element = source
        item_element = ET.fromstring(ET.tostring(source_element, encoding="unicode"))
        if item.identifier not in vanilla_items:
            source_note = ET.Comment(f" Existing mod item fallback for {item.identifier}. ")
            outputs[xml_name].append(source_note)
        set_visual_element(item_element, "InventoryIcon", MOD_ICON_TEXTURE, ctx.icon_entries[item.identifier])
        set_visual_element(item_element, "Sprite", MOD_SPRITE_TEXTURE, ctx.sprite_entries[item.identifier])
        outputs[xml_name].append(item_element)

    for xml_name, elements in outputs.items():
        out_path = PROJECT_ROOT / "Items" / "Medical" / xml_name
        override = ET.Element("Override")
        items_root = ET.SubElement(override, "Items")
        for element in elements:
            items_root.append(element)
        indent_xml(override)
        tree = ET.ElementTree(override)
        if ctx.args.dry_run:
            print(f"DRY RUN: would write {rel(out_path)} with {len(elements)} overrides")
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            tree.write(out_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
        print(f"Prepared {len(elements)} overrides for {rel(out_path)}")


def update_filelist(args: argparse.Namespace) -> None:
    required_files = [
        "%ModDir%/Items/Medical/medical.xml",
        "%ModDir%/Items/Medical/poisons.xml",
        "%ModDir%/Items/Medical/buffs.xml",
    ]
    disallowed_files = {
        "%ModDir%/Items/Medical/icons.png",
        "%ModDir%/Items/Medical/sprites.png",
    }
    filelist_path = DEFAULT_FILELIST
    if not filelist_path.is_file():
        fail(f"filelist.xml not found: {rel(filelist_path)}")

    tree = ET.parse(filelist_path)
    root = tree.getroot()
    existing = {
        value
        for element in root
        for key, value in element.attrib.items()
        if key.lower() == "file"
    }

    added: list[str] = []
    for file_value in required_files:
        if file_value in existing:
            continue
        ET.SubElement(root, "Item", {"file": file_value})
        added.append(file_value)

    removed: list[str] = []
    for element in list(root):
        file_value = None
        for key, value in element.attrib.items():
            if key.lower() == "file":
                file_value = value
                break
        if file_value not in disallowed_files:
            continue
        root.remove(element)
        removed.append(file_value)

    indent_xml(root)
    if args.dry_run:
        changes = []
        if added:
            changes.append(f"add filelist entries: {', '.join(added)}")
        if removed:
            changes.append(f"remove filelist PNG entries: {', '.join(removed)}")
        if changes:
            print(f"DRY RUN: would {'; '.join(changes)}")
        else:
            print("DRY RUN: filelist.xml already has required entries and no PNG entries")
        return

    if added or removed:
        tree.write(filelist_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
        print(f"Updated {rel(filelist_path)} with {len(added)} added and {len(removed)} removed entries")
    else:
        print(f"{rel(filelist_path)} already has required entries and no PNG entries")


def print_item_summary(items: list[ItemAsset], verbose: bool) -> None:
    print(f"Validated {len(items)} item asset folders")
    if not verbose:
        return
    for item in items:
        print(
            f"  {item.identifier}: {item.asset_name}, icon {item.icon_size[0]}x{item.icon_size[1]}, "
            f"sprite {item.sprite_size[0]}x{item.sprite_size[1]}"
        )


def main() -> None:
    args = parse_args()
    ensure_project_dirs(args)
    if args.save_status_icons is not None and args.add_status_icons is None:
        fail("--save-status-icons requires --add-status-icons")

    items = discover_items(args.textures_dir)
    print_item_summary(items, args.verbose)
    ctx = BuildContext(args=args, items=items, icon_entries={}, sprite_entries={}, warnings=[])

    status_map: dict[str, str] = {}
    if args.add_status_icons is not None:
        status_map = read_status_icon_map(args.add_status_icons, {item.identifier for item in items}, args.statusicons_dir)
        print(f"Loaded {len(status_map)} status icon mappings from {rel(args.add_status_icons)}")
        save_status_overlay_icons(items, status_map, args)

    build_atlases = args.all or (not args.validate_only)
    if build_atlases:
        write_atlases(ctx, status_map)

    if args.all or args.xml:
        build_xml(ctx)

    if args.all or args.filelist:
        update_filelist(args)

    if ctx.warnings and args.strict:
        fail(f"Strict mode failed with {len(ctx.warnings)} warnings")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted")
