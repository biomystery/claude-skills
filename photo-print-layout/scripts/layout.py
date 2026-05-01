#!/usr/bin/env python3
"""
photo-print-layout: Tile a fixed-size ID/passport photo onto a print canvas.

Usage:
    python3 layout.py <photo> <photo_w_mm> <photo_h_mm> [options]

Options:
    --canvas WxH       Canvas size in inches, e.g. 4x6 (default: 4x6)
    --dpi N            Resolution (default: 300)
    --gap N            Gap between photos in mm (default: 2)
    --border           Draw thin black border around each photo
    --out PATH         Output file (default: print_layout.jpg)
"""
import sys
import argparse
from PIL import Image, ImageDraw


def mm_to_px(mm, dpi):
    return round(mm * dpi / 25.4)


def in_to_px(inches, dpi):
    return round(inches * dpi)


def best_grid(photo_w_px, photo_h_px, canvas_w_px, canvas_h_px, gap_px, min_margin_px=10):
    """Return (cols, rows) maximizing photo count while keeping margins >= min_margin_px."""
    best = (1, 1)
    best_count = 0
    for cols in range(1, 20):
        for rows in range(1, 20):
            grid_w = cols * photo_w_px + (cols - 1) * gap_px
            grid_h = rows * photo_h_px + (rows - 1) * gap_px
            margin_x = (canvas_w_px - grid_w) // 2
            margin_y = (canvas_h_px - grid_h) // 2
            if margin_x >= min_margin_px and margin_y >= min_margin_px:
                count = cols * rows
                if count > best_count:
                    best_count = count
                    best = (cols, rows)
    return best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("photo")
    parser.add_argument("photo_w_mm", type=float)
    parser.add_argument("photo_h_mm", type=float)
    parser.add_argument("--canvas", default="4x6")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--gap", type=float, default=2.0)
    parser.add_argument("--border", action="store_true")
    parser.add_argument("--out", default="print_layout.jpg")
    args = parser.parse_args()

    dpi = args.dpi
    photo_w_px = mm_to_px(args.photo_w_mm, dpi)
    photo_h_px = mm_to_px(args.photo_h_mm, dpi)
    gap_px = mm_to_px(args.gap, dpi)

    cw_in, ch_in = map(float, args.canvas.lower().split("x"))
    canvas_w_px = in_to_px(cw_in, dpi)
    canvas_h_px = in_to_px(ch_in, dpi)

    # Try both canvas orientations, pick the one fitting more photos
    cols_p, rows_p = best_grid(photo_w_px, photo_h_px, canvas_w_px, canvas_h_px, gap_px)
    cols_l, rows_l = best_grid(photo_w_px, photo_h_px, canvas_h_px, canvas_w_px, gap_px)

    if cols_l * rows_l > cols_p * rows_p:
        cols, rows = cols_l, rows_l
        canvas_w_px, canvas_h_px = canvas_h_px, canvas_w_px
        orientation = "landscape"
    else:
        cols, rows = cols_p, rows_p
        orientation = "portrait"

    grid_w = cols * photo_w_px + (cols - 1) * gap_px
    grid_h = rows * photo_h_px + (rows - 1) * gap_px
    margin_x = (canvas_w_px - grid_w) // 2
    margin_y = (canvas_h_px - grid_h) // 2

    src = Image.open(args.photo).convert("RGB")
    photo = src.resize((photo_w_px, photo_h_px), Image.LANCZOS)

    canvas = Image.new("RGB", (canvas_w_px, canvas_h_px), (255, 255, 255))
    draw = ImageDraw.Draw(canvas) if args.border else None

    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (photo_w_px + gap_px)
            y = margin_y + row * (photo_h_px + gap_px)
            canvas.paste(photo, (x, y))
            if draw:
                draw.rectangle([x, y, x + photo_w_px - 1, y + photo_h_px - 1],
                                outline=(0, 0, 0), width=1)

    canvas.save(args.out, "JPEG", dpi=(dpi, dpi), quality=95)

    print(f"Saved: {args.out}")
    print(f"Canvas: {args.canvas}\" ({orientation}), {canvas_w_px}x{canvas_h_px}px @ {dpi}dpi")
    print(f"Photo:  {args.photo_w_mm}x{args.photo_h_mm}mm → {photo_w_px}x{photo_h_px}px")
    print(f"Grid:   {cols}x{rows} = {cols * rows} photos, gap={args.gap}mm")
    print(f"Margins: left/right={margin_x}px ({margin_x/dpi*25.4:.1f}mm), "
          f"top/bottom={margin_y}px ({margin_y/dpi*25.4:.1f}mm)")


if __name__ == "__main__":
    main()
