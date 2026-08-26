#!/usr/bin/env python3
"""Verify a catalog->tracker conversion against the pre-change backup.

Checks, per file:
  1. every stable ID present before is still present after  (nothing dropped)
  2. no ID gained occurrences                                (nothing invented)
  3. every URL present before is still present after         (no dead rewrites)
  4. every completion date present before is still present  (no lost history)

A backup that matches no files is itself a failure: an empty or mistyped --backup would
otherwise make this gate pass vacuously.

An ID legitimately appears more than once after conversion when it was scheduled in
more than one cycle: those occurrences are distinct events, each with its own tag and
completion date. What must never happen is an ID coming out with MORE occurrences than
it went in with — that is the conversion duplicating rather than merging.

Exit code 1 if any check fails, so it can gate a commit.

Usage:
  python3 verify_merge.py --backup /tmp/backup --current "Modules" \
      --id-pattern '[A-Z]+\\.\\d+'
"""
import argparse
import pathlib
import re
import sys

DEFAULT_ID = r"[A-Z]+\.\d+"
DONE_RE = re.compile(r"✅\s*\d{4}-\d{2}-\d{2}")


def scan(path, id_re, url_re):
    text = path.read_text(encoding="utf-8")
    ids = {}
    for m in id_re.finditer(text):
        ids[m.group(0)] = ids.get(m.group(0), 0) + 1
    return ids, set(url_re.findall(text)), len(DONE_RE.findall(text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backup", required=True, help="directory holding pre-change copies")
    ap.add_argument("--current", required=True, help="directory holding the converted files")
    ap.add_argument("--id-pattern", default=DEFAULT_ID)
    ap.add_argument("--glob", default="*.md")
    args = ap.parse_args()

    try:
        id_re = re.compile(rf"\b(?:{args.id_pattern})\b")
    except re.error as exc:
        print(f"--id-pattern is not a valid regex: {exc}", file=sys.stderr)
        sys.exit(2)
    url_re = re.compile(r"\]\((https?://\S+?)\)")

    backup = pathlib.Path(args.backup)
    current = pathlib.Path(args.current)
    if not backup.is_dir():
        print(f"--backup is not a directory: {backup}", file=sys.stderr)
        sys.exit(2)
    if not current.is_dir():
        print(f"--current is not a directory: {current}", file=sys.stderr)
        sys.exit(2)
    failures, checked = [], 0

    for old in sorted(backup.glob(args.glob)):
        new = current / old.name
        if not new.exists():
            failures.append(f"{old.name}: missing after conversion")
            continue
        checked += 1
        old_ids, old_urls, old_done = scan(old, id_re, url_re)
        new_ids, new_urls, new_done = scan(new, id_re, url_re)

        dropped = sorted(set(old_ids) - set(new_ids))
        if dropped:
            failures.append(f"{old.name}: IDs vanished -> {', '.join(dropped)}")

        gained = sorted(i for i, n in new_ids.items() if n > old_ids.get(i, 0))
        if gained:
            detail = ", ".join(f"{i} ({old_ids.get(i, 0)}->{new_ids[i]})" for i in gained)
            failures.append(f"{old.name}: IDs gained occurrences -> {detail}")

        lost_urls = sorted(old_urls - new_urls)
        if lost_urls:
            failures.append(f"{old.name}: {len(lost_urls)} URL(s) lost, e.g. {lost_urls[0]}")

        if new_done < old_done:
            failures.append(f"{old.name}: {old_done - new_done} completion date(s) lost "
                            f"({old_done}->{new_done})")

        merged = sum(old_ids.values()) - sum(new_ids.values())
        repeats = sum(n - 1 for n in new_ids.values() if n > 1)
        note = f", {repeats} scheduled repeat(s) kept" if repeats else ""
        print(f"  {old.name}: {len(new_ids)} unique IDs, "
              f"{merged} duplicate occurrence(s) merged{note}")

    print(f"\nchecked {checked} file(s)")
    if not checked and not failures:
        print(f"\nFAILED:\n  - nothing to check: no '{args.glob}' files in {backup}")
        sys.exit(1)
    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
