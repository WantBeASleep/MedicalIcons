from __future__ import annotations

import csv
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BAROTRAUMA_ROOT = PROJECT_ROOT.parents[1]
CONTENT_ITEMS_ROOT = BAROTRAUMA_ROOT / "Content" / "Items"
ATLAS_DIR = PROJECT_ROOT / "devspace" / "scripts" / "item_atlases"
DEV_ITEMS_ROOT = PROJECT_ROOT / "devspace" / "items"
MOD_ITEMS_DIR = PROJECT_ROOT / "Items" / "Medical"
FILELIST_PATH = PROJECT_ROOT / "filelist.xml"

ICON_ATLAS_TEXTURE = "%ModDir%/Items/Medical/icons.png"
SPRITE_ATLAS_TEXTURE = "%ModDir%/Items/Medical/sprites.png"


@dataclass(frozen=True)
class OverrideAsset:
    item: str
    identifier: str
    folder: Path
    icon_sourcerect: str
    sprite_sourcerect: str


@dataclass(frozen=True)
class VanillaItem:
    identifier: str
    source_xml: Path
    element: ET.Element


def load_atlas_entries(csv_path: Path) -> dict[tuple[str, str], str]:
    entries: dict[tuple[str, str], str] = {}
    with csv_path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            entries[(row["item"], row["identifier"])] = row["sourcerect"]
    return entries


def iter_item_folders() -> list[tuple[str, str, Path]]:
    item_folders: list[tuple[str, str, Path]] = []
    for item_dir in sorted(DEV_ITEMS_ROOT.iterdir()):
        identifiers_dir = item_dir / "items"
        if not item_dir.is_dir() or not identifiers_dir.is_dir():
            continue

        for identifier_dir in sorted(identifiers_dir.iterdir()):
            if identifier_dir.is_dir():
                item_folders.append((item_dir.name, identifier_dir.name, identifier_dir))
    return item_folders


def load_override_assets() -> list[OverrideAsset]:
    icon_entries = load_atlas_entries(ATLAS_DIR / "icons.csv")
    sprite_entries = load_atlas_entries(ATLAS_DIR / "sprites.csv")
    item_folders = iter_item_folders()

    duplicate_identifiers: dict[str, list[str]] = defaultdict(list)
    missing_icons: list[str] = []
    missing_sprites: list[str] = []
    assets: list[OverrideAsset] = []

    for item, identifier, folder in item_folders:
        key = (item, identifier)
        display_key = f"{item}/{identifier}"
        duplicate_identifiers[identifier].append(display_key)

        icon_sourcerect = icon_entries.get(key)
        sprite_sourcerect = sprite_entries.get(key)
        if icon_sourcerect is None:
            missing_icons.append(display_key)
        if sprite_sourcerect is None:
            missing_sprites.append(display_key)
        if icon_sourcerect is None or sprite_sourcerect is None:
            continue

        assets.append(
            OverrideAsset(
                item=item,
                identifier=identifier,
                folder=folder,
                icon_sourcerect=icon_sourcerect,
                sprite_sourcerect=sprite_sourcerect,
            )
        )

    conflicts = {
        identifier: display_keys
        for identifier, display_keys in duplicate_identifiers.items()
        if len(display_keys) > 1
    }
    if conflicts:
        lines = [
            f"- {identifier}: {', '.join(display_keys)}"
            for identifier, display_keys in sorted(conflicts.items())
        ]
        raise RuntimeError(
            "Cannot build XML overrides; multiple asset folders target the same item identifier:\n"
            + "\n".join(lines)
        )

    if missing_icons or missing_sprites:
        details: list[str] = []
        if missing_icons:
            details.append("missing icon atlas entries: " + ", ".join(sorted(missing_icons)))
        if missing_sprites:
            details.append("missing sprite atlas entries: " + ", ".join(sorted(missing_sprites)))
        raise RuntimeError(
            "Cannot build XML overrides; rebuild item atlases first or remove stale item folders:\n"
            + "\n".join(details)
        )

    if not assets:
        raise RuntimeError(f"No override item folders found under {DEV_ITEMS_ROOT}")

    return assets


def find_vanilla_items(identifiers: set[str]) -> dict[str, VanillaItem]:
    found: dict[str, VanillaItem] = {}
    duplicates: dict[str, list[Path]] = defaultdict(list)

    for xml_path in sorted(CONTENT_ITEMS_ROOT.rglob("*.xml")):
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError:
            continue

        for child in root:
            identifier = child.attrib.get("identifier")
            if identifier not in identifiers:
                continue

            if identifier in found:
                duplicates[identifier].append(xml_path)
                continue

            found[identifier] = VanillaItem(
                identifier=identifier,
                source_xml=xml_path,
                element=child,
            )

    if duplicates:
        lines = []
        for identifier, paths in sorted(duplicates.items()):
            first_path = found[identifier].source_xml
            all_paths = [first_path, *paths]
            relative_paths = [str(path.relative_to(BAROTRAUMA_ROOT)) for path in all_paths]
            lines.append(f"- {identifier}: {', '.join(relative_paths)}")
        raise RuntimeError(
            "Cannot build XML overrides; multiple vanilla item definitions share an identifier:\n"
            + "\n".join(lines)
        )

    missing = sorted(identifiers - set(found))
    if missing:
        raise RuntimeError("Missing vanilla item definitions: " + ", ".join(missing))

    return found


def replace_or_append(parent: ET.Element, element: ET.Element) -> None:
    existing = parent.find(element.tag)
    if existing is None:
        parent.append(element)
        return
    index = list(parent).index(existing)
    parent.remove(existing)
    parent.insert(index, element)


def make_icon(existing: ET.Element | None, sourcerect: str) -> ET.Element:
    attrs = dict(existing.attrib) if existing is not None else {}
    attrs["texture"] = ICON_ATLAS_TEXTURE
    attrs["sourcerect"] = sourcerect
    attrs.setdefault("origin", "0.5,0.5")
    return ET.Element("InventoryIcon", attrs)


def make_sprite(existing: ET.Element | None, sourcerect: str) -> ET.Element:
    attrs = dict(existing.attrib) if existing is not None else {}
    attrs["texture"] = SPRITE_ATLAS_TEXTURE
    attrs["sourcerect"] = sourcerect
    attrs.setdefault("depth", "0.6")
    attrs.setdefault("origin", "0.5,0.5")
    return ET.Element("Sprite", attrs)


def make_override_item(asset: OverrideAsset, vanilla_item: VanillaItem) -> ET.Element:
    item = deepcopy(vanilla_item.element)
    replace_or_append(item, make_icon(item.find("InventoryIcon"), asset.icon_sourcerect))
    replace_or_append(item, make_sprite(item.find("Sprite"), asset.sprite_sourcerect))
    return item


def output_path_for_vanilla_xml(path: Path) -> Path:
    return MOD_ITEMS_DIR / path.name


def group_assets_by_source_xml(
    assets: list[OverrideAsset],
    vanilla_items: dict[str, VanillaItem],
) -> dict[Path, list[OverrideAsset]]:
    grouped: dict[Path, list[OverrideAsset]] = defaultdict(list)
    output_names: dict[str, Path] = {}

    for asset in assets:
        source_xml = vanilla_items[asset.identifier].source_xml
        output_path = output_path_for_vanilla_xml(source_xml)
        existing_source = output_names.get(output_path.name)
        if existing_source is not None and existing_source != source_xml:
            raise RuntimeError(
                f"Cannot write {output_path.relative_to(PROJECT_ROOT)}; both "
                f"{existing_source.relative_to(BAROTRAUMA_ROOT)} and "
                f"{source_xml.relative_to(BAROTRAUMA_ROOT)} use that output name"
            )
        output_names[output_path.name] = source_xml
        grouped[source_xml].append(asset)

    return dict(sorted(grouped.items(), key=lambda entry: str(entry[0])))


def indent(element: ET.Element, level: int = 0) -> None:
    indent_text = "\n" + level * "  "
    child_indent_text = "\n" + (level + 1) * "  "
    children = list(element)
    if children:
        if not element.text or not element.text.strip():
            element.text = child_indent_text
        for child in children:
            indent(child, level + 1)
        if not children[-1].tail or not children[-1].tail.strip():
            children[-1].tail = indent_text
    if level and (not element.tail or not element.tail.strip()):
        element.tail = indent_text


def write_override_xml(
    source_xml: Path,
    assets: list[OverrideAsset],
    vanilla_items: dict[str, VanillaItem],
) -> Path:
    override = ET.Element("Override")
    items = ET.SubElement(override, "Items")

    for asset in sorted(assets, key=lambda candidate: candidate.identifier):
        vanilla_item = vanilla_items[asset.identifier]
        item_name = vanilla_item.element.attrib.get("name") or vanilla_item.element.tag
        items.append(
            ET.Comment(
                f" Override vanilla {item_name} ({asset.identifier}) visuals with {asset.item} assets. "
            )
        )
        items.append(make_override_item(asset, vanilla_item))

    indent(override)
    output_path = output_path_for_vanilla_xml(source_xml)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(override).write(output_path, encoding="utf-8", xml_declaration=True)
    return output_path


def update_filelist(output_paths: list[Path]) -> None:
    tree = ET.parse(FILELIST_PATH)
    root = tree.getroot()
    wanted_files = {
        f"%ModDir%/Items/Medical/{path.name}"
        for path in sorted(output_paths, key=lambda candidate: candidate.name)
    }
    existing_files = {
        child.attrib.get("file")
        for child in root
        if child.tag == "Item" and child.attrib.get("file")
    }

    for file_path in sorted(wanted_files - existing_files):
        root.append(ET.Element("Item", {"file": file_path}))

    indent(root)
    tree.write(FILELIST_PATH, encoding="utf-8", xml_declaration=True)


def main() -> None:
    assets = load_override_assets()
    vanilla_items = find_vanilla_items({asset.identifier for asset in assets})
    grouped_assets = group_assets_by_source_xml(assets, vanilla_items)

    output_paths = [
        write_override_xml(source_xml, grouped, vanilla_items)
        for source_xml, grouped in grouped_assets.items()
    ]
    update_filelist(output_paths)

    for output_path in output_paths:
        print(f"Wrote {output_path.relative_to(PROJECT_ROOT)}")
    print(f"Updated {FILELIST_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Updated {len(assets)} item overrides across {len(output_paths)} XML files")


if __name__ == "__main__":
    main()
