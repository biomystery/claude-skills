#!/usr/bin/env python3
"""Report per-section size of markdown notes, to diagnose WHERE they are overgrown.

Usage:  measure_sections.py NOTE.md [NOTE2.md ...] [--level 3] [--brief]

Prints one row per heading: start line, line count, byte size, heading text,
then a VERDICT line saying whether the note should be split.

Read the output for three signals before you split anything:
  1. HOTSPOTS  - sections far larger than their siblings
  2. BURIED    - a "Status"/"Current state" heading late in the file
  3. DENSITY   - few lines but many bytes = mega-bullets mixing claim and evidence

VERDICT is the mechanical stopping rule for recursive refactors. Pass a whole
folder of spokes with --brief to find which ones still need promoting:

    measure_sections.py Threads/*.md --brief
"""
import argparse
import os
import re
import sys

FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")


def mask_fenced(lines):
    """Return a copy of `lines` with fenced-code lines blanked out.

    A bash comment inside a fence (`# do the thing`) is not a heading, and a
    fenced example containing `## Status` is not a section of this note.
    """
    out, in_fence, marker = [], False, ""
    for line in lines:
        m = FENCE_RE.match(line)
        if m and not in_fence:
            in_fence, marker = True, m.group(1)
            out.append("")
            continue
        if in_fence:
            out.append("")
            if m and m.group(1) == marker:
                in_fence = False
            continue
        out.append(line)
    return out


def analyse(path, level):
    """Return (rows, flags, verdict, reason) for one note, or None if unreadable."""
    try:
        raw = open(path, encoding="utf-8").read().split("\n")
    except OSError as e:
        print(f"cannot read {path}: {e}", file=sys.stderr)
        return None

    scan = mask_fenced(raw)
    pat = re.compile(r"^#{2,%d} " % level)
    top = re.compile(r"^## ")
    heads = [(i + 1, l) for i, l in enumerate(scan) if pat.match(l)]
    n_top = sum(1 for _, l in heads if top.match(l))

    rows = []
    for idx, (ln, text) in enumerate(heads):
        end = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(raw)
        body = "\n".join(raw[ln - 1:end])
        rows.append((ln, end - ln + 1, len(body.encode()), text))

    flags = []
    if rows:
        avg = sum(r[2] for r in rows) / len(rows)
        for ln, count, nbytes, text in rows:
            if nbytes > 3 * avg:
                flags.append(("HOTSPOT", ln,
                              f"{nbytes/1024:.1f} KB - split candidate: {text[:50]}"))
            if count and nbytes / count > 250:
                flags.append(("DENSE", ln,
                              f"{nbytes/count:.0f} B/line - mega-bullets: {text[:50]}"))
        for ln, _, _, text in rows:
            if re.search(r"status|current|posture", text, re.I) and ln > len(raw) * 0.5:
                flags.append(("BURIED", ln,
                              f"status-like heading past the halfway mark: {text[:50]}"))
    return rows, flags, n_top, len(raw)


def verdict_for(n_lines, n_top, flags, split_at, watch_at):
    """Mechanical split rule. Encodes the skill's own 'when to use' criteria."""
    hot = any(f[0] in ("HOTSPOT", "BURIED") for f in flags)
    if n_lines >= split_at and n_top < 3:
        return ("INDIVISIBLE",
                f"{n_lines} lines but only {n_top} top-level section(s) - "
                "likely one document; give it a hub neighbour, do not carve it up")
    if n_lines >= split_at:
        return ("SPLIT", f"{n_lines} lines across {n_top} top-level sections")
    if n_lines >= watch_at and hot and n_top >= 3:
        return ("SPLIT", f"{n_lines} lines, {n_top} sections, and "
                         + ", ".join(sorted({f[0] for f in flags if f[0] != 'DENSE'})))
    if n_lines >= watch_at or hot:
        return ("WATCH", f"{n_lines} lines - reorder in place before splitting")
    return ("LEAVE", f"{n_lines} lines - healthy")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("notes", nargs="+")
    ap.add_argument("--level", type=int, default=3,
                    help="deepest heading level to report (default 3)")
    ap.add_argument("--brief", action="store_true",
                    help="one VERDICT line per note; skip the per-section table")
    ap.add_argument("--split-at", type=int, default=400,
                    help="line count at or above which a note should be split (default 400)")
    ap.add_argument("--watch-at", type=int, default=300,
                    help="line count at or above which a note is worth watching (default 300)")
    args = ap.parse_args()

    if args.watch_at > args.split_at:
        print("--watch-at must be <= --split-at", file=sys.stderr)
        return 2

    any_ok = False
    for path in args.notes:
        res = analyse(path, args.level)
        if res is None:
            continue
        any_ok = True
        rows, flags, n_top, n_lines = res
        nbytes = os.path.getsize(path)
        tag, reason = verdict_for(n_lines, n_top, flags, args.split_at, args.watch_at)

        if args.brief:
            print(f"{tag:<12} {path}  ({reason})")
            continue

        print(f"\n=== {path}")
        print(f"TOTAL: {n_lines} lines, {nbytes/1024:.1f} KB, "
              f"{n_top} top-level section(s)\n")
        if not rows:
            print("  no headings found - is this the right file?")
        for ln, count, nb, text in rows:
            print(f"L{ln:>5}  {count:>4} lines  {nb/1024:>6.1f} KB  {text[:70]}")
        if flags:
            print()
        for kind, ln, msg in flags:
            print(f"  {kind:<8} L{ln}: {msg}")
        print(f"\nVERDICT: {tag} - {reason}")

    return 0 if any_ok else 1


if __name__ == "__main__":
    sys.exit(main())
