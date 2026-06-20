---
name: md-to-pptx-editable
description: Converts a Marp markdown deck to PowerPoint (.pptx), rendering Mermaid diagrams as embedded images and producing an editable PPTX (real text boxes via LibreOffice) plus pixel-perfect PDF and image PPTX fallbacks, with Marp speaker-note transcripts preserved. Use when turning a Marp .md into slides someone needs to edit in PowerPoint, or when a deck has Mermaid blocks and presenter notes that must survive the export.
user-invocable: true
---

# Marp Markdown to Editable PowerPoint

Converts a [Marp](https://marp.app) markdown deck to `.pptx`. By default Marp exports a PPTX where each slide is a single flat image — not editable. This skill produces a **text-editable** PPTX via Marp's experimental `--pptx-editable` (LibreOffice) path, renders embedded Mermaid blocks to PNG first, and re-injects the speaker-note transcripts that the editable export drops. Because the editable path can re-wrap tight layouts, it also emits a **pixel-perfect PDF and image-based PPTX** so you always have a faithful artifact.

## When to Use

- "Convert this Marp deck to PowerPoint", "make an editable pptx from slides.md"
- A Marp `.md` contains ` ```mermaid ``` ` diagrams that must appear as pictures
- A Marp deck has `<!-- ... -->` speaker notes that need to survive into PowerPoint
- You need slides a non-technical user can edit in PowerPoint, not flat images

## Example Invocations

```
/md-to-pptx-editable
/md-to-pptx-editable slides.md
/md-to-pptx-editable deck.md --theme clinical.css
/md-to-pptx-editable deck.md --mermaid-config mermaid.json --out build/deck.pptx
/md-to-pptx-editable deck.md --no-editable      # pixel-perfect outputs only
convert this marp deck to an editable powerpoint
```

---

## Instructions

### Step 0: Resolve Paths and Flags

- **Source `.md`**: the argument path; else the most recently edited `.md` in context; else ask *"Which Marp markdown file should I convert?"*
- **Output base**: `--out <path>` if given, else the source dir + base name. Editable file = `<base>_editable.pptx`; pixel-perfect files = `<base>.pdf` and `<base>_print.pptx`.
- **Flags**: `--theme <css>` (extra Marp `--theme-set`), `--mermaid-config <json>` (Mermaid theme), `--no-editable` (skip the LibreOffice path), `--editable-only` (skip PDF + image PPTX).

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/md-to-pptx-editable/SKILL.md)")"
```

### Step 1: Prerequisites

```bash
which marp || echo "MISSING: marp-cli  (npm i -g @marp-team/marp-cli)"
# Browser for Marp + mermaid rendering:
ls "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/chromium 2>/dev/null | head -1 || echo "MISSING: Chrome/Chromium"
# LibreOffice — required ONLY for the editable PPTX path:
ls "/Applications/LibreOffice.app/Contents/MacOS/soffice" /usr/bin/soffice /usr/bin/libreoffice 2>/dev/null | head -1 || echo "MISSING: LibreOffice (editable export only)"
```

- `marp` missing → tell the user to install it and stop.
- Chrome missing → tell the user to install a Chromium browser and stop.
- LibreOffice missing → editable export is impossible; proceed with `--no-editable` and tell the user. To install when `brew install --cask libreoffice` is blocked (e.g. Homebrew permissions), download the DMG directly — see Step 3a.

Export the browser path so Marp and mermaid-cli reuse it (avoids a puppeteer Chromium download):

```bash
export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # or the Linux path
```

Set up a reused virtualenv for the Python helpers (avoids PEP-668 "externally managed" errors):

```bash
VENV="$SKILL_DIR/.venv"
[ -d "$VENV" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q python-pptx pymupdf
PY="$VENV/bin/python"
```

### Step 2: Render Mermaid Diagrams

Marp does not render Mermaid. Replace each fence with a rendered PNG (kept in the source dir until cleanup):

```bash
out=$("$PY" "$SKILL_DIR/scripts/render_mermaid.py" "$SRC_MD" ${MERMAID_CONFIG:+--config "$MERMAID_CONFIG"})
TMP_MD=$(echo "$out" | sed -n 's/^TMP_MD=//p')
PNG_COUNT=$(echo "$out" | sed -n 's/^PNG_COUNT=//p')
PNGS=$(echo "$out" | sed -n 's/^PNGS=//p')
```

If `PNG_COUNT=0`, there were no Mermaid blocks and `TMP_MD` equals the source.

> If the markdown already references a not-yet-existing image (e.g. `![](Workflow.png)`) **and** carries the same diagram as a ```mermaid``` fence, prefer the fence: it is the source of truth. Delete the dangling manual `![]()` line, or point it at the rendered `_mermaid_0.png`, so the slide shows one clean diagram.

### Step 3: Build the Pixel-Perfect Outputs (default)

These use Chrome only — fast and faithful. The image PPTX keeps speaker notes natively.

```bash
THEME=${THEME:+--theme-set "$THEME"}
marp "$TMP_MD" $THEME --html --allow-local-files --pdf  -o "$OUT_PDF"
marp "$TMP_MD" $THEME --html --allow-local-files --pptx -o "$OUT_PRINT_PPTX"   # image-per-slide
```

Skip this step if `--editable-only` was passed.

### Step 3a: Build the Editable PPTX

Requires LibreOffice. **Warm its font cache first** — the first `soffice` run after any font change rebuilds the cache and can hang the conversion indefinitely:

```bash
SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"   # or /usr/bin/soffice
export PATH="$(dirname "$SOFFICE"):$PATH"
"$SOFFICE" --headless --terminate_after_init      # warm the font cache, then exit
marp "$TMP_MD" $THEME --html --allow-local-files --pptx --pptx-editable -o "$OUT_EDITABLE_PPTX"
```

If marp appears to hang for more than ~2 minutes: `pkill -f "marp "; pkill -f soffice`, remove a stale lock at `~/Library/Application Support/LibreOffice/4/user/.lock`, re-warm, and retry. Skip this step if `--no-editable` was passed.

### Step 4: Re-inject Speaker Notes into the Editable PPTX

The editable (LibreOffice) export drops Marp notes. Pull them back out of the markdown and write them onto the slides (the image PPTX from Step 3 already has them):

```bash
"$PY" "$SKILL_DIR/scripts/add_notes.py" "$SRC_MD" "$OUT_EDITABLE_PPTX"
```

### Step 5: QA

Report structure, and render the editable deck's pages to spot LibreOffice re-wrapping/overlap:

```bash
"$PY" "$SKILL_DIR/scripts/qa_render.py" "$OUT_EDITABLE_PPTX" --render 1,3,5
```

Read the `/tmp/qa_<n>.png` images. Watch for: headings that wrapped a word early and overlap the body, inline chips/labels that dropped their last character, blurred `box-shadow` rendered as a solid gray band. These are inherent `--pptx-editable` limits — if they appear, point the user to the PDF / image PPTX and (optionally) suggest loosening the theme.

### Step 6: Clean Up and Report

```bash
[ "$TMP_MD" != "$SRC_MD" ] && rm -f "$TMP_MD"
[ -n "$PNGS" ] && rm -f ${PNGS//,/ }
```

Report: each file written and what it is for (table below), the number of diagrams embedded, slides with notes, and **which file to use** — present from the PDF or image PPTX; edit text in the `_editable.pptx`. Call out any QA artifacts you saw.

| File | Fidelity | Editable text | Notes | Use for |
|---|---|---|---|---|
| `<base>.pdf` | Pixel-perfect | No | Yes | Presenting / submitting |
| `<base>_print.pptx` | Pixel-perfect (images) | No | Yes | When `.pptx` required, looks must match |
| `<base>_editable.pptx` | Approximate | Yes | Yes | Editing wording in PowerPoint |

---

## Output

Up to three files: a pixel-perfect `.pdf`, an image-based `_print.pptx`, and a text-editable `_editable.pptx` — all carrying the deck's Mermaid diagrams as images and its Marp speaker notes.

## Requirements

| Tool | Install | Purpose |
|---|---|---|
| `@marp-team/marp-cli` | `npm i -g @marp-team/marp-cli` | Markdown → PDF / PPTX |
| Chrome / Chromium | system install | Marp + Mermaid rendering |
| LibreOffice | cask, or direct DMG (Step 3a) | Editable PPTX export only |
| `@mermaid-js/mermaid-cli` | auto via `npx` | Renders Mermaid blocks |
| `python-pptx`, `pymupdf` | auto into `$SKILL_DIR/.venv` | Notes injection + QA render |

## Notes

- **Editable vs. faithful is a real trade-off.** `--pptx-editable` is experimental and routes through LibreOffice, which sizes text boxes tightly and re-wraps tight headings and styled inline runs. Keep themes loose (generous heading sizes, avoid `box-shadow`/blur and pill-style inline labels) if the editable file is the primary deliverable. Otherwise lean on the PDF / image PPTX.
- Marp treats non-directive `<!-- ... -->` comments as speaker notes; `add_notes.py` skips directive comments (`_class:`, `paginate:`, `_header:`, …).
- Per-slide directives still work: `<!-- _class: lead -->`, `<!-- _header: '01 · INTRO' -->`, `footer:` in frontmatter.
- `--allow-local-files` is required for Marp to embed local diagram PNGs.

## Skill Structure

```
md-to-pptx-editable/
├── SKILL.md            (this file)
├── README.md
└── scripts/
    ├── render_mermaid.py   (extract + render Mermaid fences to PNG)
    ├── add_notes.py        (re-inject Marp speaker notes into the editable PPTX)
    └── qa_render.py        (structure report + PPTX→PNG render for visual QA)
```
