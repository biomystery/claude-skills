#!/usr/bin/env python3
"""Replace the body of one markdown section between its heading line and the
next heading of equal-or-shallower depth (or EOF).

UTF-8 safe: reads and writes bytes-as-text directly, so it isn't defeated by
the Edit tool's string-normalization mismatches against template
placeholder text -- Obsidian weekly-note templates commonly use curly quotes
(') or CJK punctuation in their prompt lines (e.g. '"What went well...?"')
that look identical to a plain apostrophe but fail an exact Edit match.

The heading is matched as an exact stripped-line match (include the leading
#'s). Everything between that heading and the next heading of depth <= its
own depth is replaced with --body, framed by a single blank line on each
side.

Usage:
    replace_section.py --file PATH --heading "## Wins" --body STR
"""
import argparse
import sys


def heading_depth(line: str) -> int:
    stripped = line.lstrip("#")
    return len(line) - len(stripped)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True)
    ap.add_argument("--heading", required=True, help="Exact heading line, e.g. '## Wins'")
    ap.add_argument("--body", required=True, help="Replacement body text (may contain \\n)")
    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    target = args.heading.strip()
    depth = heading_depth(target)

    start = next((i for i, ln in enumerate(lines) if ln.strip() == target), None)
    if start is None:
        print(f"heading not found: {target!r}", file=sys.stderr)
        return 1

    end = len(lines)
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.lstrip().startswith("#") and heading_depth(ln.lstrip()) <= depth:
            end = i
            break

    body_lines = args.body.split("\n")
    new_lines = lines[: start + 1] + [""] + body_lines + [""] + lines[end:]

    with open(args.file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"replaced section {target!r}: lines {start + 1}-{end - 1} -> {len(body_lines)} line(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
