#!/usr/bin/env python3
"""
create_collage.py — Year-labeled photo collage generator

Usage:
    python3 create_collage.py <photo_folder> [output_filename]

Generates a chronological grid collage from a folder of year-named photos.
Supports JPEG, PNG, and HEIC (macOS sips required for HEIC).

Designed for China visa applications requiring annual facial-change photos
(历年生活照片), but works for any year-based photo timeline.
"""

import os
import re
import sys
import subprocess
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "--break-system-packages", "-q"])
    from PIL import Image, ImageDraw, ImageFont


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}

# Grid / thumbnail settings
COLS = 5
THUMB_W = 600
THUMB_H = 800
LABEL_H = 60
PADDING = 20
BG_COLOR = (255, 255, 255)
LABEL_BG = (40, 40, 40)
LABEL_FG = (255, 255, 255)
FONT_SIZE = 42
JPEG_QUALITY = 90


def extract_year(filename: str) -> str | None:
    """Return the first 4-digit year found in a filename, or None."""
    m = re.search(r"((?:19|20)\d{2})", filename)
    return m.group(1) if m else None


def heic_to_jpeg(heic_path: str, tmp_dir: str) -> str:
    """Convert a HEIC file to JPEG using macOS sips. Returns JPEG path."""
    out_path = os.path.join(tmp_dir, os.path.basename(heic_path) + ".jpg")
    result = subprocess.run(
        ["sips", "-s", "format", "jpeg", heic_path, "--out", out_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"sips failed for {heic_path}: {result.stderr.decode()}")
    return out_path


def load_photo(path: str, tmp_dir: str) -> Image.Image:
    """Load a photo, converting HEIC if needed."""
    ext = os.path.splitext(path)[1].lower()
    if ext in {".heic", ".heif"}:
        path = heic_to_jpeg(path, tmp_dir)
    return Image.open(path).convert("RGB")


def center_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Crop image to target aspect ratio, biasing slightly upward to favor faces."""
    w, h = img.size
    target_ratio = target_w / target_h
    actual_ratio = w / h
    if actual_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 4  # slightly above center → favor face
        img = img.crop((0, top, w, top + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def build_collage(photos: list[tuple[str, str]], output_path: str) -> None:
    """
    Build and save a collage.

    photos: list of (year_label, file_path) sorted by year
    """
    rows = (len(photos) + COLS - 1) // COLS
    canvas_w = COLS * (THUMB_W + PADDING) + PADDING
    canvas_h = rows * (THUMB_H + LABEL_H + PADDING) + PADDING

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    font = get_font(FONT_SIZE)

    with tempfile.TemporaryDirectory() as tmp_dir:
        for i, (year, fpath) in enumerate(photos):
            col = i % COLS
            row = i // COLS
            x = PADDING + col * (THUMB_W + PADDING)
            y = PADDING + row * (THUMB_H + LABEL_H + PADDING)

            try:
                img = load_photo(fpath, tmp_dir)
            except Exception as e:
                print(f"  WARNING: skipping {fpath}: {e}")
                continue

            img = center_crop(img, THUMB_W, THUMB_H)
            canvas.paste(img, (x, y))

            # Year label bar
            draw.rectangle(
                [x, y + THUMB_H, x + THUMB_W, y + THUMB_H + LABEL_H],
                fill=LABEL_BG,
            )
            bbox = draw.textbbox((0, 0), year, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                (x + (THUMB_W - tw) // 2, y + THUMB_H + (LABEL_H - th) // 2),
                year,
                font=font,
                fill=LABEL_FG,
            )

    canvas.save(output_path, "JPEG", quality=JPEG_QUALITY)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    folder = os.path.expanduser(sys.argv[1])
    output_name = sys.argv[2] if len(sys.argv) > 2 else "photo_collage_年度照片.jpg"
    output_path = os.path.join(folder, output_name)

    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a directory.")
        sys.exit(1)

    # Collect year → file mappings
    year_map: dict[str, str] = {}
    for fname in os.listdir(folder):
        if fname.startswith("."):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in SUPPORTED_EXTS:
            continue
        year = extract_year(fname)
        if year and fname != output_name:
            # Prefer files with longer names (more specific) if duplicate years
            if year not in year_map or len(fname) > len(year_map[year]):
                year_map[year] = os.path.join(folder, fname)

    if not year_map:
        print(f"No year-named photos found in '{folder}'.")
        sys.exit(1)

    photos = sorted(year_map.items())  # sort by year string
    print(f"Found {len(photos)} photos: {', '.join(y for y, _ in photos)}")
    print(f"Building collage ({COLS} columns)...")

    build_collage(photos, output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
