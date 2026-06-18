#!/usr/bin/env python3
"""Insert a block of text into a markdown journal relative to an anchor line.

UTF-8 safe: reads and writes bytes-as-text directly, so it matches lines
containing characters (→ ⏳ ❌ — CJK, NBSP, full-width punctuation) that the
Claude Code Edit tool can fail to match due to string normalization.

The anchor is matched as a SUBSTRING of a line. The new text is inserted on its
own line(s) immediately before or after the first matching line. If no line
matches the anchor, nothing is written and the script exits non-zero.

Usage:
    journal_insert.py --file PATH --anchor STR --position {before,after} --text STR

Pass newlines in --text as literal \n via shell $'...\n...' quoting.
"""
import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True, help="Path to the journal markdown file")
    ap.add_argument("--anchor", required=True, help="Substring identifying the anchor line")
    ap.add_argument("--position", choices=("before", "after"), default="before",
                    help="Insert the text before or after the anchor line")
    ap.add_argument("--text", required=True, help="Text block to insert (may contain newlines)")
    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    idx = next((i for i, ln in enumerate(lines) if args.anchor in ln), None)
    if idx is None:
        print(f"anchor not found: {args.anchor!r}", file=sys.stderr)
        return 1

    new_block = args.text.split("\n")
    insert_at = idx if args.position == "before" else idx + 1
    lines[insert_at:insert_at] = new_block

    with open(args.file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"inserted {len(new_block)} line(s) {args.position} line {idx + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
