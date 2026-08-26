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


def section_bounds(lines, title, mask=None):
    """(start, end) line indices of a '## Heading' section, ignoring fenced text."""
    if mask is None:
        mask = fence_mask(lines)
    start = None
    for i, line in enumerate(lines):
        if not mask[i] and line.strip() == title.strip():
            start = i
            break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if not mask[j] and lines[j].startswith("## "):
            return (start, j)
    return (start, len(lines))


def build_res(id_pat):
    # the user pattern is always wrapped in its own group; extra groups inside it
    # would break .groups() unpacking, so reject them up front (see main()).
    return {
        # table row that is a bold group header: | **A. First group** | — | |
        "group": re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|"),
        # table row holding a linked item: | [A.1 Title](url) | … |
        "item": re.compile(rf"^\|\s*\[({id_pat})\s+(.+?)\]\((\S+?)\)\s*\|"),
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
    """Map stable ID -> LIST of scheduled-line parts, from the merge section."""
    found = {}
    if not merge_heading:
        return found
    bounds = section_bounds(lines, merge_heading, mask)
    if not bounds:
        return found
    for i in range(bounds[0], bounds[1]):
        if mask[i]:
            continue  # fenced example, not a real scheduled line
        s = lines[i].strip()
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
    return found


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

    sched = harvest(lines, args.merge_heading, res, mask)
    n_sched_lines = sum(len(v) for v in sched.values())

    bounds = section_bounds(lines, args.items_heading, mask)
    if not bounds:
        print(f"  SKIP (no '{args.items_heading}'): {path}")
        return False

    hashes = "#" * args.group_level
    out, used_ids, n_items, n_used_lines = [], set(), 0, 0

    for i in range(bounds[0] + 1, bounds[1]):
        line = lines[i]
        if mask[i]:
            out.append(line)  # fenced block: verbatim, blanks included
            continue
        # item test runs FIRST: a bolded link row is an item, not a group header
        im = res["item"].match(line)
        gm = None if im else res["group"].match(line)
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
        elif line.strip().startswith("|"):
            continue  # header row, separator row, empty template row
        elif line.strip() == "":
            continue
        else:
            out.append(line)  # prose inside the section survives

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
        new_section += ["", callout.read_text(encoding="utf-8").rstrip("\n")]
    new_section += out + [""]

    lines = lines[:bounds[0]] + new_section + lines[bounds[1]:]

    if args.merge_heading:
        mb = section_bounds(lines, args.merge_heading)
        if mb:
            lines = lines[:mb[0]] + lines[mb[1]:]

    text = collapse_blank_runs(lines)
    if not args.no_stamp:
        text = stamp_frontmatter(text)

    flag = "  ORPHANS " + ",".join(orphans) if orphans else ""
    print(f"  {path.name}: {n_items} items, "
          f"{n_used_lines}/{n_sched_lines} scheduled line(s) merged{flag}")

    if args.dry_run:
        return True
    if args.backup_dir:
        bdir = pathlib.Path(args.backup_dir)
        bdir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, bdir / path.name)
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

    res = build_res(args.id_pattern)
    touched = 0
    for f in args.file:
        p = pathlib.Path(f)
        if not p.is_file():
            print(f"  not a file: {p}", file=sys.stderr)
            continue
        try:
            touched += bool(convert(p, args, res))
        except UnicodeDecodeError:
            print(f"  not UTF-8 text, skipped: {p}", file=sys.stderr)
    print(f"{'would convert' if args.dry_run else 'converted'} {touched} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
