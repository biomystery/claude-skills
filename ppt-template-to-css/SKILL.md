---
name: ppt-template-to-css
description: Generates a Marp theme CSS from a PowerPoint template (.pptx or .potx) by reading its OOXML theme — color scheme, fonts, and master title/body sizes — so Marp decks match an existing brand/template. Use when you have a corporate or course PowerPoint template and want a Marp markdown deck styled to match, especially as the --theme input to /md-to-pptx-editable.
user-invocable: true
---

# PowerPoint Template to Marp CSS

Turns a PowerPoint template (`.pptx` / `.potx`) into a [Marp](https://marp.app) theme CSS. It reads the template's OOXML theme part — the color scheme (`dk1/lt1/accent1-6/hlink`), the major/minor fonts, and the slide master's title/body sizes — and writes a Marp theme that `@import`s `default` and applies those tokens. Pair it with `/md-to-pptx-editable` to render a markdown deck in a brand's look. The extractor is pure Python stdlib (no dependencies).

## When to Use

- You have a corporate / course / conference PowerPoint template and want Marp decks to match it
- "Make a Marp theme from this .pptx", "turn our brand template into CSS"
- You're about to run `/md-to-pptx-editable` and want a `--theme` that matches a real template

## Example Invocations

```
/ppt-template-to-css brand-template.potx
/ppt-template-to-css deck.pptx --name acme --out themes/acme.css
/ppt-template-to-css template.pptx --preview
make a marp theme css from this powerpoint template
```

---

## Instructions

### Step 0: Resolve Input, Name, Output

- **Template**: the argument path; else the most recently referenced `.pptx`/`.potx` in context; else ask *"Which PowerPoint template (.pptx/.potx) should I convert?"*
- **Theme name** (`--name`): a kebab-case CSS theme id; default = sanitized template base name.
- **Output** (`--out`): default = template dir + `<name>.css`.

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/ppt-template-to-css/SKILL.md)")"
```

### Step 1: Prerequisites

The extractor needs only `python3` (stdlib `zipfile` + `xml.etree`). The optional `--preview` step additionally needs `marp` and a Chromium browser.

```bash
python3 --version || echo "MISSING: python3"
# only for --preview:
which marp || echo "NOTE: marp-cli not found — preview will be skipped"
```

### Step 2: Generate the Theme CSS

```bash
python3 "$SKILL_DIR/scripts/template_to_css.py" "$TEMPLATE" ${NAME:+--name "$NAME"} ${OUT:+--out "$OUT"}
```

It prints `OUT=<css_path>` and a token summary (bg, text, accent, head/body fonts, sizes). Read the generated CSS and skim it — it is meant to be a readable, hand-tunable starting point, not a locked artifact.

### Step 3: Preview (optional, `--preview`)

Render a tiny sample deck so the user can see the colors/fonts before using the theme:

```bash
SAMPLE=$(mktemp /tmp/ppttheme_XXXX.md)
cat > "$SAMPLE" <<MD
---
marp: true
theme: $NAME
paginate: true
---

# Heading in the template's font

## Accent-colored subheading

- A bullet with **bold accent** text
- A [hyperlink](https://example.com) in the theme's link color
MD
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  marp "$SAMPLE" --theme-set "$OUT_CSS" --images png -o /tmp/ppttheme_preview.png
rm -f "$SAMPLE"
```

Read `/tmp/ppttheme_preview.001.png` and report how faithfully it matches.

### Step 4: Report

Tell the user:
- Path to the generated `.css` and its `@theme` name
- The extracted tokens (background, text, accent, heading/body fonts, title/body px)
- Any caveats that apply (see Notes) — especially fonts that may need installing
- **How to use it**: `/md-to-pptx-editable deck.md --theme <name>.css`, or add `theme: <name>` to the deck's frontmatter and pass the CSS via `--theme-set`.

---

## What Gets Mapped

| PowerPoint theme element | Marp CSS |
|---|---|
| `bg1` (via master `clrMap`) | `section` background |
| `tx1` | body text color |
| `accent1` | `--accent` → h2, bold, bullets, pagination |
| `accent1-6` | `--accent1 … --accent6` variables |
| `hlink` | link color |
| Major font (`majorFont/latin`) | heading `font-family` |
| Minor font (`minorFont/latin`) | body `font-family` |
| Master `titleStyle` lvl1 size/color | `h1` size + color |
| Master `bodyStyle` lvl1 size | body `font-size` |

## Output

A single Marp theme `.css` file (`@import 'default'` + a `:root` token block + element rules), ready to pass to Marp or `/md-to-pptx-editable`.

## Requirements

| Tool | Install | Purpose |
|---|---|---|
| `python3` | system | Theme extraction (stdlib only) |
| `@marp-team/marp-cli` | `npm i -g @marp-team/marp-cli` | `--preview` only |
| Chrome / Chromium | system install | `--preview` only |

## Notes

- **Fonts** are emitted by name with sane sans fallbacks. If the template's font (e.g. a brand face) isn't installed where Marp renders (Chrome), the fallback is used — install the font, or edit `--font-head`/`--font-body`.
- **Approximation, not pixel-parity.** Background images, gradients, picture fills, effects, and per-layout placeholder geometry are not extracted — only color, font, and base sizes. The CSS is a clean starting point to tune.
- Sizes are clamped to legible ranges (title 36–66px, body 22–30px) because PowerPoint placeholder sizes are often oversized for slide bullets.
- `sysClr` (windowText/window) resolves via its `lastClr`, falling back to black/white.
- Works on both `.pptx` and `.potx` — same OOXML package structure.

## Skill Structure

```
ppt-template-to-css/
├── SKILL.md            (this file)
├── README.md
└── scripts/
    └── template_to_css.py   (parse OOXML theme → Marp CSS)
```
