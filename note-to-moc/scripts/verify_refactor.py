#!/usr/bin/env python3
"""Verify a MOC refactor lost no content, broke no links, and stranded no note.

Usage:
  verify_refactor.py --original BACKUP.md [--original BACKUP2.md ...] \
                     --new-dir PROJECT_DIR --vault VAULT_ROOT [--hub HUB.md]

Three independent checks:

  CONTENT  every substantive line of each original must appear somewhere in the
           new file set. Lines that were deliberately REWRITTEN will show up
           here - that is expected. Read each one and confirm it was rewritten
           on purpose rather than dropped.

  LINKS    every [[wikilink]] in the new files resolves to a real note, and every
           [[note#heading]] anchor resolves to a real heading. Targets are resolved
           the way Obsidian resolves them: exact vault-relative path, then relative
           to the linking file's own folder, then by basename with the nearest
           match winning. A basename matching two notes is reported as AMBIGUOUS -
           a warning, not a failure, because Obsidian still picks one, but a
           refactor that introduces a duplicate basename is how [[Background]] in
           the hub and [[Background]] in a spoke quietly become different notes.

  REACH    with --hub, every note under --new-dir must be reachable by following
           links from the hub. A spoke whose bytes survive but that nothing links
           to is lost in practice. This is what catches a recursive refactor that
           promoted a spoke to a sub-hub without wiring its children in.

--new-dir is walked recursively, so one run covers the whole tree however deep it
nests. The ROOT original stays the single source of truth for content loss: pass
the top-level backup, not the per-level ones.

Exit code 1 if any link is broken, any anchor is bad, or any note is unreachable.
Content misses and ambiguity are reported, never fatal: rewriting is legitimate and
Obsidian does resolve ambiguity deterministically - only a human can tell an
intended rewrite from a silent drop.
"""
import argparse
import os
import re
import sys

SKIP_DIRS = {".obsidian", ".git", ".trash", ".smart-env", "node_modules", ".backup"}
LINK_RE = re.compile(r"\[\[([^\]|#]*)(#[^\]|]*)?(\\?\|[^\]]*)?\]\]")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")


def walk_md(root):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(cur, fn)


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def norm_heading(text):
    """Normalise a heading for anchor comparison.

    Obsidian resolves anchors case-insensitively and ignores inline markup, so
    `## **Status** update` is reachable as `#status update`.
    """
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"\[\[([^\]|]*)(?:\|[^\]]*)?\]\]", r"\1", text)
    text = re.sub(r"[*_`~]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def headings_of(path):
    """Headings in a file, excluding `#` lines inside fenced code blocks."""
    out, in_fence, marker = set(), False, ""
    for line in read(path).split("\n"):
        m = FENCE_RE.match(line)
        if m:
            if not in_fence:
                in_fence, marker = True, m.group(1)
            elif m.group(1) == marker:
                in_fence = False
            continue
        if not in_fence and line.startswith("#"):
            out.add(norm_heading(line))
    return out


def resolve(target, src_rel, paths, names):
    """Resolve a wikilink target the way Obsidian does.

    Order: exact vault-relative path, then relative to the linking file's own
    folder, then basename with the NEAREST match winning. Returns
    (rel_path_or_None, all_basename_candidates).
    """
    target = target[:-3] if target.endswith(".md") else target
    if target in paths:
        return target, []
    near = os.path.normpath(os.path.join(os.path.dirname(src_rel), target))
    if near in paths:
        return near, []
    cands = names.get(os.path.basename(target), [])
    if not cands:
        return None, []
    if len(cands) == 1:
        return cands[0], []
    # Obsidian breaks a basename tie by proximity to the linking file.
    src_dir = os.path.dirname(src_rel).split(os.sep)
    def distance(c):
        d = os.path.dirname(c).split(os.sep)
        shared = len(os.path.commonprefix([src_dir, d]))
        return (-shared, len(d), c)
    return min(cands, key=distance), sorted(cands)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", action="append", required=True)
    ap.add_argument("--new-dir", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--hub", help="hub note; enables the reachability check")
    ap.add_argument("--min-len", type=int, default=25,
                    help="ignore lines shorter than this (default 25)")
    args = ap.parse_args()

    new_files = sorted(walk_md(args.new_dir))
    if not new_files:
        print(f"no .md files under --new-dir ({args.new_dir}) - nothing to verify",
              file=sys.stderr)
        return 1
    blob = "".join(read(f) + "\n" for f in new_files)

    # ---------- CONTENT ----------
    print(f"CONTENT - checking {len(args.original)} original(s) against "
          f"{len(new_files)} new file(s)\n")
    total_missing = 0
    for orig in args.original:
        if not os.path.isfile(orig):
            print(f"  MISSING BACKUP: {orig} - cannot check content loss")
            return 1
        missing, in_fm = [], False
        for i, line in enumerate(read(orig).split("\n"), 1):
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

    broken, ambiguous, bad_anchor, n = [], set(), [], 0
    edges = {}
    for f in new_files:
        rel_self = os.path.relpath(f, args.vault)[:-3]
        edges.setdefault(rel_self, set())
        for m in LINK_RE.finditer(read(f)):
            target = (m.group(1) or "").strip().rstrip("\\")
            anchor = (m.group(2) or "")[1:].strip().rstrip("\\")
            n += 1
            if anchor.startswith("^"):        # block reference, not a heading
                anchor = ""
            if target:
                rel, cands = resolve(target, rel_self, paths, names)
                if cands:
                    ambiguous.add((os.path.basename(f), target, tuple(cands)))
            else:
                rel = rel_self                # [[#Anchor]] points at this file
            if rel is None:
                broken.append((os.path.basename(f), target))
                continue
            edges[rel_self].add(rel)
            if anchor and norm_heading(anchor) not in headings_of(
                    os.path.join(args.vault, rel + ".md")):
                bad_anchor.append((os.path.basename(f), target or rel_self, anchor))

    print(f"\nLINKS - {n} wikilink(s) checked")
    print(f"  broken links : {len(broken)}")
    for f, t in broken:
        print(f"     {f} -> [[{t}]]")
    print(f"  ambiguous    : {len(ambiguous)}  (warning - Obsidian picks the nearest)")
    for f, t, cands in sorted(ambiguous):
        print(f"     {f} -> [[{t}]] matches {len(cands)}: {', '.join(cands)}")
    print(f"  bad anchors  : {len(bad_anchor)}")
    for f, t, a in bad_anchor:
        print(f"     {f} -> [[{t}#{a}]]")

    # ---------- REACH ----------
    unreachable = []
    if args.hub:
        hub_rel = os.path.relpath(os.path.abspath(args.hub), args.vault)[:-3]
        if hub_rel not in edges:
            print(f"\nREACH - hub {args.hub} is not under --new-dir; skipping")
        else:
            seen, stack = {hub_rel}, [hub_rel]
            while stack:
                for nxt in edges.get(stack.pop(), ()):
                    if nxt in edges and nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            unreachable = sorted(set(edges) - seen)
            print(f"\nREACH - {len(edges)} note(s) under {args.new_dir}, "
                  f"{len(seen)} reachable from the hub")
            print(f"  unreachable  : {len(unreachable)}")
            for r in unreachable:
                print(f"     {r}.md - nothing in the tree links to it")

    ok = not (broken or bad_anchor or unreachable)
    print("\nRESULT:", "links OK" if ok else "STRUCTURE ERRORS - fix before continuing")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
