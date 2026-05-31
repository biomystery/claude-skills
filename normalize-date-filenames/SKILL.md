---
name: normalize-date-filenames
description: Normalize filenames in a folder that start with YYYY-MM-DD to a consistent format — all hyphens, no underscores, no trailing spaces. Dry-runs first and asks before applying.
user-invocable: true
---

# Normalize Date Filenames

Scans a directory for files whose names begin with `YYYY-MM-DD` and renames them to a consistent format: hyphens throughout, no underscores, no trailing spaces before the extension. Always dry-runs first and waits for user confirmation before touching any file.

## When to Use

- A folder of scanned documents (or any dated files) has accumulated inconsistent naming: some use `YYYY-MM-DD_desc`, others `YYYY-MM-DD-desc`, some have trailing spaces
- You want a one-shot cleanup that shows exactly what will change before applying it

## Parameters

| Parameter | Values | Default | Meaning |
|---|---|---|---|
| `<dir>` | path to directory | required | Folder to normalize |
| `--ext` | file extension filter | all extensions | Limit to `.pdf`, `.jpg`, etc. |

## Instructions

### Step 1: Identify the Target Directory

Use the path the user provides. If none given, ask:

> "Which directory should I normalize? (provide the full path)"

### Step 2: Dry Run — Show What Would Change

Run a Python snippet that finds all files matching `YYYY-MM-DD[-_]` and computes the target name:

```python
import re, os

dir_path = "<user-provided path>"
pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})[-_](.+?)(\.[^.]+)$')

renames = []
for name in sorted(os.listdir(dir_path)):
    m = pattern.match(name)
    if not m:
        continue
    date, desc, ext = m.group(1), m.group(2), m.group(3)
    desc = desc.strip()            # remove trailing spaces before extension
    new_desc = desc.replace('_', '-')
    new_name = f"{date}-{new_desc}{ext}"
    if new_name != name:
        renames.append((name, new_name))

for old, new in renames:
    print(f"  {old!r:60s} → {new!r}")
print(f"\nTotal: {len(renames)} files to rename")
```

Present the table to the user. If zero files match, say so and stop.

### Step 3: Confirm with User

Ask:

> "Proceed with renaming these N files?"

Wait for explicit yes/no. Do not rename anything until confirmed.

If the user wants a different separator convention (e.g. all underscores), adjust the `new_desc` line before the dry run and re-present. Common variants:
- All hyphens (default): `desc.replace('_', '-')`
- All underscores: `desc.replace('-', '_')` in the description only — keep `YYYY-MM-DD` date with hyphens

### Step 4: Apply Renames

```python
import re, os

dir_path = "<user-provided path>"
pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})[-_](.+?)(\.[^.]+)$')

renames = []
for name in sorted(os.listdir(dir_path)):
    m = pattern.match(name)
    if not m:
        continue
    date, desc, ext = m.group(1), m.group(2), m.group(3)
    desc = desc.strip()
    new_desc = desc.replace('_', '-')
    new_name = f"{date}-{new_desc}{ext}"
    if new_name != name:
        renames.append((name, new_name))

errors = []
for old, new in renames:
    src = os.path.join(dir_path, old)
    dst = os.path.join(dir_path, new)
    if os.path.exists(dst):
        errors.append(f"SKIP (destination exists): {old} → {new}")
        continue
    os.rename(src, dst)
    print(f"OK: {old!r} → {new!r}")

for e in errors:
    print(e)
print(f"\nDone. {len(renames) - len(errors)} renamed, {len(errors)} skipped.")
```

### Step 5: Report

State how many files were renamed and how many were skipped (destination already existed). If any were skipped, list them so the user can decide how to handle the conflict.

## Example Invocations

```
/normalize-date-filenames ~/Documents/scans
```
→ Normalizes all dated files in `~/Documents/scans` to all-hyphen format

```
/normalize-date-filenames ~/Documents/scans --ext .pdf
```
→ Same, restricted to PDF files only

## Output

Files renamed in-place. No files are created or deleted.

**Sample dry-run output:**
```
  '2022-06-26_car_service_receipt.pdf'  → '2022-06-26-car-service-receipt.pdf'
  '2023-04-01-Hd-Wyze .pdf'            → '2023-04-01-Hd-Wyze.pdf'
  '2024-05-21-Honda-invoice .pdf'       → '2024-05-21-Honda-invoice.pdf'

Total: 3 files to rename
```

## Requirements

- Python 3 (standard library only — `re`, `os`)
- Write permission to the target directory

## Gotchas

- **Trailing spaces before extension**: filenames like `invoice .pdf` (space before `.pdf`) are caught by `.strip()` on the description — do not skip this step
- **Destination conflict**: if the normalized name already exists, the file is skipped and reported; no overwrite occurs
- **Unicode filenames**: Python's `os.rename` handles non-ASCII characters (CJK, accented letters) correctly
- **Separator convention**: users often change their mind on hyphens vs. underscores — always dry-run first, and re-dry-run after any format change before applying

## Skill Structure

```
normalize-date-filenames/
├── SKILL.md
└── README.md
```
