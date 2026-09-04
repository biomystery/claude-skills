#!/usr/bin/env python3
"""Enumerate EVERY container in a data source, so absence can never be assumed.

The failure this prevents: scanning one sheet of a multi-sheet workbook, or one
table of a database, and concluding "this file has no treatment variables" /
"there is no date column". Both are claims about the whole source, made from a
sample of it.

    "I did not find it" is not "it does not exist."

Supports .xlsx / .xls (stdlib only - reads the OOXML zip directly, no openpyxl),
.csv / .tsv, and .sqlite / .db. Prints every sheet/table, its dimensions, and
every column name, then a flat searchable index of all columns.

Usage:
    enumerate_source.py FILE [--grep PATTERN]

--grep searches the flat column index case-insensitively, so you can check for a
variable across the entire source in one pass:

    enumerate_source.py dataset.xlsx --grep 'dose|exposure|treat|covariate'
"""
import argparse
import csv
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/package/2006/relationships}'
ONS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def _xlsx_sheets(path):
    """Yield (sheet_name, n_rows, [column headers]) for every sheet."""
    zf = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in zf.namelist():
        root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
        for si in root.findall(NS + 'si'):
            shared.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    wb = ET.fromstring(zf.read('xl/workbook.xml'))
    rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    rid = {r.get('Id'): r.get('Target') for r in rels.findall(RNS + 'Relationship')}

    for sh in wb.iter(NS + 'sheet'):
        name = sh.get('name')
        target = rid.get(sh.get(ONS + 'id'), '')
        member = 'xl/' + target.lstrip('/').replace('xl/', '')
        if member not in zf.namelist():
            yield name, 0, []
            continue
        ws = ET.fromstring(zf.read(member))
        rows = list(ws.iter(NS + 'row'))
        headers = []
        if rows:
            for c in rows[0].findall(NS + 'c'):
                v = c.find(NS + 'v')
                if v is None:
                    headers.append('')
                    continue
                headers.append(shared[int(v.text)] if c.get('t') == 's' else (v.text or ''))
        yield name, max(0, len(rows) - 1), headers


def _delim_headers(path):
    delim = '\t' if path.lower().endswith(('.tsv', '.tab')) else ','
    with open(path, newline='', encoding='utf-8-sig', errors='replace') as f:
        r = csv.reader(f, delimiter=delim)
        headers = next(r, [])
        n = sum(1 for _ in r)
    return [(os.path.basename(path), n, headers)]


def _sqlite_tables(path):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")
    out = []
    for (t,) in cur.fetchall():
        cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{t}")')]
        try:
            n = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        except sqlite3.Error:
            n = -1
        out.append((t, n, cols))
    con.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file')
    ap.add_argument('--grep', help='Regex to search the flat column index (case-insensitive)')
    args = ap.parse_args()

    p = args.file
    if not os.path.exists(p):
        print(f'no such file: {p}', file=sys.stderr)
        return 1

    low = p.lower()
    if low.endswith(('.xlsx', '.xlsm', '.xls')):
        containers = list(_xlsx_sheets(p))
        kind = 'sheet'
    elif low.endswith(('.csv', '.tsv', '.tab')):
        containers = _delim_headers(p)
        kind = 'file'
    elif low.endswith(('.sqlite', '.sqlite3', '.db')):
        containers = _sqlite_tables(p)
        kind = 'table'
    else:
        print(f'unsupported extension: {p}', file=sys.stderr)
        return 1

    total_cols = sum(len(c) for _, _, c in containers)
    print(f'{os.path.basename(p)}  —  {len(containers)} {kind}(s), {total_cols} columns total')
    print('=' * 78)
    for name, nrows, cols in containers:
        print(f'\n[{kind}] {name}   rows={nrows}   cols={len(cols)}')
        for i, c in enumerate(cols):
            print(f'    {i:>4}  {c}')

    print('\n' + '=' * 78)
    print(f'FLAT INDEX — {total_cols} columns across {len(containers)} {kind}(s)')
    flat = [(cn, c) for cn, _, cols in containers for c in cols]
    if args.grep:
        rx = re.compile(args.grep, re.I)
        hits = [(cn, c) for cn, c in flat if rx.search(c)]
        print(f"grep {args.grep!r}: {len(hits)} hit(s)")
        for cn, c in hits:
            print(f'    [{cn}] {c}')
        if not hits:
            print('    none — absence is now supported by a COMPLETE enumeration,')
            print('    not by a partial scan.')
    else:
        print('(pass --grep PATTERN to search for a variable across every container)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
