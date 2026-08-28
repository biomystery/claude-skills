#!/usr/bin/env python3
"""Report per-section size of a markdown note, to diagnose WHERE it is overgrown.

Usage:  measure_sections.py NOTE.md [--level 3]

Prints one row per heading: start line, line count, byte size, heading text.
Read the output for three signals before you split anything:
  1. HOTSPOTS  - sections far larger than their siblings
  2. BURIED    - a "Status"/"Current state" heading late in the file
  3. DENSITY   - few lines but many bytes = mega-bullets mixing claim and evidence
"""
import argparse
import re
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("note")
    ap.add_argument("--level", type=int, default=3,
                    help="deepest heading level to report (default 3)")
    args = ap.parse_args()

    try:
        lines = open(args.note, encoding="utf-8").read().split("\n")
    except OSError as e:
        print(f"cannot read {args.note}: {e}", file=sys.stderr)
        return 1

    pat = re.compile(r"^#{2,%d} " % args.level)
    heads = [(i + 1, l) for i, l in enumerate(lines) if pat.match(l)]
    if not heads:
        print("no headings found - is this the right file?", file=sys.stderr)
        return 1

    print(f"TOTAL: {len(lines)} lines, {len(chr(10).join(lines).encode())/1024:.1f} KB\n")
    rows = []
    for idx, (ln, text) in enumerate(heads):
        end = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)
        body = "\n".join(lines[ln - 1:end])
        rows.append((ln, end - ln + 1, len(body.encode()), text))

    for ln, count, nbytes, text in rows:
        print(f"L{ln:>5}  {count:>4} lines  {nbytes/1024:>6.1f} KB  {text[:70]}")

    print()
    avg = sum(r[2] for r in rows) / len(rows)
    for ln, count, nbytes, text in rows:
        if nbytes > 3 * avg:
            print(f"  HOTSPOT  L{ln}: {nbytes/1024:.1f} KB - split candidate: {text[:50]}")
        if count and nbytes / count > 250:
            print(f"  DENSE    L{ln}: {nbytes/count:.0f} B/line - mega-bullets: {text[:50]}")
    for ln, _, _, text in rows:
        if re.search(r"status|current|posture", text, re.I) and ln > len(lines) * 0.5:
            print(f"  BURIED   L{ln}: status-like heading past the halfway mark: {text[:50]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
