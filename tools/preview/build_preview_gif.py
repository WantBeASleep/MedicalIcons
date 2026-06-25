from argparse import ArgumentParser
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
VENDOR_DIR = PROJECT_ROOT / "_vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


LEGACY_PREVIEW_DIR = PROJECT_ROOT / "preview" / "legacy"
OUTPUT_PATH = PROJECT_ROOT / "preview" / "medical_icons_preview.gif"
FONT_DIR = PROJECT_ROOT / "source" / "fonts"

SLIDES = [
    ("before_after.png", "Before / After"),
    ("new_icons.png", "New medical item icons"),
    ("ampoule_items.png", "Ampoules"),
    ("vial_items.png", "Vials"),
    ("pocket_injector_items.png", "Pocket injectors"),
    ("dart_syringe_items.png", "Dart syringes"),
    ("insulin_syringe_items.png", "Insulin syringes"),
]


def parse_args():
    parser = ArgumentParser(
        description="Build an animated GIF preview from the archived static preview images."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=LEGACY_PREVIEW_DIR,
        help="Directory containing source PNG preview frames. Defaults to preview/legacy.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="GIF output path. Defaults to preview/medical_icons_preview.gif.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=960,
        help="Output GIF width in pixels.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=540,
        help="Output GIF height in pixels.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=1300,
        help="Duration of each content slide in milliseconds.",
    )
    parser.add_argument(
        "--transition-frames",
        type=int,
        default=5,
        help="Number of crossfade frames between slides.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned input and output files without writing the GIF.",
    )
    return parser.parse_args()


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def cover_frame(size: tuple[int, int], source: Path) -> Image.Image:
    width, height = size
    background = Image.open(source).convert("RGB")
    background = ImageOps.fit(background, size, Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(5))
    background = ImageEnhance.Brightness(background).enhance(0.34)
    background = ImageEnhance.Contrast(background).enhance(1.18)

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    title_font = load_font("bahnschrift.ttf", 74)
    subtitle_font = load_font("segoeui.ttf", 26)
    label_font = load_font("segoeuib.ttf", 20)

    title = "MEDICAL ICONS"
    subtitle = "Readable medicine at submarine speed"
    badge = "Barotrauma client-side UI mod"

    title_box = draw.textbbox((0, 0), title, font=title_font)
    subtitle_box = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    badge_box = draw.textbbox((0, 0), badge, font=label_font)

    title_x = (width - (title_box[2] - title_box[0])) // 2
    title_y = height // 2 - 88
    subtitle_x = (width - (subtitle_box[2] - subtitle_box[0])) // 2
    subtitle_y = title_y + 86
    badge_w = badge_box[2] - badge_box[0] + 44
    badge_h = 44
    badge_x = (width - badge_w) // 2
    badge_y = subtitle_y + 56

    draw.rounded_rectangle(
        (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
        radius=8,
        fill=(10, 16, 20, 196),
        outline=(108, 176, 168, 180),
        width=2,
    )
    draw.text((title_x + 3, title_y + 3), title, font=title_font, fill=(4, 8, 10, 210))
    draw.text((title_x, title_y), title, font=title_font, fill=(221, 246, 239, 255))
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(183, 211, 204, 255))
    draw.text((badge_x + 22, badge_y + 9), badge, font=label_font, fill=(213, 238, 231, 255))

    return Image.alpha_composite(background.convert("RGBA"), overlay).convert("P", palette=Image.Palette.ADAPTIVE)


def fit_frame(path: Path, size: tuple[int, int], label: str) -> Image.Image:
    frame = Image.open(path).convert("RGB")
    frame = ImageOps.fit(frame, size, Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font("segoeuib.ttf", 22)
    label_box = draw.textbbox((0, 0), label, font=font)
    padding_x = 18
    padding_y = 10
    x = 22
    y = 22
    draw.rounded_rectangle(
        (
            x,
            y,
            x + label_box[2] - label_box[0] + padding_x * 2,
            y + label_box[3] - label_box[1] + padding_y * 2,
        ),
        radius=7,
        fill=(5, 10, 12, 190),
        outline=(97, 150, 146, 150),
        width=1,
    )
    draw.text((x + padding_x, y + padding_y - 1), label, font=font, fill=(229, 241, 235, 255))
    return Image.alpha_composite(frame.convert("RGBA"), overlay).convert("P", palette=Image.Palette.ADAPTIVE)


def build_frames(input_dir: Path, size: tuple[int, int], transition_frames: int):
    slide_paths = [(input_dir / filename, label) for filename, label in SLIDES]
    missing = [path for path, _label in slide_paths if not path.exists()]
    if missing:
        missing_list = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing preview source files:\n{missing_list}")

    frames = [cover_frame(size, slide_paths[0][0])]
    frames.extend(fit_frame(path, size, label) for path, label in slide_paths)

    animated_frames = []
    durations = []
    for index, frame in enumerate(frames):
        animated_frames.append(frame)
        durations.append(1800 if index == 0 else None)
        next_frame = frames[(index + 1) % len(frames)]
        for step in range(1, transition_frames + 1):
            alpha = step / (transition_frames + 1)
            blended = Image.blend(frame.convert("RGB"), next_frame.convert("RGB"), alpha)
            animated_frames.append(blended.convert("P", palette=Image.Palette.ADAPTIVE))
            durations.append(70)

    return animated_frames, durations


def main():
    args = parse_args()
    size = (args.width, args.height)
    slide_paths = [args.input_dir / filename for filename, _label in SLIDES]

    if args.dry_run:
        print(f"Would write: {args.output}")
        print(f"Size: {args.width}x{args.height}")
        print("Would read:")
        for path in slide_paths:
            print(f"- {path}")
        return

    frames, durations = build_frames(args.input_dir, size, args.transition_frames)
    durations = [args.duration if duration is None else duration for duration in durations]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
