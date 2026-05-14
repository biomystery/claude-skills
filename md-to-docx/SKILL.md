---
name: md-to-docx
description: Convert a Markdown file to Word (.docx), rendering any Mermaid diagrams as embedded PNG images. Uses pandoc + mermaid-cli (via npx, no global install needed).
user-invocable: true
---

# Markdown to Word (.docx) Converter

Converts a Markdown file to a Word document (`.docx`), automatically detecting and rendering Mermaid diagram code blocks as embedded PNG images before passing the file to pandoc. Requires no global mermaid install — uses `npx @mermaid-js/mermaid-cli` on demand.

## When to Use

- User says "convert this markdown to Word", "export to docx", "make a Word version"
- User wants to share a `.md` document with stakeholders who use Word or Google Docs
- A markdown file contains Mermaid diagrams that need to appear as images in the output

## Example Invocations

```
/md-to-docx
/md-to-docx report.md
/md-to-docx docs/proposal.md --out docs/proposal.docx
/md-to-docx docs/proposal.md --reference my-template.docx
convert this markdown to word
export the spec to docx
```

---

## Instructions

### Step 0: Resolve Input and Output Paths

**Determine the source markdown file:**

1. If a path was passed as argument, use it.
2. If no path given, look for an obvious candidate: the most recently edited `.md` file in the working directory or referenced in recent conversation context.
3. If still ambiguous, ask the user: *"Which markdown file should I convert?"*

**Determine the output `.docx` path:**

- If `--out <path>` was passed, use it.
- Otherwise, place the `.docx` in the same directory as the source file, same base name: `<source-stem>.docx`.

**Check for `--reference <template.docx>`:**  
If provided, pass it to pandoc as `--reference-doc=<template>` for custom styles.

---

### Step 1: Check Prerequisites

```bash
which pandoc || echo "MISSING: pandoc"
npx @mermaid-js/mermaid-cli --version 2>/dev/null | head -1 || echo "MISSING: mermaid-cli"
```

- If `pandoc` is missing: tell the user to install it (`brew install pandoc` on macOS, `apt install pandoc` on Linux) and stop.
- If mermaid-cli is missing via npx: warn the user but continue — Mermaid blocks will be left as fenced code blocks in the output instead of failing.

---

### Step 2: Extract and Render Mermaid Diagrams

Run the following Python snippet (inline via `python3 -`) to extract Mermaid blocks, render each to PNG, and produce a temporary markdown file with image references substituted in:

```python
import re, subprocess, os, sys, tempfile

src      = "<ABSOLUTE_PATH_TO_SOURCE_MD>"
out_docx = "<ABSOLUTE_PATH_TO_OUTPUT_DOCX>"
src_dir  = os.path.dirname(src)

with open(src) as f:
    content = f.read()

mermaid_pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
matches = list(mermaid_pattern.finditer(content))

png_paths = []
for i, match in enumerate(matches):
    mmd_path = os.path.join(src_dir, f"_mermaid_{i}.mmd")
    png_path = os.path.join(src_dir, f"_mermaid_{i}.png")
    with open(mmd_path, 'w') as f:
        f.write(match.group(1))
    result = subprocess.run(
        ["npx", "@mermaid-js/mermaid-cli", "-i", mmd_path, "-o", png_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Warning: mermaid render failed for block {i}: {result.stderr}", file=sys.stderr)
        png_paths.append(None)
    else:
        png_paths.append(png_path)
    os.remove(mmd_path)

def replace_mermaid(m):
    idx = matches.index(m)      # matches is closed-over list
    png = png_paths[idx]
    if png:
        return f"![Diagram]({png})"
    return m.group(0)           # leave as fenced block if render failed

new_content = mermaid_pattern.sub(replace_mermaid, content)

# Use enumerate-based replacement to avoid re.finditer issue
offset = 0
new_content = content
for i, match in enumerate(matches):
    png = png_paths[i]
    replacement = f"![Diagram]({png_paths[i]})" if png else match.group(0)
    new_content = new_content[:match.start() + offset] + replacement + new_content[match.end() + offset:]
    offset += len(replacement) - (match.end() - match.start())

tmp_md = os.path.join(src_dir, "_tmp_pandoc_input.md")
with open(tmp_md, 'w') as f:
    f.write(new_content)

print(f"TMP_MD={tmp_md}")
print(f"PNG_COUNT={len([p for p in png_paths if p])}")
```

Capture `TMP_MD` and `PNG_COUNT` from stdout.

---

### Step 3: Run Pandoc

```bash
pandoc "$TMP_MD" -o "$OUT_DOCX" [--reference-doc="$TEMPLATE" if provided]
```

If pandoc exits non-zero, show the error message to the user.

---

### Step 4: Clean Up Temp Files

```bash
rm -f "$TMP_MD"
rm -f "$SRC_DIR"/_mermaid_*.png   # rendered PNGs embedded in docx, no longer needed
```

---

### Step 5: Report Result

Tell the user:
- Path to the generated `.docx`
- Number of Mermaid diagrams rendered (from `PNG_COUNT`)
- Any diagrams that failed to render (left as code blocks)
- Tip: *"To import into Google Docs: drag the .docx into Google Drive → Open with Google Docs."*

---

## Output

A `.docx` file at the specified output path, with:
- All markdown elements converted (headings, tables, bold, code, lists)
- Mermaid diagrams embedded as PNG images
- Optional: styles from a reference `.docx` template

## Requirements

| Tool | Install | Purpose |
|---|---|---|
| `pandoc` | `brew install pandoc` / `apt install pandoc` | Markdown → .docx conversion |
| `npx` (Node.js) | Ships with Node.js | Runs mermaid-cli without global install |
| `@mermaid-js/mermaid-cli` | Fetched via `npx` on demand | Renders Mermaid code blocks to PNG |

## Notes

- If `npx @mermaid-js/mermaid-cli` is slow on first run, it is downloading the package — subsequent runs are cached.
- SVG is not used because Word embeds PNG more reliably.
- Use `--reference-doc` with a branded `.docx` template to apply company fonts and styles.
- To share as Google Doc: drag the `.docx` into Google Drive → right-click → *Open with Google Docs*.

## Skill Structure

```
md-to-docx/
├── SKILL.md    (this file)
└── README.md
```
