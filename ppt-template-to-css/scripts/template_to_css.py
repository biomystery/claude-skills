#!/usr/bin/env python3
"""Generate a Marp theme CSS from a PowerPoint template (.pptx / .potx).

Usage: template_to_css.py <template.pptx|.potx> [--name <theme-name>] [--out <file.css>]

Reads the OOXML theme (ppt/theme/theme1.xml) for the color scheme and font scheme,
and the slide master (ppt/slideMasters/slideMaster1.xml) for the color map,
background, and title/body text sizes/colors. Maps them onto a Marp theme that
`@import`s 'default'. Colors and fonts approximate the PowerPoint theme — fonts
fall back gracefully if not installed where Marp renders (Chrome).

Prints OUT=<css_path> and a short token summary to stdout.
"""
import sys, os, re, zipfile
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"

SCHEME_ORDER = ["dk1", "lt1", "dk2", "lt2",
                "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
                "hlink", "folHlink"]
SYS = {"windowText": "000000", "window": "FFFFFF"}


def color_from(el):
    """Resolve an <a:srgbClr>/<a:sysClr> child element to a hex string."""
    if el is None:
        return None
    srgb = el.find(f"{A}srgbClr")
    if srgb is not None:
        return srgb.get("val", "").upper()
    sysc = el.find(f"{A}sysClr")
    if sysc is not None:
        return (sysc.get("lastClr") or SYS.get(sysc.get("val"), "000000")).upper()
    return None


def read_part(z, name):
    try:
        return ET.fromstring(z.read(name))
    except KeyError:
        return None


def main():
    tpl = sys.argv[1]
    name = None
    out = None
    if "--name" in sys.argv:
        name = sys.argv[sys.argv.index("--name") + 1]
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]

    base = os.path.splitext(os.path.basename(tpl))[0]
    name = name or re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "ppt-theme"
    out = out or os.path.join(os.path.dirname(os.path.abspath(tpl)), f"{name}.css")

    z = zipfile.ZipFile(tpl)
    theme = read_part(z, "ppt/theme/theme1.xml")
    if theme is None:
        for n in z.namelist():
            if re.match(r"ppt/theme/theme\d+\.xml$", n):
                theme = read_part(z, n)
                break
    if theme is None:
        sys.exit("ERROR: no theme part found in template")
    master = read_part(z, "ppt/slideMasters/slideMaster1.xml")

    # --- Color scheme ---
    clr = {}
    cs = theme.find(f".//{A}clrScheme")
    if cs is not None:
        for tok in SCHEME_ORDER:
            el = cs.find(f"{A}{tok}")
            if el is not None:
                clr[tok] = color_from(el)

    # --- Font scheme ---
    fs = theme.find(f".//{A}fontScheme")
    def latin(which):
        el = fs.find(f"{A}{which}/{A}latin") if fs is not None else None
        tf = el.get("typeface") if el is not None else None
        return tf or None
    major = latin("majorFont") or "Calibri Light"
    minor = latin("minorFont") or "Calibri"

    # --- Color map (bg1/tx1/... -> dk1/lt1/...) from the master ---
    cmap = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2"}
    if master is not None:
        m = master.find(f"{P}clrMap")
        if m is not None:
            for k in ("bg1", "tx1", "bg2", "tx2"):
                if m.get(k):
                    cmap[k] = m.get(k)

    def resolve(tok):
        tok = cmap.get(tok, tok)
        return clr.get(tok)

    bg = resolve("bg1") or "FFFFFF"
    text = resolve("tx1") or "000000"
    accent = clr.get("accent1") or text
    hlink = clr.get("hlink") or accent

    # --- Title / body sizes + title color from master txStyles ---
    def style_pt_color(style_tag):
        sz, col = None, None
        if master is not None:
            pr = master.find(f".//{P}{style_tag}/{A}lvl1pPr/{A}defRPr")
            if pr is not None:
                if pr.get("sz"):
                    sz = int(pr.get("sz")) / 100.0
                fill = pr.find(f"{A}solidFill")
                if fill is not None:
                    sc = fill.find(f"{A}schemeClr")
                    if sc is not None and sc.get("val"):
                        col = resolve(sc.get("val")) or clr.get(sc.get("val"))
                    else:
                        col = color_from(fill)
        return sz, col

    title_pt, title_col = style_pt_color("titleStyle")
    body_pt, _ = style_pt_color("bodyStyle")
    title_pt = title_pt or 44.0
    body_pt = body_pt or 18.0
    title_col = title_col or accent or text

    PX = 1280.0 / 960.0  # 16:9 slide: 960pt wide -> 1280px
    clamp = lambda v, lo, hi: max(lo, min(hi, v))
    # PowerPoint placeholder sizes can be unusually large (top-level body bullets
    # are often 28-32pt); clamp to ranges that stay legible in a Marp deck.
    title_px = clamp(round(title_pt * PX), 36, 66)
    body_px = clamp(round(body_pt * PX), 22, 30)
    h2_px = round(title_px * 0.66)
    h3_px = round(title_px * 0.52)

    def hx(v):  # "RRGGBB" -> "#rrggbb"
        return "#" + v.lower() if v and not v.startswith("#") else (v or "#000000")

    accent_vars = "\n".join(
        f"  --accent{i}: {hx(clr['accent'+str(i)])};"
        for i in range(1, 7) if clr.get("accent" + str(i)))

    fb_sans = '"Segoe UI", Helvetica, Arial, sans-serif'
    css = f"""/* @theme {name}
 * Generated from {os.path.basename(tpl)} by ppt-template-to-css.
 * Colors and fonts approximate the PowerPoint theme — tune as needed.
 * Pair with /md-to-pptx-editable:  --theme {name}.css
 */

@import 'default';

:root {{
  --bg: {hx(bg)};
  --text: {hx(text)};
  --accent: {hx(accent)};
  --title: {hx(title_col)};
  --link: {hx(hlink)};
{accent_vars}
  --font-head: "{major}", {fb_sans};
  --font-body: "{minor}", {fb_sans};
}}

section {{
  background-color: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: {body_px}px;
  line-height: 1.4;
  padding: 64px 72px;
}}

h1 {{
  font-family: var(--font-head);
  color: var(--title);
  font-size: {title_px}px;
  line-height: 1.15;
  margin: 0 0 24px;
}}
h2 {{ font-family: var(--font-head); color: var(--accent); font-size: {h2_px}px; }}
h3 {{ font-family: var(--font-head); color: var(--text);   font-size: {h3_px}px; }}

ul > li::marker {{ color: var(--accent); }}
strong {{ color: var(--accent); }}
a {{ color: var(--link); }}

/* pagination + footer */
section::after {{ color: var(--accent); }}
footer {{ color: var(--text); opacity: 0.7; }}
"""

    with open(out, "w") as f:
        f.write(css)

    print(f"OUT={out}")
    print(f"theme={name}  bg=#{bg.lower()}  text=#{text.lower()}  "
          f"accent=#{accent.lower()}  head='{major}'  body='{minor}'  "
          f"title={title_px}px  body_font={body_px}px")


if __name__ == "__main__":
    main()
