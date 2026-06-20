from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BAROTRAUMA_ROOT = PROJECT_ROOT.parents[1]
ATLAS_DIR = PROJECT_ROOT / "devspace" / "scripts" / "item_atlases"
DART_ITEMS_DIR = PROJECT_ROOT / "devspace" / "items" / "dart_syringe" / "items"
OUT_PATH = PROJECT_ROOT / "Items" / "Medical" / "poisons.xml"

POISON_IDS = [
    "cyanide",
    "sufforin",
    "morbusine",
    "deliriumine",
    "paralyzant",
    "radiotoxin",
    "calyxanide",
    "sulphuricacid",
    "raptorbaneextract",
    "europabrew",
    "chloralhydrate",
]

VANILLA_FILES = [
    BAROTRAUMA_ROOT / "Content" / "Items" / "Medical" / "poisons.xml",
    BAROTRAUMA_ROOT / "Content" / "Items" / "Medical" / "medical.xml",
    BAROTRAUMA_ROOT / "Content" / "Items" / "Jobgear" / "Medic" / "medic_talent_items.xml",
]


def load_atlas_entries(csv_path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    with csv_path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["item"] == "dart_syringe":
                entries[row["identifier"]] = row["sourcerect"]
    return entries


def find_vanilla_items() -> dict[str, ET.Element]:
    found: dict[str, ET.Element] = {}
    for path in VANILLA_FILES:
        root = ET.parse(path).getroot()
        for child in root:
            identifier = child.attrib.get("identifier")
            if identifier in POISON_IDS and identifier not in found:
                found[identifier] = child
    missing = sorted(set(POISON_IDS) - set(found))
    if missing:
        raise RuntimeError(f"Missing vanilla item definitions: {', '.join(missing)}")
    return found


def replace_or_append(parent: ET.Element, element: ET.Element) -> None:
    existing = parent.find(element.tag)
    if existing is None:
        parent.append(element)
        return
    index = list(parent).index(existing)
    parent.remove(existing)
    parent.insert(index, element)


def make_icon(sourcerect: str) -> ET.Element:
    return ET.Element(
        "InventoryIcon",
        {
            "texture": "%ModDir%/Items/Medical/icons.png",
            "sourcerect": sourcerect,
            "origin": "0.5,0.5",
        },
    )


def make_sprite(sourcerect: str) -> ET.Element:
    return ET.Element(
        "Sprite",
        {
            "texture": "%ModDir%/Items/Medical/sprites.png",
            "sourcerect": sourcerect,
            "depth": "0.6",
            "origin": "0.5,0.5",
        },
    )


def make_body(identifier: str) -> ET.Element:
    sprite_path = DART_ITEMS_DIR / identifier / "sprite.png"
    width, height = Image.open(sprite_path).size
    return ET.Element(
        "Body",
        {
            "width": str(width),
            "height": str(height),
            "density": "10.2",
            "waterdragcoefficient": "1",
        },
    )


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


def main() -> None:
    icon_entries = load_atlas_entries(ATLAS_DIR / "icons.csv")
    sprite_entries = load_atlas_entries(ATLAS_DIR / "sprites.csv")
    vanilla_items = find_vanilla_items()

    missing_icons = sorted(set(POISON_IDS) - set(icon_entries))
    missing_sprites = sorted(set(POISON_IDS) - set(sprite_entries))
    if missing_icons or missing_sprites:
        raise RuntimeError(f"Missing atlas entries: icons={missing_icons}, sprites={missing_sprites}")

    override = ET.Element("Override")
    items = ET.SubElement(override, "Items")
    for identifier in POISON_IDS:
        items.append(ET.Comment(f" Override vanilla {identifier} visuals with dart_syringe assets. "))
        item = deepcopy(vanilla_items[identifier])
        replace_or_append(item, make_icon(icon_entries[identifier]))
        replace_or_append(item, make_sprite(sprite_entries[identifier]))
        replace_or_append(item, make_body(identifier))
        items.append(item)

    indent(override)
    tree = ET.ElementTree(override)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUT_PATH, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUT_PATH.relative_to(PROJECT_ROOT)} ({len(POISON_IDS)} overrides)")


if __name__ == "__main__":
    main()
