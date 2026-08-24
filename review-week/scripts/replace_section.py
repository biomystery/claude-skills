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

If the heading is missing and --insert-before is given, a new section is
inserted immediately before that heading (used when older weekly notes lack
People / Goals sections).

Usage:
    replace_section.py --file PATH --heading "## Wins" --body STR
    replace_section.py --file PATH --heading "## People" --body STR \\
        --insert-before "## Wins"
"""
import argparse
import sys


def heading_depth(line: str) -> int:
    stripped = line.lstrip("#")
    return len(line) - len(stripped)


def find_heading(lines, target: str):
    return next((i for i, ln in enumerate(lines) if ln.strip() == target), None)


def replace_body(lines, start: int, body_lines):
    depth = heading_depth(lines[start].lstrip())
    end = len(lines)
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.lstrip().startswith("#") and heading_depth(ln.lstrip()) <= depth:
            end = i
            break
    return lines[: start + 1] + [""] + body_lines + [""] + lines[end:], end


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True)
    ap.add_argument("--heading", required=True, help="Exact heading line, e.g. '## Wins'")
    ap.add_argument("--body", required=True, help="Replacement body text (may contain \\n)")
    ap.add_argument(
        "--insert-before",
        default=None,
        help="If --heading is missing, insert a new section before this heading",
    )
    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    target = args.heading.strip()
    body_lines = args.body.split("\n")
    start = find_heading(lines, target)

    if start is None:
        if not args.insert_before:
            print(f"heading not found: {target!r}", file=sys.stderr)
            return 1
        before_target = args.insert_before.strip()
        before = find_heading(lines, before_target)
        if before is None:
            print(
                f"heading not found: {target!r}; insert-before also missing: {before_target!r}",
                file=sys.stderr,
            )
            return 1
        new_block = [target, ""] + body_lines + [""]
        new_lines = lines[:before] + new_block + lines[before:]
        action = f"inserted section {target!r} before {before_target!r}"
    else:
        new_lines, end = replace_body(lines, start, body_lines)
        action = (
            f"replaced section {target!r}: lines {start + 1}-{end - 1} "
            f"-> {len(body_lines)} line(s)"
        )

    with open(args.file, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
