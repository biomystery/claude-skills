---
name: md-to-docx
description: Converts a Markdown file to a Word (.docx) document, rendering Mermaid diagrams as embedded PNG images and applying a bundled business style. Use when sharing markdown with Word or Google Docs users, or when a markdown file contains Mermaid diagrams that need to appear as images in the output.
user-invocable: true
---

# Markdown to Word (.docx) Converter

Converts a Markdown file to a Word document (`.docx`), automatically rendering Mermaid diagram code blocks as embedded PNG images and applying a clean business style (dark navy headings, styled code blocks, blue-accented blockquotes) via a bundled reference template. A custom template can be substituted with `--reference`.

## When to Use

- User says "convert this markdown to Word", "export to docx", "make a Word version"
- User wants to share a `.md` document with stakeholders who use Word or Google Docs
- A markdown file contains Mermaid diagrams that need to appear as images in the output

## Example Invocations

```
/md-to-docx
/md-to-docx report.md
/md-to-docx docs/proposal.md --out docs/proposal.docx
/md-to-docx docs/proposal.md --reference my-brand-template.docx
/md-to-docx docs/proposal.md --no-reference
convert this markdown to word
export the spec to docx
```

---

## Instructions

### Step 0: Resolve Input, Output, and Reference Paths

**Source markdown file:**
1. If a path was passed as argument, use it.
2. Otherwise look for the most recently edited `.md` file in context.
3. If still ambiguous, ask: *"Which markdown file should I convert?"*

**Output `.docx` path:**
- If `--out <path>` was passed, use it.
- Otherwise: same directory and base name as the source, `.docx` extension.

**Reference doc (controls Word styles):**
- If `--reference <file>` was passed, use that file.
- If `--no-reference` was passed, skip the reference doc entirely (pandoc defaults).
- Otherwise, use the **bundled business reference** — resolve its path:
  ```bash
  SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/md-to-docx/SKILL.md)")"
  REFERENCE="$SKILL_DIR/business-reference.docx"
  ```
  If `business-reference.docx` does not exist at that path, go to Step 1b to generate it.

---

### Step 1: Check Prerequisites

```bash
which pandoc || echo "MISSING: pandoc"
npx @mermaid-js/mermaid-cli --version 2>/dev/null | head -1 || echo "MISSING: mermaid-cli (diagrams will be skipped)"
python3 -c "import docx" 2>/dev/null || echo "MISSING: python-docx (will be auto-installed if needed)"
```

- If `pandoc` is missing: tell the user to install it (`brew install pandoc` on macOS, `apt install pandoc` on Linux) and stop.
- mermaid-cli and python-docx are handled automatically (npx download / pip install on demand).

---

### Step 1b: Generate the Business Reference Doc (first-run, if missing)

Run this once to create `business-reference.docx` in the skill directory:

```bash
python3 "$SKILL_DIR/scripts/make_reference.py" "$REFERENCE"
```

The script auto-installs `python-docx` if needed, pulls pandoc's default reference as a base, then applies these styles:

| Element | Style |
|---|---|
| Heading 1 / 2 | Calibri Light, dark navy `#1E3A5F` |
| Heading 3 | Calibri bold, dark slate `#334155` |
| Inline code (`VerbatimChar`) | Consolas 9.5pt, dark slate `#2D3748` |
| Fenced code blocks (`Source Code`) | Consolas 9pt, light gray `#F4F6F8` bg, gray left bar |
| Blockquotes (`Block Text`) | Calibri 10.5pt, light blue `#EBF4FD` bg, blue `#3B82F6` left bar |
| Body text | Calibri 11pt |

---

### Step 2: Extract and Render Mermaid Diagrams

Run the bundled script — extracts all ` ```mermaid ``` ` blocks, renders each to PNG, writes a temp markdown copy with image references:

```bash
output=$(python3 "$SKILL_DIR/scripts/render_mermaid.py" "$SRC_MD")
TMP_MD=$(echo "$output" | grep '^TMP_MD=' | cut -d= -f2-)
PNG_COUNT=$(echo "$output" | grep '^PNG_COUNT=' | cut -d= -f2)
```

If `PNG_COUNT=0`, no Mermaid blocks were found and `TMP_MD` equals the source file.

---

### Step 3: Run Pandoc

```bash
# With business reference (default):
pandoc "$TMP_MD" -o "$OUT_DOCX" --reference-doc="$REFERENCE"

# With custom reference (--reference flag):
pandoc "$TMP_MD" -o "$OUT_DOCX" --reference-doc="$CUSTOM_REFERENCE"

# With no reference (--no-reference flag):
pandoc "$TMP_MD" -o "$OUT_DOCX"
```

If pandoc exits non-zero, show the full error message to the user.

---

### Step 3.5: Style Tables (post-process with python-docx)

Run the bundled script — applies dark-navy header row and alternating row bands to every table in the generated `.docx`:

```bash
python3 "$SKILL_DIR/scripts/style_tables.py" "$OUT_DOCX"
```

---

### Step 4: Clean Up Temp Files

```bash
rm -f "$TMP_MD"
rm -f "$SRC_DIR"/_mermaid_*.png
```

---

### Step 5: Report Result

Tell the user:
- Path to the generated `.docx`
- Reference template used (business default / custom / none)
- Number of Mermaid diagrams rendered
- Any diagrams that failed to render (left as code blocks)
- Tip: *"To import into Google Docs: drag the .docx into Google Drive → Open with Google Docs."*

---

## Output

A `.docx` file with:
- Clean business styling (headings, code blocks, blockquotes) from the bundled reference
- Mermaid diagrams embedded as PNG images
- All markdown elements converted (tables, bold, lists, inline code)

## Requirements

| Tool | Install | Purpose |
|---|---|---|
| `pandoc` | `brew install pandoc` / `apt install pandoc` | Markdown → .docx conversion |
| `npx` (Node.js) | Ships with Node.js | Runs mermaid-cli without global install |
| `@mermaid-js/mermaid-cli` | Auto-fetched via `npx` | Renders Mermaid blocks to PNG |
| `python-docx` | Auto-installed via `pip` on first run | Generates `business-reference.docx` |

## Notes

- `business-reference.docx` is generated once on first run and reused on all subsequent calls.
- SVG is not used for diagrams — Word embeds PNG more reliably.
- Pass `--no-reference` to get pandoc's plain default output with no style overrides.
- To share as Google Doc: drag the `.docx` into Google Drive → right-click → *Open with Google Docs*.

## Skill Structure

```
md-to-docx/
├── SKILL.md                 (this file)
├── README.md
├── business-reference.docx  (generated on first run, then reused)
└── scripts/
    ├── make_reference.py    (generates the business reference doc)
    ├── render_mermaid.py    (extracts and renders Mermaid blocks to PNG)
    └── style_tables.py      (applies table header/band styling to .docx)
```
