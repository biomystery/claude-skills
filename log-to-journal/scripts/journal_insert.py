#!/usr/bin/env python3
"""Insert a block of text into a markdown journal relative to an anchor line.

UTF-8 safe: reads and writes text directly, so it matches lines containing
characters (→ ⏳ ❌ — CJK, NBSP, full-width punctuation) that the Claude Code
Edit tool can fail to match due to string normalization.

The anchor is matched as a SUBSTRING of a line. The new text is inserted on its
own line(s) immediately before or after the first matching line. If no line
matches the anchor, nothing is written and the script exits non-zero.

Two ways to supply the text
---------------------------
Prefer --stdin. It avoids shell quoting entirely, which matters because zsh's
$'...' cannot express emoji: it supports \\u (4 hex digits) but not \\U (8), and
every emoji lives above U+FFFF. Writing $'\\U0001F3AF' aborts the whole command
with "zsh: character not in range".

    python3 journal_insert.py --file J.md --anchor "- 10:00" --position before --stdin <<'TXT'
    - 16:38 🎯 headline
    \t- detail with a [[wikilink]] and $literal dollars
    TXT

--text still works for a single short line with no emoji and no tabs:

    python3 journal_insert.py --file J.md --anchor "- 10:00" --position before \\
        --text "- 16:38 done"

Also supports --update-frontmatter to bump the YAML `updated:` field in the same
pass, so the caller does not need a second edit.
"""
import argparse
import re
import sys


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", required=True, help="Path to the journal markdown file")
    ap.add_argument("--anchor", required=True, help="Substring identifying the anchor line")
    ap.add_argument("--position", choices=("before", "after"), default="before",
                    help="Insert the text before or after the anchor line")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Text block to insert. Avoid for emoji or tabs "
                                    "- zsh cannot express them in $'...'. Use --stdin.")
    src.add_argument("--stdin", action="store_true",
                     help="Read the text block from stdin (preferred; no shell quoting)")
    ap.add_argument("--update-frontmatter", metavar="TIMESTAMP",
                    help="Also set the YAML 'updated:' field, e.g. 2026-09-03T16:38")
    args = ap.parse_args()

    text = sys.stdin.read().rstrip("\n") if args.stdin else args.text
    if not text:
        print("empty text block, nothing to insert", file=sys.stderr)
        return 1

    with open(args.file, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")

    idx = next((i for i, ln in enumerate(lines) if args.anchor in ln), None)
    if idx is None:
        print(f"anchor not found: {args.anchor!r}", file=sys.stderr)
        return 1

    new_block = text.split("\n")
    insert_at = idx if args.position == "before" else idx + 1
    lines[insert_at:insert_at] = new_block
    out = "\n".join(lines)

    if args.update_frontmatter:
        out, n = re.subn(r"^updated: .*$", f"updated: {args.update_frontmatter}",
                         out, count=1, flags=re.M)
        if not n:
            print("warning: no 'updated:' field found in frontmatter", file=sys.stderr)

    with open(args.file, "w", encoding="utf-8") as f:
        f.write(out)

    msg = f"inserted {len(new_block)} line(s) {args.position} line {idx + 1}"
    if args.update_frontmatter:
        msg += f"; updated: {args.update_frontmatter}"
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
