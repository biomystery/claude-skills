#!/usr/bin/env python3
"""Locate the current-week and previous-week weekly note + daily notes for
an Obsidian vault using the Journals/YYYY/YYYY-WNN.md + YYYY/YYYY-WNN/
layout.

Does NOT compute the week label from a naive date.strftime("%V") on the
target day. Some vaults run weekly notes Sunday-Saturday but number them by
the ISO week of the Monday inside that range -- so a Sunday's own ISO week
number is off by one from the folder it actually lives in. Instead this
script reads every existing weekly note's frontmatter (journal-start-date /
journal-end-date) and picks by actual date range, which is authoritative
regardless of numbering scheme.

Usage:
    find_week_files.py --vault PATH [--date YYYY-MM-DD]

Prints JSON:
{
  "today": "...",
  "current_week": {"label", "weekly_file", "daily_dir", "start", "end", "daily_files": [...]},
  "past_week":    {same shape, for the weekly note immediately before current_week} | null
}
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.S)


def parse_frontmatter_dates(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, None
    fm = m.group(1)
    start = re.search(r"journal-start-date:\s*(\S+)", fm)
    end = re.search(r"journal-end-date:\s*(\S+)", fm)
    if not (start and end):
        return None, None
    try:
        return (
            datetime.strptime(start.group(1), "%Y-%m-%d").date(),
            datetime.strptime(end.group(1), "%Y-%m-%d").date(),
        )
    except ValueError:
        return None, None


def find_weekly_notes(vault):
    pattern = os.path.join(vault, "Journals", "*", "*-W[0-9][0-9].md")
    out = []
    for path in glob.glob(pattern):
        start, end = parse_frontmatter_dates(path)
        if start and end:
            out.append((start, end, path))
    out.sort(key=lambda t: t[0])
    return out


def daily_files_for(path, start, end):
    daily_dir = path[:-3]  # strip .md -> matching folder of the same name
    if not os.path.isdir(daily_dir):
        return daily_dir, []
    files = []
    d = start
    while d <= end:
        candidate = os.path.join(daily_dir, f"{d.isoformat()}.md")
        if os.path.isfile(candidate):
            files.append(candidate)
        d += timedelta(days=1)
    return daily_dir, files


def week_info(start, end, path):
    daily_dir, files = daily_files_for(path, start, end)
    return {
        "label": os.path.basename(path)[:-3],
        "weekly_file": path,
        "daily_dir": daily_dir,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "daily_files": files,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--date", default=None, help="Target date, default today (YYYY-MM-DD)")
    args = ap.parse_args()

    today = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()

    weeks = find_weekly_notes(args.vault)
    if not weeks:
        print("no weekly notes found under Journals/*/*-W##.md", file=sys.stderr)
        return 1

    current = next((w for w in weeks if w[0] <= today <= w[1]), None)
    if current is None:
        print(f"no weekly note covers {today.isoformat()}", file=sys.stderr)
        return 1

    idx = weeks.index(current)
    past = weeks[idx - 1] if idx > 0 else None

    result = {
        "today": today.isoformat(),
        "current_week": week_info(*current),
        "past_week": week_info(*past) if past else None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
