#!/usr/bin/env python3
"""Lint a figure and the code that produced it, for the defects that ship silently.

Plotting libraries fail QUIETLY. These four all reached a near-final deliverable
before being caught by eye:

  1. clipped axes        - hardcoded limits that no longer bracket the data
  2. dropped data        - explicit histogram bins discard out-of-range values
                           with no warning at all
  3. stale annotations   - a hardcoded "n.s." label sitting on a p = 0.006 result
  4. overclaiming text   - "at every position" when it held at 9 of 10

This checks what a machine can check. It does NOT replace opening the image and
looking at it - defect 1 in particular is usually only obvious by eye.

Usage:
    check_figure.py FIGURE.png [--source plotting_script.py]

Image checks need Pillow if available; source checks are stdlib-only.
"""
import argparse
import os
import re
import sys

# (regex, severity, message)
SOURCE_RULES = [
    (r"""["'][^"']*\bn\.?s\.?\b[^"']*["']""", 'HIGH',
     'hardcoded "n.s." in a label — recompute significance from the data instead'),
    (r"""["'][^"']*\bp\s*[=<>]\s*0?\.\d+[^"']*["']""", 'HIGH',
     'hardcoded p-value in a string — interpolate the computed value'),
    (r'set_[xy]lim\(\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\)', 'MED',
     'hardcoded axis limits — derive them from the data or they will clip when it changes'),
    (r'bins\s*=\s*np\.arange\([^)]*\)', 'MED',
     'explicit bins silently DROP out-of-range values — clip to an overflow bucket '
     'and report the true max'),
    (r"""["'][^"']*\b(every|all|always|never|none|no)\b\s+\w*(position|patient|case|sample|joint|group)""", 'HIGH',
     'absolute claim in a caption — verify it holds in every stratum, or soften it'),
    (r'\\U[0-9A-Fa-f]{8}', 'LOW',
     'literal \\U escape — some shells cannot parse it; paste the character instead'),
]

MISSING_GLYPH_HINT = ('→', '⇒', '≤', '≥')


def check_source(path):
    out = []
    try:
        src = open(path, encoding='utf-8').read()
    except OSError as e:
        return [('ERR', 0, str(e))]
    lines = src.split('\n')
    for rx, sev, msg in SOURCE_RULES:
        for i, ln in enumerate(lines, 1):
            if ln.lstrip().startswith('#'):
                continue
            if re.search(rx, ln):
                out.append((sev, i, f'{msg}\n         {ln.strip()[:96]}'))
    for i, ln in enumerate(lines, 1):
        if any(g in ln for g in MISSING_GLYPH_HINT) and ('title' in ln or 'label' in ln
                                                         or 'text' in ln or 'foot' in ln):
            out.append(('LOW', i,
                        'arrow/comparison glyph in a label — many fonts lack it and '
                        'matplotlib renders a blank box; verify in the rendered image'))
    return out


def check_image(path):
    try:
        from PIL import Image
    except ImportError:
        return None, 'Pillow not installed — skipping image checks (pip install pillow)'
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.load()
    bg = px[0, 0]

    def row_has_ink(y):
        return any(px[x, y] != bg for x in range(0, w, max(1, w // 400)))

    def col_has_ink(x):
        return any(px[x, y] != bg for y in range(0, h, max(1, h // 400)))

    findings = []
    for name, hit in (('top', row_has_ink(0)), ('bottom', row_has_ink(h - 1)),
                      ('left', col_has_ink(0)), ('right', col_has_ink(w - 1))):
        if hit:
            findings.append(('MED', 0, f'content touches the {name} edge — possible clipping'))
    ink = sum(1 for y in range(0, h, 8) for x in range(0, w, 8) if px[x, y] != bg)
    total = len(range(0, h, 8)) * len(range(0, w, 8))
    frac = ink / total
    if frac < 0.02:
        findings.append(('HIGH', 0, f'image is {100*frac:.1f}% ink — is it blank or did rendering fail?'))
    return findings, f'{w}x{h}, {100*frac:.1f}% non-background'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('figure')
    ap.add_argument('--source', help='The script that generated the figure')
    args = ap.parse_args()

    rc = 0
    if not os.path.exists(args.figure):
        print(f'no such figure: {args.figure}', file=sys.stderr)
        return 1

    print(f'FIGURE  {os.path.basename(args.figure)}')
    img = check_image(args.figure)
    if img[0] is None:
        print(f'  {img[1]}')
    else:
        findings, info = img
        print(f'  {info}')
        for sev, _, msg in findings:
            print(f'  [{sev}] {msg}')
            rc = rc or (1 if sev == 'HIGH' else 0)

    if args.source:
        print(f'\nSOURCE  {os.path.basename(args.source)}')
        found = check_source(args.source)
        if not found:
            print('  no lint hits')
        for sev, line, msg in found:
            print(f'  [{sev}] line {line}: {msg}')
            if sev == 'HIGH':
                rc = 1

    print('\nNow OPEN THE IMAGE AND LOOK AT IT. Clipped axes and wrong captions are')
    print('usually only visible by eye. This script narrows the search; it does not')
    print('replace the look.')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
