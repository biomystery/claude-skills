#!/usr/bin/env python3
"""
Generate a business-styled pandoc reference .docx.

Styles applied:
  Heading 1/2    — Calibri Light, dark navy (#1E3A5F)
  Heading 3      — Calibri bold, dark slate (#334155)
  VerbatimChar   — Consolas 9.5pt, dark slate (#2D3748)   [inline code]
  Source Code    — Consolas 9pt, light gray bg, gray left bar  [fenced code blocks]
  Block Text     — Calibri 10.5pt, light blue bg, blue left bar  [blockquotes]
  Normal         — Calibri 11pt

Usage:
  python3 make_reference.py [output_path]

Default output: business-reference.docx in the same directory as this script.
"""

import subprocess, sys, os

# ── ensure python-docx is available ──────────────────────────────────────────
try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.enum.style import WD_STYLE_TYPE
except ImportError:
    print("Installing python-docx…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.enum.style import WD_STYLE_TYPE

# ── helpers ───────────────────────────────────────────────────────────────────

def hex_rgb(h):
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def set_para_shading(style, fill_hex):
    pPr = style.element.get_or_add_pPr()
    for el in pPr.findall(qn('w:shd')):
        pPr.remove(el)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    pPr.append(shd)

def set_left_border(style, color_hex, sz=18, space=4):
    pPr = style.element.get_or_add_pPr()
    pBdr = pPr.find(qn('w:pBdr'))
    if pBdr is None:
        pBdr = OxmlElement('w:pBdr')
        pPr.append(pBdr)
    for el in pBdr.findall(qn('w:left')):
        pBdr.remove(el)
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), str(sz))
    left.set(qn('w:space'), str(space))
    left.set(qn('w:color'), color_hex)
    pBdr.append(left)

def set_para_indent(style, left_twips=360):
    pPr = style.element.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    ind.set(qn('w:left'), str(left_twips))

def set_para_spacing(style, before=None, after=None, line=None):
    pPr = style.element.get_or_add_pPr()
    spc = pPr.find(qn('w:spacing'))
    if spc is None:
        spc = OxmlElement('w:spacing')
        pPr.append(spc)
    if before is not None: spc.set(qn('w:before'), str(before))
    if after  is not None: spc.set(qn('w:after'),  str(after))
    if line   is not None:
        spc.set(qn('w:line'), str(line))
        spc.set(qn('w:lineRule'), 'auto')

def set_font_color_xml(style, color_hex):
    rPr = style.element.find(qn('w:rPr'))
    if rPr is None:
        rPr = OxmlElement('w:rPr')
        style.element.append(rPr)
    for el in rPr.findall(qn('w:color')):
        rPr.remove(el)
    col = OxmlElement('w:color')
    col.set(qn('w:val'), color_hex)
    rPr.append(col)

# ── build reference doc ───────────────────────────────────────────────────────

def build(out_path):
    # Start from pandoc's own default reference so all required styles exist
    result = subprocess.run(
        ["pandoc", "--print-default-data-file", "reference.docx"],
        capture_output=True
    )
    if result.returncode != 0:
        print("ERROR: pandoc not found. Install pandoc first.", file=sys.stderr)
        sys.exit(1)

    tmp_default = out_path + ".default.tmp"
    with open(tmp_default, 'wb') as f:
        f.write(result.stdout)

    doc = Document(tmp_default)
    os.remove(tmp_default)

    # Heading 1 — Calibri Light 18pt, dark navy
    h1 = doc.styles['Heading 1']
    h1.font.name = 'Calibri Light'
    h1.font.size = Pt(18)
    h1.font.bold = False
    set_font_color_xml(h1, '1E3A5F')
    set_para_spacing(h1, before=240, after=120)

    # Heading 2 — Calibri Light 13pt, dark navy
    h2 = doc.styles['Heading 2']
    h2.font.name = 'Calibri Light'
    h2.font.size = Pt(13)
    h2.font.bold = False
    set_font_color_xml(h2, '1E3A5F')
    set_para_spacing(h2, before=200, after=80)

    # Heading 3 — Calibri 11pt bold, dark slate
    h3 = doc.styles['Heading 3']
    h3.font.name = 'Calibri'
    h3.font.size = Pt(11)
    h3.font.bold = True
    set_font_color_xml(h3, '334155')
    set_para_spacing(h3, before=160, after=60)

    # VerbatimChar — inline code: Consolas, dark slate
    vc = doc.styles['Verbatim Char']
    vc.font.name = 'Consolas'
    vc.font.size = Pt(9.5)
    vc.font.bold = False
    set_font_color_xml(vc, '2D3748')

    # Source Code — fenced code blocks: light gray bg, gray left bar
    style_names = [s.name for s in doc.styles]
    if 'Source Code' not in style_names:
        sc = doc.styles.add_style('Source Code', WD_STYLE_TYPE.PARAGRAPH)
        sc.base_style = doc.styles['Normal']
    else:
        sc = doc.styles['Source Code']
    sc.font.name = 'Consolas'
    sc.font.size = Pt(9)
    set_font_color_xml(sc, '1A202C')
    set_para_shading(sc, 'F4F6F8')
    set_left_border(sc, '718096', sz=16, space=6)
    set_para_indent(sc, left_twips=200)
    set_para_spacing(sc, before=80, after=80, line=276)

    # Block Text — blockquotes: light blue bg, blue left bar
    bt = doc.styles['Block Text']
    bt.font.name = 'Calibri'
    bt.font.size = Pt(10.5)
    set_para_shading(bt, 'EBF4FD')
    set_left_border(bt, '3B82F6', sz=20, space=6)
    set_para_indent(bt, left_twips=240)
    set_para_spacing(bt, before=80, after=80)

    # Normal — body text
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)

    doc.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', 'business-reference.docx')
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else default_out)
    build(out)
