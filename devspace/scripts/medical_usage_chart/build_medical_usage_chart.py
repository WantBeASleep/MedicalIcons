from __future__ import annotations

import csv
import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BAROTRAUMA_ROOT = PROJECT_ROOT.parents[1]
VANILLA_MEDICAL_DIR = BAROTRAUMA_ROOT / "Content" / "Items" / "Medical"
OUTPUT_DIR = Path(__file__).resolve().parent

SOURCE_FILES = ("medical.xml", "poisons.xml", "buffs.xml")


@dataclass(frozen=True)
class ItemScore:
    urgency: float
    frequency: float
    group: str
    note: str


GROUP_COLORS = {
    "trauma": "#d94c3d",
    "resuscitation": "#d7831f",
    "blood": "#b23a60",
    "antidote": "#8067b7",
    "infection": "#2f8d6a",
    "oxygen": "#2e7bbf",
    "buff": "#c49b20",
    "poison": "#4d5966",
    "food_drink": "#6d9f3a",
    "material": "#8a8f99",
    "misc": "#5b6fb8",
}


OVERRIDES: dict[str, ItemScore] = {
    "antibleeding1": ItemScore(9.0, 9.5, "trauma", "Базовое лечение кровотечения и ожогов."),
    "antibleeding2": ItemScore(8.7, 7.6, "trauma", "Более сильное лечение ран, часто в аптечках."),
    "antibleeding3": ItemScore(8.8, 4.8, "trauma", "Сильный клей для тяжелых ран, но редкий."),
    "antidama1": ItemScore(8.0, 8.2, "trauma", "Частый анальгетик против урона, риск передоза."),
    "antidama2": ItemScore(8.7, 5.2, "trauma", "Сильный анальгетик для критических случаев."),
    "deusizine": ItemScore(9.7, 2.6, "resuscitation", "Почти паническое средство широкого профиля."),
    "antibloodloss1": ItemScore(8.0, 8.0, "blood", "Базовая компенсация кровопотери."),
    "antibloodloss2": ItemScore(8.6, 6.4, "blood", "Сильнее saline, полезно при тяжелой кровопотере."),
    "liquidoxygenite": ItemScore(9.4, 4.3, "oxygen", "Острая нехватка кислорода, но применяется ситуативно."),
    "pomegrenadeextract": ItemScore(8.3, 2.4, "oxygen", "Сильный кислородный эффект, нишевое средство."),
    "calyxanide": ItemScore(8.9, 3.9, "infection", "Срочно при husk infection, но случай не постоянный."),
    "antibiotics": ItemScore(6.6, 5.4, "infection", "Профилактика/лечение инфекций, не всегда срочно."),
    "stabilozine": ItemScore(7.3, 6.6, "misc", "Универсальный стабилизатор и компонент."),
    "opium": ItemScore(6.2, 5.6, "trauma", "Раннее обезболивание/сырье, но с рисками."),
    "adrenaline": ItemScore(7.7, 5.7, "resuscitation", "Боевой стимулятор и компонент."),
    "antipsychosis": ItemScore(6.0, 4.0, "antidote", "Психоз опасен, но встречается не каждый рейс."),
    "morbusineantidote": ItemScore(9.2, 1.7, "antidote", "Антидот нужен срочно, но только при конкретном яде."),
    "cyanideantidote": ItemScore(9.5, 1.8, "antidote", "Антидот к быстрому смертельному отравлению."),
    "sufforinantidote": ItemScore(9.3, 1.6, "antidote", "Срочный, редкий антидот."),
    "deliriumineantidote": ItemScore(8.8, 1.5, "antidote", "Редкий антидот от deliriumine."),
    "antirad": ItemScore(8.1, 2.0, "antidote", "Радиация опасна, но обычно ситуативна."),
    "antiparalysis": ItemScore(9.1, 1.9, "antidote", "Паралич требует быстрой реакции, но редок."),
    "antinarc": ItemScore(8.4, 4.2, "antidote", "Срочно при опиатной передозировке, но не расходуется постоянно."),
    "meth": ItemScore(6.9, 3.8, "buff", "Стимулятор для боя/спасения, не базовое лечение."),
    "steroids": ItemScore(5.8, 3.0, "buff", "Бафф силы, обычно плановое применение."),
    "hyperzine": ItemScore(6.7, 2.4, "buff", "Сильный бафф, но редкий и дорогой."),
    "tonicliquid": ItemScore(4.7, 4.1, "buff", "Усилитель длительности эффектов, скорее подготовка."),
    "ethanol": ItemScore(3.4, 5.5, "food_drink", "Часто доступен, медицинская срочность низкая."),
    "energydrink": ItemScore(3.9, 4.7, "food_drink", "Бытовой/баффовый расходник."),
    "proteinbar": ItemScore(2.4, 5.0, "food_drink", "Еда/легкий бафф, не срочная медицина."),
    "mindsense": ItemScore(4.5, 2.4, "buff", "Полезный редкий бафф."),
    "mindwipe": ItemScore(3.2, 1.4, "misc", "Нишевое средство."),
    "morbusine": ItemScore(8.6, 1.1, "poison", "Яд: высокая срочность как угроза, низкая частота лечения им."),
    "chloralhydrate": ItemScore(6.9, 1.8, "poison", "Снотворный яд, ситуативен."),
    "cyanide": ItemScore(9.6, 1.2, "poison", "Быстро смертельный яд."),
    "radiotoxin": ItemScore(8.2, 1.1, "poison", "Опасный, но редкий яд."),
    "sufforin": ItemScore(8.8, 1.1, "poison", "Опасный редкий яд."),
    "deliriumine": ItemScore(7.8, 1.1, "poison", "Редкий психоактивный яд."),
    "paralyzant": ItemScore(8.9, 1.3, "poison", "Паралич опасен и требует антидота."),
    "raptorbaneextract": ItemScore(5.2, 1.4, "poison", "Больше токсин/компонент, чем частая медицина."),
    "hallucinogenicbufotoxin": ItemScore(4.8, 1.2, "poison", "Нишевый токсин."),
    "sulphuricacid": ItemScore(5.6, 2.1, "poison", "Опасная химия и компонент."),
    "elastin": ItemScore(2.0, 5.0, "material", "Материал для крафта, не применяется срочно."),
}


def read_xml(path: Path) -> ET.Element:
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r">>\s*\n", ">\n", text)
    return ET.fromstring(text)


def lower_attr(element: ET.Element, name: str, default: str = "") -> str:
    for key, value in element.attrib.items():
        if key.lower() == name.lower():
            return value
    return default


def split_words(value: str) -> set[str]:
    return {part.strip().lower() for part in value.replace(";", ",").split(",") if part.strip()}


def collect_items() -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    seen: set[str] = set()

    for file_name in SOURCE_FILES:
        root = read_xml(VANILLA_MEDICAL_DIR / file_name)
        for element in root:
            identifier = lower_attr(element, "identifier")
            if not identifier or identifier in seen or lower_attr(element, "variantof"):
                continue
            seen.add(identifier)

            tags = split_words(lower_attr(element, "tags"))
            category = split_words(lower_attr(element, "category"))
            suitable = []
            reduces = []
            afflicts = []
            min_available = 0.0
            price_count = 0

            for node in element.iter():
                tag = node.tag.lower()
                if tag == "suitabletreatment":
                    suitable.append(lower_attr(node, "identifier") or lower_attr(node, "type"))
                elif tag == "reduceaffliction":
                    reduces.append(lower_attr(node, "identifier") or lower_attr(node, "type"))
                elif tag == "affliction":
                    afflicts.append(lower_attr(node, "identifier") or lower_attr(node, "type"))
                elif tag == "price":
                    price_count += 1
                    raw = lower_attr(node, "minavailable")
                    if raw:
                        try:
                            min_available += float(raw)
                        except ValueError:
                            pass

            items.append(
                {
                    "source_file": file_name,
                    "xml_tag": element.tag,
                    "identifier": identifier,
                    "category": ",".join(sorted(category)),
                    "tags": ",".join(sorted(tags)),
                    "suitable": ",".join(sorted(set(filter(None, suitable)))),
                    "reduces": ",".join(sorted(set(filter(None, reduces)))),
                    "afflicts": ",".join(sorted(set(filter(None, afflicts)))),
                    "price_count": price_count,
                    "min_available": min_available,
                }
            )
    return items


def infer_score(item: dict[str, object]) -> ItemScore:
    identifier = str(item["identifier"])
    if identifier in OVERRIDES:
        return OVERRIDES[identifier]

    blob = " ".join(
        str(item[key])
        for key in ("identifier", "xml_tag", "category", "tags", "suitable", "reduces", "afflicts")
    ).lower()
    tags = split_words(str(item["tags"]))
    min_available = float(item["min_available"])
    price_count = int(item["price_count"])

    urgency = 3.0
    frequency = 2.0
    group = "misc"
    notes = []

    if "poison" in tags:
        urgency += 3.5
        frequency -= 0.7
        group = "poison"
        notes.append("яд/токсин")
    if "medical" in tags or "medical" in str(item["category"]).lower():
        urgency += 1.0
        frequency += 1.0
    if "material" in str(item["category"]).lower() and "useinhealthinterface" not in blob:
        urgency -= 1.0
        group = "material"

    urgent_terms = {
        "bleeding": 3.2,
        "bloodloss": 3.0,
        "oxygenlow": 3.5,
        "stun": 2.5,
        "burn": 2.0,
        "internaldamage": 3.0,
        "paralysis": 3.4,
        "cyanidepoisoning": 4.0,
        "sufforinpoisoning": 3.7,
        "morbusinepoisoning": 3.6,
        "radiationsickness": 2.5,
        "huskinfection": 2.8,
        "infection": 2.1,
        "psychosis": 1.7,
    }
    common_terms = {
        "bleeding": 3.0,
        "burn": 2.2,
        "bloodloss": 2.6,
        "internaldamage": 2.1,
        "oxygenlow": 1.8,
        "infection": 1.5,
        "stun": 1.4,
        "huskinfection": 0.8,
        "psychosis": 0.9,
    }

    for term, amount in urgent_terms.items():
        if term in blob:
            urgency += amount
    for term, amount in common_terms.items():
        if term in blob:
            frequency += amount

    if any(term in blob for term in ("bleeding", "burn", "internaldamage")):
        group = "trauma"
    if "bloodloss" in blob:
        group = "blood"
    if "oxygenlow" in blob:
        group = "oxygen"
    if any(term in blob for term in ("poisoning", "radiationsickness", "paralysis")) and "poison" not in tags:
        group = "antidote"
    if any(term in blob for term in ("haste", "strengthen", "mindsense", "durationincrease")):
        group = "buff"
    if any(term in identifier for term in ("beer", "drink", "bar")):
        group = "food_drink"

    frequency += min(min_available / 12.0, 2.5)
    frequency += min(price_count / 6.0, 1.0)

    if not notes:
        notes.append("оценка по XML-эффектам и доступности")

    return ItemScore(
        urgency=max(1.0, min(10.0, round(urgency, 1))),
        frequency=max(1.0, min(10.0, round(frequency, 1))),
        group=group,
        note="; ".join(notes),
    )


def write_csv(rows: list[dict[str, object]]) -> Path:
    csv_path = OUTPUT_DIR / "medical_usage_chart.csv"
    fieldnames = [
        "identifier",
        "xml_tag",
        "source_file",
        "urgency",
        "frequency",
        "group",
        "note",
        "category",
        "tags",
        "suitable",
        "reduces",
        "afflicts",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
    return csv_path


def write_svg(rows: list[dict[str, object]]) -> Path:
    width = 1600
    height = 1100
    margin_left = 120
    margin_right = 360
    margin_top = 80
    margin_bottom = 120
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    def sx(value: float) -> float:
        return margin_left + (value - 1.0) / 9.0 * plot_w

    def sy(value: float) -> float:
        return margin_top + (10.0 - value) / 9.0 * plot_h

    group_offsets: dict[str, int] = {}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Segoe UI,Arial,sans-serif;fill:#1f252b} .tick{fill:#6b737c;font-size:18px}",
        ".label{font-size:15px}.small{font-size:14px;fill:#59616b}.title{font-size:34px;font-weight:700}",
        ".axis{stroke:#313941;stroke-width:2}.grid{stroke:#d9dee3;stroke-width:1}",
        "</style>",
        '<rect width="100%" height="100%" fill="#f7f4ee"/>',
        '<text class="title" x="80" y="46">Vanilla Barotrauma medical items: срочность x частота</text>',
        '<text class="small" x="80" y="72">Список предметов автоматически взят из Content/Items/Medical/*.xml; координаты 1-10 выставлены эвристикой.</text>',
    ]

    for tick in range(1, 11):
        x = sx(tick)
        y = sy(tick)
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{margin_top + plot_h}"/>')
        parts.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{margin_left + plot_w}" y2="{y:.1f}"/>')
        parts.append(f'<text class="tick" x="{x - 5:.1f}" y="{margin_top + plot_h + 32}">{tick}</text>')
        parts.append(f'<text class="tick" x="{margin_left - 42}" y="{y + 6:.1f}">{tick}</text>')

    parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}"/>')
    parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}"/>')
    parts.append(f'<text x="{margin_left + plot_w / 2 - 115:.1f}" y="{height - 42}" font-size="24" font-weight="600">срочность применения</text>')
    parts.append(f'<text x="28" y="{margin_top + plot_h / 2 + 120:.1f}" transform="rotate(-90 28 {margin_top + plot_h / 2 + 120:.1f})" font-size="24" font-weight="600">частота использования</text>')

    for row in rows:
        urgency = float(row["urgency"])
        frequency = float(row["frequency"])
        group = str(row["group"])
        color = GROUP_COLORS.get(group, "#555")
        index = group_offsets.get(group, 0)
        group_offsets[group] = index + 1
        dx = ((index % 5) - 2) * 4
        dy = (((index // 5) % 5) - 2) * 4
        x = sx(urgency) + dx
        y = sy(frequency) + dy
        label_x = x + 10
        label_y = y - 8
        identifier = html.escape(str(row["identifier"]))
        title = html.escape(f'{identifier}: urgency {urgency}, frequency {frequency}, {row["note"]}')
        parts.append(f'<g><title>{title}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>')
        parts.append(f'<text class="label" x="{label_x:.1f}" y="{label_y:.1f}">{identifier}</text></g>')

    legend_x = width - margin_right + 44
    legend_y = margin_top + 24
    parts.append(f'<text x="{legend_x}" y="{legend_y - 22}" font-size="22" font-weight="700">Группы</text>')
    for index, (group, color) in enumerate(GROUP_COLORS.items()):
        y = legend_y + index * 31
        parts.append(f'<circle cx="{legend_x}" cy="{y}" r="7" fill="{color}"/>')
        parts.append(f'<text x="{legend_x + 18}" y="{y + 6}" font-size="18">{html.escape(group)}</text>')

    notes_y = height - 118
    parts.append(f'<text class="small" x="{width - margin_right + 44}" y="{notes_y}">Правая верхняя зона: держать в быстром доступе.</text>')
    parts.append(f'<text class="small" x="{width - margin_right + 44}" y="{notes_y + 24}">Правая нижняя: срочно, но редко/нишево.</text>')
    parts.append(f'<text class="small" x="{width - margin_right + 44}" y="{notes_y + 48}">Левая верхняя: частые, но не панические.</text>')
    parts.append("</svg>")

    svg_path = OUTPUT_DIR / "medical_usage_chart.svg"
    svg_path.write_text("\n".join(parts), encoding="utf-8")
    return svg_path


def main() -> None:
    rows = []
    for item in collect_items():
        score = infer_score(item)
        rows.append(
            {
                **item,
                "urgency": f"{score.urgency:.1f}",
                "frequency": f"{score.frequency:.1f}",
                "group": score.group,
                "note": score.note,
            }
        )

    rows.sort(key=lambda row: (-float(row["urgency"]), -float(row["frequency"]), str(row["identifier"])))
    csv_path = write_csv(rows)
    svg_path = write_svg(rows)

    print(f"Items: {len(rows)}")
    print(f"CSV: {csv_path}")
    print(f"SVG: {svg_path}")


if __name__ == "__main__":
    main()
