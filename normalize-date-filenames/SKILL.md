---
name: normalize-date-filenames
description: Normalize dated filenames in a folder to YYYY-MM-DD-<time-or-desc>.ext — handles Office Lens, Microsoft Lens, "Scan from", compact MDY dates, and ISO dates. Dry-runs first, then optionally deletes .pptx/.docx duplicates when a .pdf counterpart exists.
user-invocable: true
---

# Normalize Date Filenames

Scans a directory for files whose names encode a date in any of several scanner/app formats, renames them to consistent `YYYY-MM-DD-<suffix>.ext` form, and optionally deletes `.pptx`/`.docx` duplicates when a `.pdf` of the same scan already exists. Always dry-runs first and waits for confirmation before touching any file.

## When to Use

- A folder of scanned documents has mixed naming from Office Lens, Microsoft Lens, iPhone "Scan from", and manual renames
- Filenames use compact un-padded dates (e.g. `81516`, `142016`), AM/PM timestamps, or no separators between date and time
- You want all files sortable by date with a single consistent format

## Parameters

| Parameter | Values | Default | Meaning |
|---|---|---|---|
| `<dir>` | path to directory | required | Folder to normalize |
| `--dedup` | flag | off | Also delete .pptx/.docx when a .pdf exists for the same scan |

## Instructions

### Step 1: Identify the Target Directory

Use the path the user provides. If none given, ask:

> "Which directory should I normalize? (provide the full path)"

### Step 2: Dry Run — Show What Would Change

Run the parser below. It handles all known date formats and produces a table of old → new names plus a delete list (if `--dedup`).

```python
import re, os, unicodedata
from datetime import datetime
from collections import defaultdict

DIR = "<user-provided path>"

def ns(s):
    """Normalize unicode whitespace (narrow no-break space etc.) to regular space."""
    return ''.join(' ' if unicodedata.category(c) == 'Zs' else c for c in s)

def expand2(yy): return 2000 + int(yy)

def valid(y, mo, d):
    try:
        datetime(y, mo, d)
        return 2000 <= y <= 2035
    except:
        return False

def fmtd(y, mo, d): return f"{y:04d}-{mo:02d}-{d:02d}"

def parse_compact_date(s):
    """Try multiple un-padded MDY/YMD interpretations of a compact digit string."""
    n = len(s)
    if n == 8:                                          # YYYYMMDD or MMDDYYYY
        y, mo, d = int(s[:4]), int(s[4:6]), int(s[6:])
        if valid(y, mo, d): return y, mo, d
        mo, d, y = int(s[:2]), int(s[2:4]), int(s[4:])
        if valid(y, mo, d): return y, mo, d
    if n == 7:                                          # MDDYYYY (1-digit month)
        mo, d, y = int(s[0]), int(s[1:3]), int(s[3:])
        if valid(y, mo, d): return y, mo, d
    if n == 6:                                          # MMDDYY, MDYYYY, or YYMMDD
        mo, d, y = int(s[:2]), int(s[2:4]), expand2(s[4:])
        if valid(y, mo, d): return y, mo, d
        mo, d, y = int(s[0]), int(s[1]), int(s[2:])    # MDYYYY
        if valid(y, mo, d): return y, mo, d
        y, mo, d = expand2(s[:2]), int(s[2:4]), int(s[4:])  # YYMMDD
        if valid(y, mo, d): return y, mo, d
    if n == 5:                                          # MDDYY
        mo, d, y = int(s[0]), int(s[1:3]), expand2(s[3:])
        if valid(y, mo, d): return y, mo, d
    if n == 4:                                          # MDYY
        mo, d, y = int(s[0]), int(s[1]), expand2(s[2:])
        if valid(y, mo, d): return y, mo, d
    return None

def clean(s):
    """Strip app-name tokens, normalize separators to hyphens."""
    if not s: return ''
    s = re.sub(r'\b(?:Office\s*Lens|Microsoft(?:\s*Lens)?)\b', '', s, flags=re.I)
    s = re.sub(r'\bScan from\b', '', s, flags=re.I)
    s = s.strip(' ,-_')
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r',', '', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def extract(stem):
    """Return (date_str, suffix_str) or None. Order matters — most specific first."""

    # P1: "Scan from YYYY-MM-DD HH_MM_SS AM/PM [desc]"
    m = re.match(r'^Scan from (\d{4}-\d{2}-\d{2})(.*)', stem, re.I)
    if m:
        y, mo, d = int(m[1][:4]), int(m[1][5:7]), int(m[1][8:])
        if valid(y, mo, d): return fmtd(y, mo, d), clean(m[2])

    # P2: "YYYY-MM-DD HH_MM_SS AM/PM [desc]"  (space after ISO date)
    m = re.match(r'^(\d{4}-\d{2}-\d{2}) (.*)', stem)
    if m:
        y, mo, d = int(m[1][:4]), int(m[1][5:7]), int(m[1][8:])
        if valid(y, mo, d): return fmtd(y, mo, d), clean(m[2])

    # P3: "Office/Microsoft Lens YYYYMMDD-HHMMSS [suffix]"
    m = re.match(r'^(?:Office|Microsoft)(?:\s*\w+)?\s+(\d{8})(.*)', stem, re.I)
    if m:
        d = parse_compact_date(m[1])
        if d: return fmtd(*d), clean(m[2])

    # P4: "YYYYMMDD-HHMMSS [suffix]"  (compact date then hyphen-time)
    m = re.match(r'^(\d{8})-(.*)', stem)
    if m:
        d = parse_compact_date(m[1])
        if d: return fmtd(*d), clean(m[2])

    # P5: "M_DD_YY, H_MM AM/PM [app]"  (Microsoft Lens underscore-comma format)
    m = re.match(r'^(\d{1,2})_(\d{1,2})_(\d{2})(.*)', stem)
    if m:
        y, mo, dv = expand2(m[3]), int(m[1]), int(m[2])
        if valid(y, mo, dv): return fmtd(y, mo, dv), clean(m[4])

    # P6: compact date (4–8 digits) then space or comma — handles MMDDYYYY, MDDYYYY,
    #     MMDDYY, MDDYY, MDYY with un-padded month/day and optional AM/PM time
    for n in [8, 7, 6, 5, 4]:
        if re.match(r'^\d{' + str(n) + r'}[\s,]', stem):
            d = parse_compact_date(stem[:n])
            if d: return fmtd(*d), clean(stem[n:])

    # P7: "YYYYMMDD_desc" or "YYMMDD_desc"
    m = re.match(r'^(\d{6,8})_(.+)', stem)
    if m:
        d = parse_compact_date(m[1])
        if d: return fmtd(*d), clean(m[2])

    # P8: "Desc_YYYYMMDD[ N]"  (description before embedded date)
    m = re.match(r'^([A-Za-z].+?)_(\d{8})(.*)', stem)
    if m:
        d = parse_compact_date(m[2])
        if d: return fmtd(*d), clean(m[1] + ' ' + m[3])

    return None

renames = []
for fname in sorted(os.listdir(DIR)):
    if re.match(r'^\d{4}-\d{2}-\d{2}[-_]', fname): continue  # already normalized
    if fname.startswith('.'): continue
    stem, ext = os.path.splitext(fname)
    r = extract(ns(stem))
    if r is None: continue
    date_s, suf = r
    new_name = date_s + ('-' + suf if suf else '') + ext
    if new_name != fname:
        renames.append((fname, new_name))

# Dedup: find stems where a .pdf exists alongside .pptx/.docx
file_to_new = dict(renames)
stem_map = defaultdict(dict)
for fname in os.listdir(DIR):
    if fname.startswith('.'): continue
    new_name = file_to_new.get(fname, fname)
    new_stem, new_ext = os.path.splitext(new_name)
    stem_map[new_stem][new_ext.lower()] = fname

deletes = []
for new_stem, ext_map in stem_map.items():
    if '.pdf' in ext_map and (ext_map.keys() & {'.pptx', '.docx'}):
        for ext in ['.pptx', '.docx']:
            if ext in ext_map:
                deletes.append(ext_map[ext])

print("=== RENAMES ===")
for old, new in renames:
    print(f"  {old!r:60s} → {new!r}")

print("\n=== DELETE (non-PDF duplicates) ===")
for f in sorted(deletes):
    print(f"  {f!r}")

print(f"\nSummary: {len(renames)} renames, {len(deletes)} deletable")
```

### Step 3: Confirm with User

Present the table and ask:

> "Proceed with N renames?" (and separately for deletes if `--dedup` was requested)

Do not rename or delete anything without explicit confirmation.

### Step 4: Apply

Delete duplicates **first** (before rename, while original names are still intact), then apply renames:

```python
# Phase 1: delete non-PDF duplicates (only if --dedup confirmed)
for fname in deletes:
    path = os.path.join(DIR, fname)
    if os.path.exists(path):
        os.remove(path)
        print(f"DELETED  {fname!r}")

# Phase 2: rename
for old, new in renames:
    src = os.path.join(DIR, old)
    dst = os.path.join(DIR, new)
    if not os.path.exists(src):
        print(f"SKIP (already gone): {old!r}")
        continue
    if os.path.exists(dst):
        print(f"SKIP (dst exists): {old!r} → {new!r}")
        continue
    os.rename(src, dst)
    print(f"RENAMED  {old!r} → {new!r}")
```

### Step 5: Report

State how many files were renamed, deleted, and skipped. Note: "SKIP (already gone)" entries for files that were deleted in Phase 1 are expected and not errors.

## Date Format Reference

| Input format | Example | Parsed as |
|---|---|---|
| `Scan from YYYY-MM-DD HH_MM_SS AM/PM` | `Scan from 2025-12-24 02_32_58 PM` | `2025-12-24-02-32-58-PM` |
| `YYYY-MM-DD HH_MM_SS AM/PM[-desc]` | `2025-08-24 10_56_34 AM-april-card` | `2025-08-24-10-56-34-AM-april-card` |
| `YYYYMMDD-HHMMSS Office Lens` | `20150930-040704 Office Lens` | `2015-09-30-040704` |
| `Office Lens YYYYMMDD-HHMMSS` | `Office Lens 20170625-213256` | `2017-06-25-213256` |
| `MMDDYYYY HHH(H) AM/PM [Lens] [N]` | `11272015 213 PM Office Lens 2` | `2015-11-27-213-PM-2` |
| `MDDYYYY HHH(H) AM/PM [Lens]` | `1242015 1023 PM Office Lens` | `2015-01-24-1023-PM` |
| `MDYYYY HHH(H) AM/PM [Lens]` | `142016 726 AM Office Lens` | `2016-01-04-726-AM` |
| `MMDDYY[,] HHH(H) AM/PM [Lens]` | `102220, 225 PM Office Lens` | `2020-10-22-225-PM` |
| `MDDYY HHH(H) AM/PM [Lens]` | `81516 621 PM Office Lens 1` | `2016-08-15-621-PM-1` |
| `MDYY HHH(H) AM/PM [Lens]` | `6916 1037 AM Office Lens` | `2016-06-09-1037-AM` |
| `M_DD_YY, H_MM AM/PM Microsoft Lens` | `1_11_23, 8_06 AM Microsoft Lens` | `2023-01-11-8-06-AM` |
| `YYMMDD_desc` | `190803_receipt` | `2019-08-03-receipt` |
| `Desc_YYYYMMDD[ N]` | `Aiden_bill_20201215` | `2020-12-15-Aiden-bill` |

## Gotchas

- **Unicode whitespace**: newer Microsoft Lens files use narrow no-break space (` `) between time and AM/PM — the `ns()` function normalises these before parsing
- **Year sanity check**: the parser rejects years outside 2000–2035 to avoid false matches (e.g. `MDYYYY` where year parses as 803)
- **2-digit years**: all assumed to be 20xx (range 2000–2035 covers the full output of these apps)
- **Delete-then-rename ordering**: deleting duplicates before renaming means the "SKIP (already gone)" log lines for deleted files during rename are expected, not errors
- **Destination conflict**: if the target name already exists, the file is skipped and reported — no overwrite occurs
- **Files not matched**: filenames with no recognisable date (e.g. `guitar_book_01_part1.pdf`, `FeddieMac_mortgage_purchase.pdf`) are silently skipped
- **Already-normalised files** (matching `^\d{4}-\d{2}-\d{2}[-_]`) are skipped

## Example Invocations

```
/normalize-date-filenames ~/Documents/scans
```
→ Renames all dated files to YYYY-MM-DD format; shows dry-run first

```
/normalize-date-filenames ~/Documents/scans --dedup
```
→ Same, plus deletes .pptx/.docx when a .pdf exists for the same scan

## Output

Files renamed and/or deleted in-place. No files created.

## Requirements

- Python 3 (standard library only — `re`, `os`, `unicodedata`, `datetime`, `collections`)
- Write permission to the target directory

## Skill Structure

```
normalize-date-filenames/
├── SKILL.md
└── README.md
```
