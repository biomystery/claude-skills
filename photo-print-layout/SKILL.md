---
name: photo-print-layout
description: Tiles a fixed-size ID/passport photo onto a standard print canvas (4x6, 5x7, etc.) at 300 DPI, auto-calculating the optimal grid, gaps, and margins. Use when preparing a print-ready JPEG for Walgreens, CVS, Costco, or any photo lab.
user-invocable: true
---

# Photo Print Layout

Takes a single ID or passport photo of known dimensions and arranges multiple copies on a standard print canvas (default: 4×6 inch) at 300 DPI. Auto-selects the best grid (cols × rows) that maximizes photo count while keeping clean margins. Outputs a print-ready JPEG.

## When to Use

- User has a passport/ID/visa photo and wants to print multiple copies on one sheet
- User is going to a photo lab (Walgreens, CVS, Costco) and needs a 4×6 or 5×7 print layout
- User specifies photo dimensions in mm or inches and a target print size

## Instructions

### Step 0: Gather Inputs

Ask (or infer from context):

1. **Photo file path** — the source image
2. **Photo dimensions** — width × height in mm (see reference table below)
3. **Canvas size** — print size in inches (default: `4x6`)
4. **Gap between photos** — in mm (default: `2`)
5. **Border?** — thin black cutting line around each photo (default: yes)

#### Common ID Photo Sizes (mm, width × height)

| Type | Width | Height |
|------|-------|--------|
| Chinese passport / visa | 33 | 48 |
| US passport | 51 | 51 |
| UK / EU biometric passport | 35 | 45 |
| Indian passport | 35 | 45 |
| Korean passport | 35 | 45 |
| Japanese passport | 35 | 45 |
| 1-inch (一寸, China) | 25 | 35 |
| 2-inch (二寸, China) | 35 | 49 |

#### Common Print Canvas Sizes

| Canvas | Inches | Typical use |
|--------|--------|-------------|
| 4×6 | 4x6 | Standard photo lab print |
| 5×7 | 5x7 | Larger sheet, more photos |
| 4×4 | 4x4 | Square format |
| 3.5×5 | 3.5x5 | Wallet size sheet |

### Step 1: Check Prerequisites

```bash
python3 -c "from PIL import Image; print('OK')" 2>&1 || pip3 install Pillow -q
```

### Step 2: Run the Layout Script

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/photo-print-layout/SKILL.md)")"
python3 "$SKILL_DIR/scripts/layout.py" \
  "<photo_path>" \
  <photo_width_mm> <photo_height_mm> \
  --canvas <WxH> \
  --gap <gap_mm> \
  --border \
  --out print_layout.jpg
```

**Example — Chinese passport photo on 4×6:**
```bash
python3 "$SKILL_DIR/scripts/layout.py" photo.jpg 33 48 --canvas 4x6 --gap 2 --border --out print_layout.jpg
```

**Example — US passport photo on 4×6:**
```bash
python3 "$SKILL_DIR/scripts/layout.py" photo.jpg 51 51 --canvas 4x6 --gap 2 --border --out print_layout.jpg
```

The script auto-tries both portrait and landscape canvas orientations and picks the one that fits more photos.

### Step 3: Show the Result

Read and display the output image to the user. Confirm:
- Number of photos on the sheet
- Left/right and top/bottom margins
- Output file path

### Step 4: Handle Layout Issues

#### Too few photos fit (e.g., only 2)
- Try a larger canvas: `--canvas 5x7`
- Reduce gap: `--gap 1`
- Check if photo dimensions are correct (common error: user swaps width/height)

#### Photos clip the edge (negative margin warning in script output)
- This means the photo is too wide for the canvas at the chosen column count
- Reduce columns by reducing gap or switching to a larger canvas
- The script enforces `min_margin_px=10` and will reduce column count automatically

#### User wants more/fewer photos
- Adjust `--gap` (smaller gap = more photos possible)
- Switch canvas size

### Step 5: Remind User How to Print

Suggest uploading `print_layout.jpg` to:
- **Walgreens** — walgreens.com/photo → Print Photos → 4×6
- **CVS** — cvs.com/photo
- **Costco Photo** — costcophotocenter.com
- Or any local photo lab that accepts JPEG uploads

Remind: order as a standard **4×6 print** (or matching canvas size), not "passport photo" — the layout is already sized correctly.

## Example Invocations

```
/photo-print-layout
```
→ Claude asks for photo path, dimensions, and canvas size, then generates layout

```
/photo-print-layout photo.jpg 33 48
```
→ Chinese passport photo on default 4×6 canvas

```
/photo-print-layout photo.jpg 51 51 --canvas 5x7
```
→ US passport photo on 5×7 canvas

## Output

- `print_layout.jpg` — print-ready JPEG at 300 DPI
- Console summary: grid dimensions, photo count, margin sizes

## Requirements

- Python 3 with Pillow (`pip3 install Pillow`)
- Source photo in JPEG, PNG, or any Pillow-supported format

## Skill Structure

```
photo-print-layout/
├── SKILL.md
├── README.md
└── scripts/
    └── layout.py
```
