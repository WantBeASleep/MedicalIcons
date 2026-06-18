from __future__ import annotations

import argparse
import csv
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


def parse_int_list(value: str, expected_count: int) -> list[int]:
    parts = [int(part.strip()) for part in value.split(",")]
    if len(parts) != expected_count:
        raise ValueError(f"Expected {expected_count} comma-separated integers, got {value!r}.")
    return parts


def iter_with_parents(root: ET.Element):
    stack: list[tuple[ET.Element, list[ET.Element]]] = [(root, [])]
    while stack:
        node, parents = stack.pop()
        yield node, parents
        stack.extend((child, parents + [node]) for child in reversed(list(node)))


def ancestor_identifier(parents: list[ET.Element]) -> str:
    for parent in reversed(parents):
        identifier = parent.attrib.get("identifier")
        if identifier:
            return identifier
    return ""


def find_colored_icon_entries(xml_paths: list[Path], barotrauma_root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for xml_path in xml_paths:
        root = ET.parse(xml_path).getroot()
        for node, parents in iter_with_parents(root):
            if node.tag.lower() != "icon":
                continue
            texture = node.attrib.get("texture", "").lower()
            source_rect = node.attrib.get("sourcerect")
            color_value = node.attrib.get("color")
            if "mainiconsatlas.png" not in texture or not source_rect or not color_value:
                continue

            rect = parse_int_list(source_rect, 4)
            color = parse_int_list(color_value, 4)
            entries.append(
                {
                    "identifier": ancestor_identifier(parents),
                    "source_xml": str(xml_path.relative_to(barotrauma_root)),
                    "source_rect": source_rect,
                    "color": color_value,
                    "x": rect[0],
                    "y": rect[1],
                    "width": rect[2],
                    "height": rect[3],
                    "color_r": color[0],
                    "color_g": color[1],
                    "color_b": color[2],
                    "color_a": color[3],
                }
            )
    return entries


def new_tinted_icon(source_atlas: Image.Image, entry: dict[str, object]) -> Image.Image:
    x = int(entry["x"])
    y = int(entry["y"])
    width = int(entry["width"])
    height = int(entry["height"])
    tint_r = int(entry["color_r"])
    tint_g = int(entry["color_g"])
    tint_b = int(entry["color_b"])
    tint_a = int(entry["color_a"])

    source = source_atlas.crop((x, y, x + width, y + height)).convert("RGBA")
    output = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    source_pixels = source.load()
    output_pixels = output.load()

    for pixel_y in range(height):
        for pixel_x in range(width):
            red, green, blue, alpha = source_pixels[pixel_x, pixel_y]
            if alpha == 0:
                continue
            intensity = ((red + green + blue) / 3.0) / 255.0
            output_pixels[pixel_x, pixel_y] = (
                min(255, round(tint_r * intensity)),
                min(255, round(tint_g * intensity)),
                min(255, round(tint_b * intensity)),
                round((alpha * tint_a) / 255.0),
            )

    return output


def build_atlas(
    barotrauma_root: Path,
    output_atlas_name: str,
    output_map_name: str,
    columns: int,
) -> None:
    if columns < 1:
        raise ValueError("Columns must be 1 or greater.")

    script_dir = Path(__file__).resolve().parent
    afflictions_path = barotrauma_root / "Content" / "Afflictions.xml"
    talent_afflictions_dir = barotrauma_root / "Content" / "Talents"
    source_atlas_path = barotrauma_root / "Content" / "UI" / "MainIconsAtlas.png"
    output_atlas_path = script_dir / output_atlas_name
    output_map_path = script_dir / output_map_name

    if not afflictions_path.exists():
        raise FileNotFoundError(f"Afflictions.xml not found: {afflictions_path}")
    if not source_atlas_path.exists():
        raise FileNotFoundError(f"MainIconsAtlas.png not found: {source_atlas_path}")

    xml_paths = [afflictions_path]
    if talent_afflictions_dir.exists():
        xml_paths.extend(sorted(talent_afflictions_dir.rglob("Afflictions*.xml")))
    xml_paths = list(dict.fromkeys(xml_paths))

    entries = find_colored_icon_entries(xml_paths, barotrauma_root)
    if not entries:
        raise ValueError(f"No colored MainIconsAtlas icon entries found in {afflictions_path}")

    max_width = max(int(entry["width"]) for entry in entries)
    max_height = max(int(entry["height"]) for entry in entries)
    rows = math.ceil(len(entries) / columns)
    output_atlas = Image.new("RGBA", (columns * max_width, rows * max_height), (0, 0, 0, 0))

    source_atlas = Image.open(source_atlas_path).convert("RGBA")
    map_rows: list[dict[str, object]] = []

    for index, entry in enumerate(entries):
        column = index % columns
        row = index // columns
        dest_x = column * max_width
        dest_y = row * max_height
        tinted = new_tinted_icon(source_atlas, entry)
        output_atlas.alpha_composite(tinted, (dest_x, dest_y))
        map_rows.append(
            {
                "index": index,
                "identifier": entry["identifier"],
                "source_xml": entry["source_xml"],
                "source_texture": "Content/UI/MainIconsAtlas.png",
                "source_rect": entry["source_rect"],
                "color": entry["color"],
                "output_texture": output_atlas_name,
                "output_rect": f"{dest_x},{dest_y},{entry['width']},{entry['height']}",
            }
        )

    output_atlas.save(output_atlas_path)
    with output_map_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(map_rows[0].keys()))
        writer.writeheader()
        writer.writerows(map_rows)

    print(f"Wrote {len(entries)} colored status icons.")
    print(f"Atlas: {output_atlas_path}")
    print(f"Map:   {output_map_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--barotrauma-root", default=r"D:\SteamLibrary\steamapps\common\Barotrauma")
    parser.add_argument("--output-atlas-name", default="ColoredStatusIconsAtlas.png")
    parser.add_argument("--output-map-name", default="ColoredStatusIconsAtlas.csv")
    parser.add_argument("--columns", type=int, default=8)
    args = parser.parse_args()

    build_atlas(
        barotrauma_root=Path(args.barotrauma_root),
        output_atlas_name=args.output_atlas_name,
        output_map_name=args.output_map_name,
        columns=args.columns,
    )


if __name__ == "__main__":
    main()
