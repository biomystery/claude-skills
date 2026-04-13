---
name: photo-year-collage
description: Create a year-labeled photo collage from a folder of annual photos. Designed for China visa applications requiring facial-change documentation (历年生活照片), but works for any year-based photo timeline.
user-invocable: true
---

# Photo Year Collage

Creates a chronological photo collage grid with year labels from a folder of photos named by year. Handles HEIC, JPEG, and PNG formats automatically, including HEIC conversion on macOS.

## When to Use

- User needs to generate a collage of annual/yearly photos
- China visa application requires proof of facial changes over time (面相变化)
- User wants to rotate specific year photos before generating the collage
- User provides a folder path or is already in a photo folder

## Instructions

### Step 1: Identify the Photo Folder

If the user hasn't specified a folder, use the current working directory. List the files to confirm they contain year-named photos (filenames starting with a 4-digit year).

### Step 2: Handle Rotation Requests (Optional)

If the user wants to rotate specific year photos before generating the collage:

```bash
# Rotate clockwise 90° using macOS sips (handles HEIC, JPEG, PNG)
sips -r 90 "<filename>"

# Rotate counter-clockwise 90°
sips -r -90 "<filename>"

# Rotate 180°
sips -r 180 "<filename>"
```

Apply to all files matching the requested years, then confirm before proceeding to collage generation.

### Step 3: Run the Collage Script

Use the bundled script:

```bash
python3 "$SKILL_DIR/scripts/create_collage.py" "<photo_folder>" [output_filename]
```

- `<photo_folder>`: Path to folder containing year-named photos
- `output_filename` (optional): defaults to `photo_collage_年度照片.jpg`

The script will:
1. Auto-detect all photos (JPEG, PNG, HEIC) in the folder
2. Extract the year from each filename (first 4 digits)
3. Convert HEIC files temporarily using macOS `sips`
4. Create a grid collage (5 columns) with dark year-label banners
5. Save to the photo folder

### Step 4: Open and Confirm

```bash
open "<photo_folder>/photo_collage_年度照片.jpg"
```

Show the user the output path and confirm success.

## Example Interactions

**Basic collage generation:**
```
/photo-year-collage
```
→ Uses current directory, generates collage

**With rotation:**
```
User: rotate 2014, 2020 clockwise then make collage
```
→ Rotate those years, then generate collage

**Specific folder:**
```
/photo-year-collage ~/Documents/visa-photos
```
→ Uses specified folder

## Requirements

- **macOS**: `sips` (built-in) for HEIC conversion and rotation
- **Python 3** with **Pillow**: `pip install Pillow --break-system-packages`
  - Script will prompt to install if missing

## Output

A single high-quality JPEG (`photo_collage_年度照片.jpg`) placed in the photo folder, showing all photos in a 5-column grid, each labeled with its year in a dark banner.

## Skill Structure

```
photo-year-collage/
├── SKILL.md          (this file)
└── scripts/
    └── create_collage.py
```
