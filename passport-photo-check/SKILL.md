---
name: passport-photo-check
description: Verifies each photo in a tiled print-lab layout JPEG (e.g., 4×6 Walgreens sheet) against official ID/passport requirements — visually (face proportion, expression, background) and dimensionally (exact mm via pixel analysis). Use when confirming a layout is compliant before sending to the print lab.
user-invocable: true
---

# Passport Photo Check

Given a print-lab layout JPEG (one image containing multiple tiled ID photos), this skill does two things:

1. **Visual compliance check** — Claude inspects each photo against the target country's official requirements (face proportion, expression, head tilt, background, lighting, glasses, etc.)
2. **Dimension check** — Python + PIL scans the pixel data to find exact photo boundaries and reports each photo's width and height in millimeters.

Pairs naturally with `/photo-print-layout`, which produces the layout file this skill checks.

## When to Use

- You have a print-lab JPEG (4×6, 5×7, etc.) with tiled ID or passport photos and want to verify compliance before printing
- You want to confirm the individual photo dimensions match the official spec (e.g., 33×48mm for Chinese passport)
- The country/document type is known (Chinese passport, US passport, UK biometric, etc.)

## Instructions

### Step 0: Prerequisites

Ensure Python 3 and Pillow are installed:

```bash
python3 -c "from PIL import Image; print('Pillow OK')" || pip3 install Pillow
```

### Step 1: Gather Inputs

Ask the user for:
1. **Layout JPEG path** — the tiled print-lab file (e.g., `~/passport_4x6_walgreens.jpg`)
2. **Document type / country** — to know which requirements to check against

Reference table of official requirements:

| Document type | Photo size (mm) | Face height | Background | Glasses |
|---|---|---|---|---|
| Chinese passport / visa | 33 × 48 | 28–33mm (58–69% of height) | White | Not allowed (since 2021) |
| US passport | 51 × 51 | 25–35mm (49–69%) | White or off-white | Not allowed |
| UK biometric passport | 35 × 45 | 29–34mm (64–76%) | Light grey or cream | Not allowed |
| Indian passport | 35 × 45 | ≥ 70% of frame | White | Not allowed |
| 1-inch 一寸 (China) | 25 × 35 | same as Chinese passport | White | Not allowed |
| 2-inch 二寸 (China) | 35 × 49 | same as Chinese passport | White | Not allowed |

### Step 2: Visual Inspection

Use the Read tool to load and view the layout image. Inspect every individual photo in the grid against the relevant checklist. Report pass / fail / borderline per criterion per row:

**Universal checklist:**
- [ ] Background is plain white (no shadows, no patterns)
- [ ] Face is forward-facing, not tilted left/right
- [ ] Gaze is straight into the camera (not downward or upward)
- [ ] Neutral expression, mouth closed
- [ ] Eyes fully open
- [ ] No glasses
- [ ] No hat or head covering (unless religious/medical)
- [ ] Even lighting — no harsh shadows on face or background
- [ ] Color photo (not black and white)

**Face proportion check (most common failure):**
- Estimate what fraction of the photo height the face (chin to crown) occupies
- Chinese/1-inch/2-inch: must be ≥ 58% (28–33mm in a 48mm photo)
- If face is small with significant chest/body visible below chin → likely FAIL

Report a table like:

| Photo | Background | Face proportion | Head tilt | Gaze | Expression | Eyes | Glasses | Lighting | Result |
|---|---|---|---|---|---|---|---|---|---|
| Row 1 Left | Pass | ~55% — FAIL | Pass | Borderline | Pass | Pass | Pass | Pass | **FAIL** |
| ... | | | | | | | | | |

### Step 3: Dimension Measurement

Resolve the skill directory, then run the bundled measurement script:

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/passport-photo-check/SKILL.md)")"
python3 "$SKILL_DIR/scripts/measure_photos.py" "<layout_path>"
```

The script auto-reads DPI from image metadata. To override:

```bash
python3 "$SKILL_DIR/scripts/measure_photos.py" "<layout_path>" --dpi 600
```

### Step 4: Report Results

Present a final summary:

**Dimension check:**

| Photo | Measured width | Measured height | Required | Result |
|---|---|---|---|---|
| All photos | 33.0 mm | 48.0 mm | 33 × 48 mm | Pass |

**Visual check summary:** (see Step 2 table)

**Overall verdict:** Pass / Fail with specific action items if any photos fail.

Common failure actions:
- Face too small → re-crop source photo tighter, re-run `/photo-print-layout`
- Gaze not straight → retake photo
- Background not white → background replacement or retake
- Glasses → retake without glasses

## Example Invocations

```
/passport-photo-check
```
→ Interactive; Claude asks for the layout JPEG path and document type

```
/passport-photo-check ~/passport_4x6_walgreens.jpg chinese-passport
```
→ Check layout against Chinese passport requirements directly

## Output

**Sample output** (illustrative values):

```
Full image: 1200x1800px = 101.6mm x 152.4mm at 300 DPI

Dimension check:
  Col 1: 390px = 33.0mm  Col 2: 390px = 33.0mm
  Row 1: 567px = 48.0mm  Row 2: 568px = 48.1mm  Row 3: 567px = 48.0mm
  → All photos: 33mm × 48mm ✓ (required: 33 × 48mm)

Visual check:
  Row 1: face ~55% of height → borderline FAIL (need ≥58%)
  Row 2: face ~60% → borderline
  Row 3: face ~65% → PASS
  Background, expression, gaze, lighting: all PASS across all photos

Overall: FAIL — face too small in rows 1–2. Re-crop source photo and re-run /photo-print-layout.
```

## Requirements

- Python 3
- Pillow: `pip3 install Pillow`
- Layout JPEG at 300 DPI (standard photo lab output)

## Supported Inputs / Edge Cases

- **2×3 grid (6 photos)**: standard 4×6 output from `/photo-print-layout` — fully supported
- **2×2 or other grids**: script auto-detects columns and rows from white-gap analysis
- **No gap between photos**: content-boundary detection still works; gap_cols list will be empty — report total content width / number of columns instead
- **Non-300 DPI**: run `sips` to get actual DPI and override the `DPI` variable
- **HEIC source**: convert first — `sips -s format jpeg photo.heic --out photo.jpg`
- **Portrait vs landscape canvas**: script is orientation-agnostic; it reads pixel dimensions directly

## Skill Structure

```
passport-photo-check/
├── SKILL.md    (this file — skill definition Claude executes)
├── README.md   (user-facing docs)
└── scripts/
    └── measure_photos.py   (pixel-level dimension measurement)
```
