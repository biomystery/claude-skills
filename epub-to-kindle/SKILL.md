---
name: epub-to-kindle
description: Convert an EPUB (or any Calibre-supported ebook) to a Kindle format — AZW3 (modern) or MOBI (legacy) — via Calibre's ebook-convert. Auto-locates the CLI inside the macOS .app bundle, installs Calibre through Homebrew if missing, and surfaces the exact sudo command when /opt/homebrew permissions block the install. Use when someone wants an .epub readable on a Kindle.
user-invocable: true
---

# EPUB to Kindle

Convert an `.epub` (or other Calibre-supported input) into a Kindle-readable file — `.azw3` by default, or `.mobi` for older devices — using Calibre's `ebook-convert`. The skill handles the macOS gotchas: the `ebook-convert` CLI lives inside the `.app` bundle (not on `$PATH`), Calibre may not be installed, and Homebrew installs fail when `/opt/homebrew` is owned by root.

## When to Use

- A user asks to convert an EPUB "to Kindle", "to AZW", "to AZW3", "to MOBI", or an ambiguous variant like "aws format"
- They want to side-load a book onto a Kindle device or app
- Any Calibre-supported input → Kindle output conversion (e.g. `.fb2`, `.lit`, `.pdb` → `.azw3`)

## Parameters

| Parameter | Values | Default | Meaning |
|---|---|---|---|
| `<input>` | path to ebook file | required | Source file to convert |
| `<format>` | `azw3` \| `mobi` | `azw3` | Target Kindle format |
| `<output>` | path | `<input>.<format>` | Where to write the result |

## Instructions

### Step 0: Disambiguate the Target Format

Kindle requests are often imprecise. Map them before doing anything:

- "aws", "azw", "azw3", "Kindle", "modern Kindle" → **AZW3** (default; KF8, current Kindles)
- "mobi", "old Kindle", "older device", "max compatibility" → **MOBI** (legacy)

If genuinely ambiguous, confirm with the user: *"Kindle format — AZW3 (modern) or MOBI (legacy)?"* AZW3 is the right default for any reasonably recent Kindle.

### Step 1: Locate the Input File

Use the path the user provided. Confirm it exists:

```bash
ls -la "<input.epub>"
```

If not found, ask for the correct path before continuing.

### Step 2: Run the Conversion Helper

The bundled script locates `ebook-convert`, installs Calibre if needed, and converts. Prefer it over hand-typed commands — it encodes every edge case from below.

```bash
"$SKILL_DIR/scripts/convert-ebook.sh" "<input.epub>" azw3 "<output.azw3>"
# or for legacy devices:
"$SKILL_DIR/scripts/convert-ebook.sh" "<input.epub>" mobi
```

(`$SKILL_DIR` is this skill's directory. Omit the third arg to default the output next to the input with the new extension.)

#### What the script does, in order

1. **Find the CLI.** Checks `$PATH`, then the macOS bundle path `/Applications/calibre.app/Contents/MacOS/ebook-convert`. The CLI is **not** on `$PATH` after a cask install — always check the bundle.
2. **Install Calibre if missing** via `brew install --cask calibre`.
3. **Convert** with `ebook-convert <input> <output>` and verify the output file exists.

### Step 3: Handle the Homebrew Permission Wall (most common failure)

If Calibre isn't installed and `/opt/homebrew` is owned by root, `brew` fails with either:

```
Error: undefined method 'to_sym' for nil
Error: /opt/homebrew is not writable.
```

The script detects a non-writable prefix and prints the fix. This **requires interactive sudo, which the agent cannot run** (the `!`-prefix shell has no TTY for the password). Tell the user to run, in a **real terminal window**:

```bash
sudo chown -R $(whoami) /opt/homebrew
```

Then re-run Step 2. (Clearing `~/Library/Caches/Homebrew/api` alone does **not** fix the permission issue — only the `chown` does. The cache clear only helps the separate `to_sym` stale-cache crash, and the script does it automatically.)

If the user prefers not to chown all of Homebrew, the alternative is the official Calibre `.dmg` from <https://calibre-ebook.com/download_osx> — but that's a GUI install they must do themselves.

### Step 4: Verify and Report

```bash
ls -la "<output.azw3>"
```

Report the output path and size, and how to side-load it:

> Connect the Kindle via USB and copy the `.azw3`/`.mobi` into the `documents` folder, or email it to your Send-to-Kindle address.

## Example Invocations

```
/epub-to-kindle ~/Downloads/book.epub
```
→ Converts to `~/Downloads/book.azw3` (AZW3 default)

```
/epub-to-kindle ~/Downloads/book.epub mobi
```
→ Converts to `~/Downloads/book.mobi` for an older Kindle

```
convert book.epub to aws format
```
→ "aws" interpreted as AZW3; confirm, then convert

## Output

A single converted ebook file (`.azw3` or `.mobi`) written next to the input (or to the path given). Original EPUB is left untouched.

## Requirements

- **macOS** with **Homebrew** (for auto-install), or Calibre already installed
- **Calibre** (`ebook-convert`) — installed automatically if absent
- Writable `/opt/homebrew` for the auto-install path (else a one-time `sudo chown`)

## Skill Structure

```
epub-to-kindle/
├── SKILL.md    (this file)
├── README.md
└── scripts/
    └── convert-ebook.sh   (locate CLI · install Calibre · convert · verify)
```
