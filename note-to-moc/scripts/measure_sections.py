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
tree of spokes with --brief to find which ones still need promoting:

    find . -name '*.md' -not -path './.backup/*' -print0 \
      | xargs -0 measure_sections.py --brief
"""
import argparse
import os
import re
import sys

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEAD_RE = re.compile(r"^(#{1,6})\s+\S")


def mask_fenced(lines):
    """Blank out fenced-code lines so their `#` lines are not read as headings.

    A bash comment inside a fence is not a heading, and a fenced example holding
    `## Status` is not a section of this note. Two rules matter:
      - the closing marker must be at least as long as the opening one, so a
        ```` ```` ```` block is not closed by an inner ``` ``` ```;
      - an UNCLOSED fence masks nothing. Treating a stray ``` as opening a fence
        that runs to EOF would blank the rest of the file and silently report the
        note as structureless.
    """
    opens = []
    in_fence, marker = False, ""
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if not m:
            continue
        if not in_fence:
            in_fence, marker = True, m.group(1)
            opens.append([i, None])
        elif m.group(1)[0] == marker[0] and len(m.group(1)) >= len(marker):
            in_fence = False
            opens[-1][1] = i
    out = list(lines)
    for start, end in opens:
        if end is None:               # unterminated - mask nothing
            continue
        for i in range(start, end + 1):
            out[i] = ""
    return out


def analyse(path, level):
    """Return (rows, flags, n_top, n_lines, n_heads) for one note, or None."""
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {path}: {e}", file=sys.stderr)
        return None

    scan = mask_fenced(raw)
    all_heads = []
    for i, l in enumerate(scan):
        m = HEAD_RE.match(l)
        if m and len(m.group(1)) <= level:
            all_heads.append((i + 1, len(m.group(1)), l))

    # "Top level" is the shallowest depth that actually carries the note's
    # sections, not a hardcoded `##`. Take the shallowest depth with at least
    # three headings: that skips a lone `# Title` in a `##`-sectioned note, and
    # still finds the sections of a note that sections itself with `#`. Calling
    # the latter INDIVISIBLE told the user to leave their biggest, most
    # organised notes alone.
    depths = sorted({d for _, d, _ in all_heads})
    counts = {d: sum(1 for _, dd, _ in all_heads if dd == d) for d in depths}
    top_depth = next((d for d in depths if counts[d] >= 3), depths[0] if depths else None)
    n_top = counts.get(top_depth, 0)

    heads = [h for h in all_heads if h[1] >= top_depth] if depths else []

    rows = []
    for idx, (ln, _, text) in enumerate(heads):
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
    return rows, flags, n_top, len(raw), len(all_heads)


def verdict_for(n_lines, n_top, n_heads, flags, split_at, watch_at):
    """Mechanical split rule. Encodes the skill's own 'when to use' criteria.

    Flags only ever ESCALATE a note that is already long enough to be worth
    watching. They never create a verdict on their own: a freshly written 18-line
    hub puts its status callout past the midpoint by design, which trips BURIED,
    and telling the user to reorder the hub the skill just wrote is nonsense.
    """
    hot = any(f[0] in ("HOTSPOT", "BURIED") for f in flags)
    if n_lines >= split_at and n_heads == 0:
        return ("UNSTRUCTURED",
                f"{n_lines} lines and no headings - cannot propose a split; "
                "read it and add headings first, or check this is the right file")
    if n_lines >= split_at and n_top < 3:
        return ("INDIVISIBLE",
                f"{n_lines} lines but only {n_top} top-level section(s) - "
                "likely one document; give it a hub neighbour, do not carve it up")
    if n_lines >= split_at:
        return ("SPLIT", f"{n_lines} lines across {n_top} top-level sections")
    if n_lines >= watch_at and hot and n_top >= 3:
        return ("SPLIT", f"{n_lines} lines, {n_top} sections, and "
                         + ", ".join(sorted({f[0] for f in flags if f[0] != 'DENSE'})))
    if n_lines >= watch_at:
        return ("WATCH", f"{n_lines} lines - reorder in place before splitting")
    return ("LEAVE", f"{n_lines} lines - healthy")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("notes", nargs="+")
    ap.add_argument("--level", type=int, default=3,
                    help="deepest heading level to report (2-6, default 3)")
    ap.add_argument("--brief", action="store_true",
                    help="one VERDICT line per note; skip the per-section table")
    ap.add_argument("--split-at", type=int, default=400,
                    help="line count at or above which a note should be split (default 400)")
    ap.add_argument("--watch-at", type=int, default=300,
                    help="line count at or above which a note is worth watching (default 300)")
    args = ap.parse_args()

    if not 2 <= args.level <= 6:
        print("--level must be between 2 and 6", file=sys.stderr)
        return 2
    if args.watch_at < 1 or args.split_at < 1:
        print("--watch-at and --split-at must be >= 1", file=sys.stderr)
        return 2
    if args.watch_at > args.split_at:
        print("--watch-at must be <= --split-at", file=sys.stderr)
        return 2

    any_ok = False
    for path in args.notes:
        res = analyse(path, args.level)
        if res is None:
            continue                     # already reported; keep sweeping
        any_ok = True
        rows, flags, n_top, n_lines, n_heads = res
        tag, reason = verdict_for(n_lines, n_top, n_heads, flags,
                                  args.split_at, args.watch_at)

        if args.brief:
            note = "" if n_heads else "  [no headings found - right file?]"
            print(f"{tag:<13} {path}  ({reason}){note}")
            continue

        print(f"\n=== {path}")
        print(f"TOTAL: {n_lines} lines, {os.path.getsize(path)/1024:.1f} KB, "
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
