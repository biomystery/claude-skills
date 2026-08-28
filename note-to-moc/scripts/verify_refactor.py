#!/usr/bin/env python3
"""Verify a MOC refactor lost no content and broke no links.

Usage:
  verify_refactor.py --original BACKUP.md [--original BACKUP2.md ...] \
                     --new-dir PROJECT_DIR --vault VAULT_ROOT

Two independent checks:

  CONTENT  every substantive line of each original must appear somewhere in the
           new file set. Lines that were deliberately REWRITTEN will show up
           here - that is expected. Read each one and confirm it was rewritten
           on purpose rather than dropped.

  LINKS    every [[wikilink]] in the new files resolves to a real note, and every
           [[note#heading]] anchor resolves to a real heading.

Exit code 1 if any link is broken. Content misses are reported, never fatal,
because rewriting is legitimate and only a human can tell rewrite from loss.
"""
import argparse
import os
import re
import sys

SKIP_DIRS = {".obsidian", ".git", ".trash", ".smart-env", "node_modules", ".backup"}
LINK_RE = re.compile(r"\[\[([^\]|#]*)(#[^\]|]*)?(\\?\|[^\]]*)?\]\]")


def walk_md(root):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(cur, fn)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", action="append", required=True)
    ap.add_argument("--new-dir", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--min-len", type=int, default=25,
                    help="ignore lines shorter than this (default 25)")
    args = ap.parse_args()

    new_files = sorted(walk_md(args.new_dir))
    blob = ""
    for f in new_files:
        blob += open(f, encoding="utf-8", errors="ignore").read() + "\n"

    # ---------- CONTENT ----------
    print(f"CONTENT - checking {len(args.original)} original(s) against "
          f"{len(new_files)} new file(s)\n")
    total_missing = 0
    for orig in args.original:
        missing, in_fm = [], False
        for i, line in enumerate(open(orig, encoding="utf-8", errors="ignore"), 1):
            s = line.strip()
            if i == 1 and s == "---":
                in_fm = True
                continue
            if in_fm:
                if s == "---":
                    in_fm = False
                continue
            if len(s) < args.min_len or s.startswith("#") or s == "---":
                continue
            if s not in blob:
                missing.append((i, s))
        total_missing += len(missing)
        print(f"  {os.path.basename(orig)}: {len(missing)} line(s) not found verbatim")
        for i, s in missing:
            print(f"     L{i}: {s[:100]}")
    if total_missing:
        print("\n  ^ Review each. Rewritten intentionally = fine. Silently dropped = bug.")

    # ---------- LINKS ----------
    # Guard: --vault must be the VAULT ROOT, not the project subfolder. Getting this
    # wrong makes every vault-relative link look broken, which is a very convincing
    # false alarm. An Obsidian vault root contains a .obsidian directory.
    if not os.path.isdir(os.path.join(args.vault, ".obsidian")):
        print(f"\n  WARNING: no .obsidian/ found in --vault ({args.vault}).")
        print("  If that is not your vault ROOT, every vault-relative [[full/path/link]]")
        print("  below will be reported broken even though Obsidian resolves it fine.")

    paths, names = set(), {}
    for f in walk_md(args.vault):
        rel = os.path.relpath(f, args.vault)[:-3]
        paths.add(rel)
        names.setdefault(os.path.basename(rel), []).append(rel)

    broken, bad_anchor, n = [], [], 0
    for f in new_files:
        text = open(f, encoding="utf-8", errors="ignore").read()
        for m in LINK_RE.finditer(text):
            target = (m.group(1) or "").strip().rstrip("\\")
            anchor = (m.group(2) or "")[1:].strip().rstrip("\\")
            if not target:
                continue
            n += 1
            rel = None
            if target in paths:
                rel = target
            elif target in names and len(names[target]) == 1:
                rel = names[target][0]
            if rel is None:
                broken.append((os.path.basename(f), target))
                continue
            if anchor:
                full = os.path.join(args.vault, rel + ".md")
                heads = {re.sub(r"^#+\s*", "", l).strip()
                         for l in open(full, encoding="utf-8", errors="ignore")
                         if l.startswith("#")}
                if anchor not in heads:
                    bad_anchor.append((os.path.basename(f), target, anchor))

    print(f"\nLINKS - {n} wikilink(s) checked")
    print(f"  broken links : {len(broken)}")
    for f, t in broken:
        print(f"     {f} -> [[{t}]]")
    print(f"  bad anchors  : {len(bad_anchor)}")
    for f, t, a in bad_anchor:
        print(f"     {f} -> [[{t}#{a}]]")

    ok = not broken and not bad_anchor
    print("\nRESULT:", "links OK" if ok else "LINK ERRORS - fix before continuing")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
