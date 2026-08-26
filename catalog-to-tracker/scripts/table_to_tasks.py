#!/usr/bin/env python3
"""Convert a markdown catalog table into a grouped checkbox tracker, merging in an
optional duplicate "scheduled items" section so no item is checkable in two places.

Typical before (one note):

    ## Scheduled
    - [x] Mon · A.1 [Do the thing](https://example.com/a1) ✅ 2026-01-05 #plan-wk1

    ## Items
    | Item | Period | Status |
    |---|---|---|
    | **A. First group** | — | |
    | [A.1 Do the thing](https://example.com/a1) | — | ⬜ |
    | [A.2 Other thing](https://example.com/a2) | — | ⬜ |

Typical after:

    ## Items

    ### A. First group
    - [x] Mon · [A.1 Do the thing](https://example.com/a1) ✅ 2026-01-05 #plan-wk1
    - [ ] [A.2 Other thing](https://example.com/a2)

Items are matched between the two sections by a STABLE ID (default `A.1`, `BB.12`),
never by title text — titles drift, IDs do not.

An item scheduled in several cycles keeps ONE checkbox PER SCHEDULED OCCURRENCE, each
with its own tag and completion date: those are distinct events and collapsing them
would destroy history. Only the unscheduled catalog row is absorbed.

Fenced code blocks are never parsed or rewritten — a `_Template.md` whose fenced
example contains its own `## Items` table keeps that example intact, and the real
catalog below it is the one converted.

Nothing is deleted on a miss: a scheduled line whose ID has no catalog row is parked
under a visible bucket, a line that does not parse at all is left under its original
heading (which is then kept, not deleted), and a catalog row matching neither pattern
is reported with its line number.

Usage:
  python3 table_to_tasks.py --file "Modules/M01.md" --file "Modules/M02.md" \
      --items-heading "## Items" --merge-heading "## 📅 Scheduled Practice" \
      --backup-dir /tmp/backup --dry-run
"""
import argparse
import datetime
import pathlib
import re
import shutil
import sys

DEFAULT_ID = r"[A-Z]+\.\d+"
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
CHECKBOX = re.compile(r"^\s*- \[[ xX]\]")
SEP_ROW = re.compile(r"^\|[\s:|-]+\|?\s*$")


def fence_mask(lines):
    """True for every line inside a fenced block, including its delimiters."""
    mask, fence = [], None
    for line in lines:
        m = FENCE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                mask.append(True)
            else:
                mask.append(False)
            continue
        mask.append(True)
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
            fence = None
    return mask


def all_section_bounds(lines, title, mask=None):
    """[(start, end)] for EVERY '## Heading' section with this title, fences ignored.

    A note can carry the scheduled section more than once (one per cycle); harvesting
    only the first would leave the rest as live duplicates.
    """
    if mask is None:
        mask = fence_mask(lines)
    out = []
    for i, line in enumerate(lines):
        if mask[i] or line.strip() != title.strip():
            continue
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if not mask[j] and lines[j].startswith("## "):
                end = j
                break
        out.append((i, end))
    return out


def section_bounds(lines, title, mask=None):
    """(start, end) line indices of the first '## Heading' section, or None."""
    found = all_section_bounds(lines, title, mask)
    return found[0] if found else None


def is_filler_row(stripped, nxt):
    """True for a table header / separator / all-empty row - nothing to preserve."""
    if SEP_ROW.match(stripped):
        return True
    if nxt is not None and SEP_ROW.match(nxt.strip()):
        return True  # header row, the separator is right below it
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    return all(c in ("", "-", "—", "–", "⬜") for c in cells)


def build_res(id_pat):
    # the user pattern is always wrapped in its own group; extra groups inside it
    # would break .groups() unpacking, so reject them up front (see main()).
    return {
        # table row that is a bold group header: | **A. First group** | — | |
        "group": re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|"),
        # table row holding a linked item: | [A.1 Title](url) | … |
        # optional ** so a bolded row stays an item instead of becoming a heading
        "item": re.compile(
            rf"^\|\s*(?:\*\*)?\[(?:\*\*)?({id_pat})\s+(.+?)(?:\*\*)?\]"
            rf"\((\S+?)\)(?:\*\*)?\s*\|"
        ),
        # checkbox in the merge section: - [x] Mon · A.1 [Title](url) <trailing>
        # the ID may sit before or inside the link, both are accepted
        "sched_out": re.compile(
            rf"^- \[([ xX])\]\s+(?:(.+?)\s+·\s+)?({id_pat})\s+\[(.+?)\]\((\S+?)\)(.*)$"
        ),
        "sched_in": re.compile(
            rf"^- \[([ xX])\]\s+(?:(.+?)\s+·\s+)?\[({id_pat})\s+(.+?)\]\((\S+?)\)(.*)$"
        ),
    }


def harvest(lines, merge_heading, res, mask):
    """Read EVERY merge section: (ID -> list of scheduled parts, leftovers, checkboxes).

    `leftovers` maps each section's (start, end) to the lines in it that could not be
    parsed as a scheduled item. Those lines are kept, not deleted: a checkbox the ID
    pattern does not match still carries a tag and a completion date, and dropping it
    loses history that no later check can recover.
    """
    found, leftovers, n_boxes = {}, {}, 0
    if not merge_heading:
        return found, leftovers, n_boxes
    for start, end in all_section_bounds(lines, merge_heading, mask):
        rest_lines = []
        for i in range(start + 1, end):
            line = lines[i]
            if mask[i]:
                rest_lines.append(line)  # fenced example: keep it where it is
                continue
            s = line.strip()
            if CHECKBOX.match(s):
                n_boxes += 1
            m = res["sched_out"].match(s) or res["sched_in"].match(s)
            if m:
                box, prefix, item_id, title, url, rest = m.groups()
                found.setdefault(item_id, []).append({
                    "done": box.lower() == "x",
                    "prefix": (prefix or "").strip(),
                    "title": title,
                    "url": url,
                    "rest": rest.rstrip(),
                })
            elif s:
                rest_lines.append(line)
        while rest_lines and not rest_lines[-1].strip():
            rest_lines.pop()
        leftovers[(start, end)] = rest_lines
    return found, leftovers, n_boxes


def render(item_id, title, url, sched=None):
    if not sched:
        return f"- [ ] [{item_id} {title}]({url})"
    box = "x" if sched["done"] else " "
    prefix = f"{sched['prefix']} · " if sched["prefix"] else ""
    rest = sched["rest"]
    if rest and not rest.startswith(" "):
        rest = " " + rest
    return f"- [{box}] {prefix}[{item_id} {title}]({url}){rest}"


def convert(path, args, res):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    mask = fence_mask(lines)

    sched, leftovers, n_sched_boxes = harvest(lines, args.merge_heading, res, mask)

    bounds = section_bounds(lines, args.items_heading, mask)
    if not bounds:
        print(f"  SKIP (no '{args.items_heading}'): {path}")
        return None

    hashes = "#" * args.group_level
    out, used_ids, n_items, n_used_lines, dropped = [], set(), 0, 0, []

    for i in range(bounds[0] + 1, bounds[1]):
        line = lines[i]
        if mask[i]:
            out.append(line)  # fenced block: verbatim, blanks included
            continue
        # item test runs FIRST: a bolded link row is an item, not a group header
        im = res["item"].match(line)
        gm = None if im else res["group"].match(line)
        s = line.strip()
        if gm:
            out.append("")
            out.append(f"{hashes} {gm.group(1)}")
        elif im:
            item_id, title, url = im.groups()
            n_items += 1
            entries = sched.get(item_id)
            if entries:
                used_ids.add(item_id)
                n_used_lines += len(entries)
                for e in entries:
                    out.append(render(item_id, title, url, e))
            else:
                out.append(render(item_id, title, url))
        elif s.startswith("|"):
            nxt = lines[i + 1] if i + 1 < bounds[1] else None
            if not is_filler_row(s, nxt):
                dropped.append(i)  # a real row neither pattern matched
            continue  # header row, separator row, empty template row
        else:
            out.append(line)  # prose and blank lines inside the section survive

    orphans = [i for i in sched if i not in used_ids]
    if orphans:
        out.append("")
        out.append(f"{hashes} Scheduled — not found in catalog")
        for item_id in orphans:
            for e in sched[item_id]:
                out.append(render(item_id, e["title"], e["url"], e))

    new_section = [args.items_heading]
    if args.callout:
        callout = pathlib.Path(args.callout)
        if not callout.exists():
            print(f"  --callout file not found: {callout}", file=sys.stderr)
            print("  write it first (see SKILL.md Step 2) or drop the flag", file=sys.stderr)
            return False
        new_section += ["", callout.read_text(encoding="utf-8").rstrip("\n"), ""]
    new_section += out + [""]

    # rebuild in one pass: the items section becomes the tracker, each merge section
    # collapses to whatever could not be parsed out of it (usually nothing).
    regions = [(bounds[0], bounds[1], new_section)]
    n_kept = 0
    for (start, end), rest_lines in sorted(leftovers.items()):
        if rest_lines:
            regions.append((start, end, [lines[start], ""] + rest_lines + [""]))
            n_kept += len(rest_lines)
        else:
            regions.append((start, end, []))
    regions.sort()
    for (s1, e1, _), (s2, _, _) in zip(regions, regions[1:]):
        if s2 < e1:
            print(f"  overlapping sections in {path.name}: "
                  f"'{args.items_heading}' and '{args.merge_heading}' collide, skipped",
                  file=sys.stderr)
            return False

    rebuilt, prev = [], 0
    for s, e, replacement in regions:
        rebuilt += lines[prev:s] + replacement
        prev = e
    rebuilt += lines[prev:]

    text = collapse_blank_runs(rebuilt)
    if not args.no_stamp:
        text = stamp_frontmatter(text)

    flags = ""
    if orphans:
        flags += "  ORPHANS " + ",".join(orphans)
    if n_kept:
        flags += f"  {n_kept} unparsed line(s) LEFT IN PLACE"
    if dropped:
        flags += f"  {len(dropped)} table row(s) DROPPED"
    print(f"  {path.name}: {n_items} items, "
          f"{n_used_lines}/{n_sched_boxes} scheduled line(s) merged{flags}")
    for i in dropped:
        print(f"    dropped {path.name}:{i + 1}: {lines[i].strip()[:110]}", file=sys.stderr)
    if n_kept:
        print(f"    {path.name}: {n_kept} line(s) under '{args.merge_heading}' did not "
              "parse as scheduled items and were left there rather than deleted - "
              "check --id-pattern, then merge or remove them by hand", file=sys.stderr)

    if args.dry_run:
        return True
    if args.backup_dir:
        bdir = pathlib.Path(args.backup_dir)
        bdir.mkdir(parents=True, exist_ok=True)
        dest = bdir / path.name
        if dest.exists():
            print(f"  backup name collision, refusing to overwrite {dest}", file=sys.stderr)
            return False
        shutil.copy2(path, dest)
    path.write_text(text, encoding="utf-8")
    return True


def collapse_blank_runs(lines):
    """Collapse 3+ blank lines to one blank — outside fenced blocks only."""
    mask = fence_mask(lines)
    out, blanks = [], 0
    for i, line in enumerate(lines):
        if mask[i]:
            blanks = 0
            out.append(line)
            continue
        if line.strip() == "":
            blanks += 1
            if blanks > 1:
                continue
        else:
            blanks = 0
        out.append(line)
    return "\n".join(out)


def stamp_frontmatter(text):
    """Bump `updated:` inside the leading --- block only; no-op if absent."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    head, tail = text[:end], text[end:]
    stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    return re.sub(r"^updated: .*$", f"updated: {stamp}", head, count=1, flags=re.M) + tail


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", action="append", required=True,
                    help="markdown file to convert (repeatable)")
    ap.add_argument("--items-heading", default="## Items",
                    help="heading of the catalog section to rewrite")
    ap.add_argument("--merge-heading", default=None,
                    help="heading of a duplicate scheduled-items section to fold in and delete")
    ap.add_argument("--id-pattern", default=DEFAULT_ID,
                    help=rf"regex for the stable item ID, no capture groups (default: {DEFAULT_ID})")
    ap.add_argument("--group-level", type=int, default=3,
                    help="heading level for group rows (default 3 => ###)")
    ap.add_argument("--callout", default=None,
                    help="path to a file whose contents are inserted under the heading")
    ap.add_argument("--backup-dir", default=None, help="copy each file here before writing")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    ap.add_argument("--no-stamp", action="store_true", help="do not touch frontmatter updated:")
    args = ap.parse_args()

    try:
        if re.compile(args.id_pattern).groups:
            print("--id-pattern must not contain capture groups; use (?:…) instead",
                  file=sys.stderr)
            return 2
    except re.error as exc:
        print(f"--id-pattern is not a valid regex: {exc}", file=sys.stderr)
        return 2

    if args.merge_heading and args.merge_heading.strip() == args.items_heading.strip():
        print("--merge-heading must differ from --items-heading: merging a section into "
              "itself deletes it", file=sys.stderr)
        return 2

    res = build_res(args.id_pattern)
    touched, failed = 0, 0
    for f in args.file:
        p = pathlib.Path(f)
        if not p.is_file():
            print(f"  not a file: {p}", file=sys.stderr)
            failed += 1
            continue
        try:
            result = convert(p, args, res)
        except UnicodeDecodeError:
            print(f"  not UTF-8 text, skipped: {p}", file=sys.stderr)
            failed += 1
            continue
        if result:
            touched += 1
        elif result is False:
            failed += 1
    print(f"{'would convert' if args.dry_run else 'converted'} {touched} file(s)")
    if failed:
        print(f"{failed} file(s) failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
