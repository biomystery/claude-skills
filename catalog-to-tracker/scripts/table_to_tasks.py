#!/usr/bin/env python3
"""Convert a markdown catalog table into a grouped checkbox tracker, merging in an
optional duplicate "scheduled items" section so every item ends up with ONE checkbox.

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


def section_bounds(lines, title):
    """Return (start, end) line indices of a '## Heading' section, or None."""
    start = None
    for i, line in enumerate(lines):
        if line.strip() == title.strip():
            start = i
            break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            return (start, j)
    return (start, len(lines))


def build_res(id_pat):
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


def harvest(lines, merge_heading, res):
    """Map stable ID -> scheduled-line parts, from the merge section."""
    found = {}
    if not merge_heading:
        return found
    bounds = section_bounds(lines, merge_heading)
    if not bounds:
        return found
    for line in lines[bounds[0]:bounds[1]]:
        s = line.strip()
        m = res["sched_out"].match(s) or res["sched_in"].match(s)
        if m:
            box, prefix, item_id, title, url, rest = m.groups()
            found[item_id] = {
                "done": box.lower() == "x",
                "prefix": (prefix or "").strip(),
                "title": title,
                "url": url,
                "rest": rest.rstrip(),
            }
    return found


def render(item_id, title, url, sched, group_level):
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

    sched = harvest(lines, args.merge_heading, res)

    bounds = section_bounds(lines, args.items_heading)
    if not bounds:
        print(f"  SKIP (no '{args.items_heading}'): {path}")
        return False

    hashes = "#" * args.group_level
    body = lines[bounds[0] + 1:bounds[1]]
    out, used, n_items = [], set(), 0

    for line in body:
        gm = res["group"].match(line)
        im = res["item"].match(line)
        if gm:
            out.append("")
            out.append(f"{hashes} {gm.group(1)}")
        elif im:
            item_id, title, url = im.groups()
            n_items += 1
            s = sched.get(item_id)
            if s:
                used.add(item_id)
            out.append(render(item_id, title, url, s, args.group_level))
        elif line.strip().startswith("|"):
            continue  # header row, separator row, empty template row
        elif line.strip() == "":
            continue
        else:
            out.append(line)  # prose inside the section survives

    orphans = [i for i in sched if i not in used]
    if orphans:
        out.append("")
        out.append(f"{hashes} Scheduled — not found in catalog")
        for item_id in orphans:
            s = sched[item_id]
            out.append(render(item_id, s["title"], s["url"], s, args.group_level))

    new_section = [args.items_heading]
    if args.callout:
        new_section += ["", pathlib.Path(args.callout).read_text(encoding="utf-8").rstrip("\n")]
    new_section += out + [""]

    lines = lines[:bounds[0]] + new_section + lines[bounds[1]:]

    if args.merge_heading:
        mb = section_bounds(lines, args.merge_heading)
        if mb:
            lines = lines[:mb[0]] + lines[mb[1]:]

    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    if not args.no_stamp:
        stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        text = re.sub(r"^updated: .*$", f"updated: {stamp}", text, count=1, flags=re.M)

    flag = "  ORPHANS " + ",".join(orphans) if orphans else ""
    print(f"  {path.name}: {n_items} items, {len(used)}/{len(sched)} merged{flag}")

    if args.dry_run:
        return True
    if args.backup_dir:
        bdir = pathlib.Path(args.backup_dir)
        bdir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, bdir / path.name)
    path.write_text(text, encoding="utf-8")
    return True


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
                    help=rf"regex for the stable item ID (default: {DEFAULT_ID})")
    ap.add_argument("--group-level", type=int, default=3,
                    help="heading level for group rows (default 3 => ###)")
    ap.add_argument("--callout", default=None,
                    help="path to a file whose contents are inserted under the heading")
    ap.add_argument("--backup-dir", default=None, help="copy each file here before writing")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    ap.add_argument("--no-stamp", action="store_true", help="do not touch frontmatter updated:")
    args = ap.parse_args()

    res = build_res(args.id_pattern)
    touched = 0
    for f in args.file:
        p = pathlib.Path(f)
        if not p.exists():
            print(f"  MISSING: {p}", file=sys.stderr)
            continue
        touched += bool(convert(p, args, res))
    print(f"{'would convert' if args.dry_run else 'converted'} {touched} file(s)")


if __name__ == "__main__":
    main()
