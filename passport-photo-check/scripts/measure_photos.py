#!/usr/bin/env python3
"""Measure individual photo dimensions in a tiled print-lab layout JPEG.

Usage: measure_photos.py <layout_path> [--dpi DPI]
"""
import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("layout_path")
parser.add_argument("--dpi", type=int, default=300)
args = parser.parse_args()

DPI = args.dpi
img = Image.open(args.layout_path)

if hasattr(img, 'info') and 'dpi' in img.info:
    meta_dpi = img.info['dpi']
    if isinstance(meta_dpi, tuple):
        meta_dpi = meta_dpi[0]
    if meta_dpi and int(meta_dpi) != DPI:
        print(f"Note: image metadata reports {int(meta_dpi)} DPI; using that instead of {DPI}")
        DPI = int(meta_dpi)

gray = img.convert('L')
W, H = img.size
pixels = list(gray.getdata())

def col_pixels(x):
    return [pixels[y * W + x] for y in range(H)]

def row_pixels(y):
    return pixels[y * W:(y + 1) * W]

content_left   = next(x for x in range(W)        if any(p < 240 for p in col_pixels(x)))
content_right  = next(x for x in range(W-1,-1,-1) if any(p < 240 for p in col_pixels(x)))
content_top    = next(y for y in range(H)        if any(p < 240 for p in row_pixels(y)))
content_bottom = next(y for y in range(H-1,-1,-1) if any(p < 240 for p in row_pixels(y)))

print(f"Full image: {W}x{H}px = {W/DPI*25.4:.1f}mm x {H/DPI*25.4:.1f}mm at {DPI} DPI")
print(f"Content area: {content_right-content_left+1} x {content_bottom-content_top+1} px")

gap_cols = [x for x in range(content_left, content_right+1)
            if all(pixels[y*W+x] > 240 for y in range(content_top, content_bottom+1))]

def group_runs(positions):
    if not positions:
        return []
    groups, start = [], positions[0]
    for i in range(1, len(positions)):
        if positions[i] != positions[i-1] + 1:
            groups.append((start, positions[i-1]))
            start = positions[i]
    groups.append((start, positions[-1]))
    return groups

col_gaps = group_runs(gap_cols)
row_gap_rows = [y for y in range(content_top, content_bottom+1)
                if all(pixels[y*W+x] > 240 for x in range(content_left, content_right+1))]
row_gaps = group_runs(row_gap_rows)
sig_row_gaps = [(s, e) for s, e in row_gaps if e - s >= 3]

print(f"\nColumn gaps: {col_gaps}")
print(f"Row gaps (significant): {sig_row_gaps}")

if col_gaps:
    main_gap = max(col_gaps, key=lambda g: g[1] - g[0])
    w1 = main_gap[0] - content_left
    w2 = content_right - main_gap[1]
    print(f"\nPhoto widths:  col1={w1}px={w1/DPI*25.4:.1f}mm  col2={w2}px={w2/DPI*25.4:.1f}mm")

if len(sig_row_gaps) >= 2:
    g1, g2 = sig_row_gaps[0], sig_row_gaps[1]
    h1 = g1[0] - content_top
    h2 = g2[0] - g1[1]
    h3 = content_bottom - g2[1]
    print(f"Photo heights: row1={h1}px={h1/DPI*25.4:.1f}mm  row2={h2}px={h2/DPI*25.4:.1f}mm  row3={h3}px={h3/DPI*25.4:.1f}mm")
elif len(sig_row_gaps) == 1:
    g1 = sig_row_gaps[0]
    h1 = g1[0] - content_top
    h2 = content_bottom - g1[1]
    print(f"Photo heights: row1={h1}px={h1/DPI*25.4:.1f}mm  row2={h2}px={h2/DPI*25.4:.1f}mm")
