# photo-year-collage

A Claude Code skill that generates a chronological photo collage grid with year labels from a folder of annual photos.

Originally created for China visa applications requiring proof of facial changes over time (**面相变化历年生活照片**), but useful for any year-based photo timeline.

## What It Does

- Scans a folder for photos named with a 4-digit year prefix
- Supports **JPEG, PNG, and HEIC** formats (auto-converts HEIC via macOS `sips`)
- Arranges photos in a 5-column grid, each labeled with its year
- Outputs a single high-quality JPEG: `photo_collage_年度照片.jpg`

## Install

Copy the skill into your Claude Code skills directory:

```bash
git clone https://github.com/frankwxu/photo-year-collage ~/.claude/skills/photo-year-collage
```

Claude Code will auto-detect it on next launch.

## Usage

### As a Claude Code skill

```
/photo-year-collage
```

Claude will use the current directory (or ask for a folder path), optionally rotate photos, and generate the collage.

### Standalone script

```bash
python3 scripts/create_collage.py <photo_folder> [output_filename]

# Example
python3 scripts/create_collage.py ~/visa-photos
```

### Rotate photos first (macOS)

```bash
# Clockwise 90°
sips -r 90 "2014-photo.jpg" "2020-photo.heic"

# Then generate collage
python3 scripts/create_collage.py ~/visa-photos
```

## Photo Naming Convention

Files must start with a 4-digit year. Common formats all work:

```
2013_PassportPhoto.jpg
2014-11-11_birthday.jpeg
2018.png
2020-12-02_18-42-27.heic
```

## Requirements

- **Python 3** + **Pillow** (`pip install Pillow`)
- **macOS `sips`** — for HEIC conversion (built into macOS, no install needed)

## Output Example

A 5-column grid collage with dark year banners, showing all photos from 2013–2026:

```
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ 2013 │ │ 2014 │ │ 2015 │ │ 2016 │ │ 2017 │
│ ████ │ │ ████ │ │ ████ │ │ ████ │ │ ████ │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘
┌──────┐ ┌──────┐ ...
│ 2018 │ │ 2019 │
└──────┘ └──────┘
```

## Skill Structure

```
photo-year-collage/
├── SKILL.md              ← Claude Code skill definition
├── README.md
└── scripts/
    └── create_collage.py ← Standalone Python script
```
