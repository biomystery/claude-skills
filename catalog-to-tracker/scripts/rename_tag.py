#!/usr/bin/env python3
"""Rename a scheduling tag scheme across a folder of markdown notes.

Renaming happens more than once in practice — the first scheme is usually too
specific (grade or person baked in) and gets narrowed after the first real week.
Previews by default; pass --write to apply.

Usage:
  # preview
  python3 rename_tag.py --path "Study/Piano" --old "plan-wk" --new "piano26-wk"

  # apply, and give a subfolder its own slug
  python3 rename_tag.py --path "Study/Piano/Grade 3" --old "plan-wk" --new "piano26-wk" --write

Notes:
  --old / --new are literal substrings, not regexes: a tag stem like `plan-wk`
  renames `plan-wk1` … `plan-wk12` in one pass without touching `plan-wknote`
  unless you ask for it. Pass --regex to treat --old as a pattern. --new is always
  literal - backslashes in it are never read as group references.
"""
import argparse
import datetime
import pathlib
import re
import sys


def stamp_frontmatter(text, stamp):
    """Bump `updated:` inside the leading --- block only; never a matching body line."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    head, tail = text[:end], text[end:]
    return re.sub(r"^updated: .*$", f"updated: {stamp}", head, count=1, flags=re.M) + tail


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", required=True, help="folder to walk (recursive)")
    ap.add_argument("--old", required=True, help="tag stem to replace, without the leading #")
    ap.add_argument("--new", required=True, help="replacement stem")
    ap.add_argument("--glob", default="*.md")
    ap.add_argument("--regex", action="store_true", help="treat --old as a regex")
    ap.add_argument("--write", action="store_true", help="apply changes (default: preview only)")
    ap.add_argument("--no-stamp", action="store_true",
                    help="do not bump frontmatter updated: on changed files")
    args = ap.parse_args()

    root = pathlib.Path(args.path)
    if not root.exists():
        print(f"No such path: {root}", file=sys.stderr)
        return 1

    try:
        pattern = re.compile(args.old if args.regex else re.escape(args.old))
    except re.error as exc:
        print(f"--old is not a valid regex: {exc}", file=sys.stderr)
        return 2
    # --new is a literal: re.sub would otherwise read \1 or \t in it as an escape
    repl = args.new.replace("\\", "\\\\")
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    total_files = total_hits = skipped = 0

    files = [root] if root.is_file() else sorted(root.rglob(args.glob))
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            print(f"  unreadable, skipped: {p} ({exc.__class__.__name__})", file=sys.stderr)
            skipped += 1
            continue
        hits = len(pattern.findall(text))
        if not hits:
            continue
        total_files += 1
        total_hits += hits
        print(f"  {hits:3d}  {p}")
        if not args.write:
            continue
        text = pattern.sub(repl, text)
        if not args.no_stamp:
            text = stamp_frontmatter(text, stamp)
        p.write_text(text, encoding="utf-8")

    verb = "renamed" if args.write else "would rename"
    print(f"{verb} {total_hits} occurrence(s) in {total_files} file(s): "
          f"{args.old} -> {args.new}")
    if not args.write and total_hits:
        print("re-run with --write to apply")
    if args.write and total_hits:
        print(f"verify with: grep -rn '{args.old}' '{root}' --include='{args.glob}'  "
              "# must return nothing")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
