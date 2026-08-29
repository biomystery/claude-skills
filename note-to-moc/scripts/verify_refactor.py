#!/usr/bin/env python3
"""Verify a MOC refactor lost no content, broke no links, and stranded no note.

Usage:
  verify_refactor.py --original BACKUP.md [--original BACKUP2.md ...] \
                     --new-dir PROJECT_DIR --vault VAULT_ROOT [--hub HUB.md]

Four checks:

  CONTENT  every substantive line of each original must appear somewhere in the
           new file set. Lines REWRITTEN on purpose show up here - that is
           expected. Read each one and confirm it was rewritten, not dropped.

  LINKS    every [[wikilink]] in the new files resolves to a real note, and every
           [[note#heading]] anchor to a real heading. Duplicate basenames are
           reported as AMBIGUOUS: Obsidian still resolves them by proximity, but
           a refactor that introduces one is how [[Background]] in the hub and
           [[Background]] in a spoke quietly become different notes.

  INBOUND  links from the REST OF THE VAULT into the refactored notes still
           resolve. This is the risk the whole skill is built around - `mv`
           breaks every inbound link and nothing warns you - and it is invisible
           if you only check links in the files you just wrote.

  REACH    with --hub, every note under --new-dir is reachable by following links
           from the hub, and (as a warning) is listed in the hub's own map.

--new-dir is walked recursively, so one run covers the whole tree however deep it
nests. The ROOT original stays the single source of truth for content loss: pass
the top-level backup, not the per-level ones.

Design note: this script's failure mode must be a false ALARM, never a false
pass. Every check that cannot run - a bad --hub, an empty backup, no files -
is a hard error, not a skip, because a check that silently no-ops while printing
"RESULT: links OK" is worse than no check at all.
"""
import argparse
import os
import re
import sys

SKIP_DIRS = {".obsidian", ".git", ".trash", ".smart-env", "node_modules", ".backup"}
LINK_RE = re.compile(r"\[\[([^\]|#]*)((?:#[^\]|]*)?)(\\?\|[^\]]*)?\]\]")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEAD_RE = re.compile(r"^(#{1,6})\s+(\S.*)$")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
COMMENT_RE = re.compile(r"%%.*?%%", re.S)


def walk_md(root):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(cur, fn)


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def mask_noncontent(text):
    """Blank fenced blocks, inline code spans and %%comments%%.

    A [[link]] inside a code fence or backticks is documentation, not a link:
    Obsidian does not resolve it and it creates no backlink. Counting it as a
    reachability edge lets a genuinely stranded note look reachable. An
    unterminated fence masks nothing, so a stray ``` cannot blank the rest of
    the file and hide every real link after it.
    """
    lines = text.split("\n")
    opens, in_fence, marker = [], False, ""
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
    for start, end in opens:
        if end is not None:
            for i in range(start, end + 1):
                lines[i] = ""
    out = "\n".join(lines)
    out = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), out)
    return INLINE_CODE_RE.sub("", out)


def norm_heading(text):
    """Normalise a heading for anchor comparison.

    Obsidian resolves anchors case-insensitively and ignores inline markup, so
    `## **Status** update` is reachable as `#status update`.
    """
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"\[\[([^\]|]*)(?:\|[^\]]*)?\]\]", r"\1", text)
    text = re.sub(r"[*_`~]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


_HEAD_CACHE = {}


def headings_of(path):
    """Headings in a file, excluding fenced code and bare `#tag` lines."""
    if path in _HEAD_CACHE:
        return _HEAD_CACHE[path]
    out = set()
    for line in mask_noncontent(read(path)).split("\n"):
        m = HEAD_RE.match(line)          # requires whitespace: #tag is not a heading
        if m:
            out.add(norm_heading(m.group(2)))
    _HEAD_CACHE[path] = out
    return out


def resolve(target, src_rel, paths, names):
    """Resolve a wikilink target the way Obsidian does.

    Exact vault-relative path, then relative to the linking file's own folder,
    then - only for a bare name with no slash - basename with the nearest match
    winning. A path-qualified target that matches nothing is BROKEN: falling back
    to basename there made [[../Alpha]] resolve to the note the `../` was written
    to escape, and let a stale [[old/path/Note]] pass as healthy.

    Returns (rel_path_or_None, all_basename_candidates). The candidate list is
    always computed, even when an earlier step already won, so a duplicate
    basename is reported no matter how the link happened to be spelled.
    """
    target = target[:-3] if target.lower().endswith(".md") else target
    target = target.lstrip("/")
    cands = names.get(os.path.basename(target).lower(), [])
    dupes = sorted(cands) if len(cands) > 1 else []

    if target in paths:
        return target, dupes
    near = os.path.normpath(os.path.join(os.path.dirname(src_rel), target))
    if near in paths:
        return near, dupes
    lower = {p.lower(): p for p in paths}         # Obsidian is case-insensitive
    for cand in (target.lower(), near.lower()):
        if cand in lower:
            return lower[cand], dupes
    if "/" in target or os.sep in target:
        return None, dupes
    if not cands:
        return None, dupes
    if len(cands) == 1:
        return cands[0], dupes
    src_dir = os.path.dirname(src_rel).split(os.sep)

    def distance(c):                              # Obsidian breaks ties by proximity
        d = os.path.dirname(c).split(os.sep)
        return (-len(os.path.commonprefix([src_dir, d])), len(d), c)

    return min(cands, key=distance), dupes


def check_anchor(anchor, rel, vault):
    """True if every segment of a (possibly nested) #A#B anchor is a heading."""
    parts = [p for p in anchor.split("#") if p.strip()]
    heads = headings_of(os.path.join(vault, rel + ".md"))
    return all(norm_heading(p) in heads for p in parts)


def links_in(text, src_rel, paths, names):
    """Yield (target, anchor) for every real wikilink in `text`."""
    for m in LINK_RE.finditer(mask_noncontent(text)):
        target = (m.group(1) or "").strip().rstrip("\\")
        anchor = (m.group(2) or "").lstrip("#").strip().rstrip("\\")
        if anchor.startswith("^"):        # block reference, not a heading
            anchor = ""
        yield target, anchor


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", action="append", required=True)
    ap.add_argument("--new-dir", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--hub", help="hub note; enables the reachability check")
    ap.add_argument("--min-len", type=int, default=10,
                    help="ignore lines shorter than this (default 10)")
    args = ap.parse_args()

    if not os.path.isdir(args.new_dir):
        print(f"--new-dir is not a directory: {args.new_dir}", file=sys.stderr)
        return 1
    new_files = sorted(walk_md(args.new_dir))
    if not new_files:
        print(f"no .md files under --new-dir ({args.new_dir})", file=sys.stderr)
        return 1
    blob = "".join(read(f) + "\n" for f in new_files)

    # ---------- CONTENT ----------
    print(f"CONTENT - checking {len(args.original)} original(s) against "
          f"{len(new_files)} new file(s)")
    print(f"  (lines shorter than {args.min_len} chars are not compared; "
          "headings are compared separately)\n")
    fatal, total_missing = False, 0
    for orig in args.original:
        if not os.path.isfile(orig):
            print(f"  MISSING BACKUP: {orig} - cannot check content loss")
            return 1
        lines = read(orig).split("\n")
        body = lines
        if lines and lines[0].strip() == "---":       # strip frontmatter, but only
            for j in range(1, len(lines)):            # if it is actually closed
                if lines[j].strip() == "---":
                    body = lines[j + 1:]
                    break
        compared = missing = 0
        head_missing, prose_missing = [], []
        for i, line in enumerate(body, len(lines) - len(body) + 1):
            s = line.strip()
            if s == "---" or len(s) < args.min_len:
                continue
            m = HEAD_RE.match(s)
            compared += 1
            if m:
                if norm_heading(m.group(2)) not in {
                        norm_heading(h.group(2))
                        for h in (HEAD_RE.match(x.strip()) for x in blob.split("\n"))
                        if h}:
                    head_missing.append((i, s))
                    missing += 1
            elif s not in blob:
                prose_missing.append((i, s))
                missing += 1
        name = os.path.basename(orig)
        print(f"  {name}: {compared} line(s) compared, {missing} not found")
        if compared == 0:
            print(f"     ERROR: nothing was compared - {name} is empty, truncated, "
                  "or entirely below --min-len. This check proved nothing.")
            fatal = True
        for i, s in head_missing:
            print(f"     heading L{i}: {s[:100]}")
        for i, s in prose_missing:
            print(f"     L{i}: {s[:100]}")
        total_missing += missing
        if missing:
            print("     ^ Review each. Rewritten intentionally = fine. "
                  "Silently dropped = bug.")

    # ---------- index the vault ----------
    if not os.path.isdir(os.path.join(args.vault, ".obsidian")):
        print(f"\n  WARNING: no .obsidian/ found in --vault ({args.vault}).")
        print("  If that is not your vault ROOT, every vault-relative [[full/path/link]]")
        print("  below will be reported broken even though Obsidian resolves it fine.")

    paths, names = set(), {}
    for f in walk_md(args.vault):
        rel = os.path.relpath(f, args.vault)[:-3]
        paths.add(rel)
        names.setdefault(os.path.basename(rel).lower(), []).append(rel)

    new_rel = {os.path.relpath(f, args.vault)[:-3] for f in new_files}

    # ---------- LINKS ----------
    broken, ambiguous, bad_anchor, n = [], set(), [], 0
    edges = {r: set() for r in new_rel}
    for f in new_files:
        rel_self = os.path.relpath(f, args.vault)[:-3]
        for target, anchor in links_in(read(f), rel_self, paths, names):
            n += 1
            if target:
                rel, dupes = resolve(target, rel_self, paths, names)
                if dupes:
                    ambiguous.add((os.path.basename(f), target, tuple(dupes)))
            else:
                rel = rel_self                # [[#Anchor]] points at this file
            if rel is None:
                broken.append((os.path.basename(f), target))
                continue
            edges[rel_self].add(rel)
            if anchor and not check_anchor(anchor, rel, args.vault):
                bad_anchor.append((os.path.basename(f), target or rel_self, anchor))

    print(f"\nLINKS - {n} wikilink(s) checked in the refactored notes")
    print(f"  broken links : {len(broken)}")
    for f, t in broken:
        print(f"     {f} -> [[{t}]]")
    print(f"  ambiguous    : {len(ambiguous)}  (warning - Obsidian picks the nearest)")
    for f, t, cands in sorted(ambiguous):
        print(f"     {f} -> [[{t}]] matches {len(cands)}: {', '.join(cands)}")
    print(f"  bad anchors  : {len(bad_anchor)}")
    for f, t, a in bad_anchor:
        print(f"     {f} -> [[{t}#{a}]]")

    # ---------- INBOUND ----------
    # Only links that AIM at the refactored area are reported, so a vault's
    # pre-existing broken links elsewhere do not drown out the signal.
    orig_names = {os.path.basename(o)[:-3].lower() for o in args.original}
    new_names = {os.path.basename(r).lower() for r in new_rel}
    watched = orig_names | new_names
    inbound_broken, inbound_anchor, m = [], [], 0
    for f in walk_md(args.vault):
        rel_self = os.path.relpath(f, args.vault)[:-3]
        if rel_self in new_rel:
            continue
        for target, anchor in links_in(read(f), rel_self, paths, names):
            base = os.path.basename(target)[:-3] if target.lower().endswith(".md") \
                else os.path.basename(target)
            if base.lower() not in watched:
                continue
            m += 1
            rel, _ = resolve(target, rel_self, paths, names)
            if rel is None:
                inbound_broken.append((rel_self, target))
            elif anchor and not check_anchor(anchor, rel, args.vault):
                inbound_anchor.append((rel_self, target, anchor))

    print(f"\nINBOUND - {m} link(s) from the rest of the vault into the refactored notes")
    print(f"  broken links : {len(inbound_broken)}")
    for f, t in inbound_broken:
        print(f"     {f}.md -> [[{t}]]")
    print(f"  bad anchors  : {len(inbound_anchor)}")
    for f, t, a in inbound_anchor:
        print(f"     {f}.md -> [[{t}#{a}]]  (heading gone - it moved to a spoke)")

    # ---------- REACH ----------
    unreachable, unmapped = [], []
    if args.hub:
        if not os.path.isfile(args.hub):
            print(f"\nREACH - ERROR: --hub is not a file: {args.hub}")
            return 1
        hub_rel = os.path.splitext(
            os.path.relpath(os.path.abspath(args.hub), os.path.abspath(args.vault)))[0]
        if hub_rel not in edges:
            print(f"\nREACH - ERROR: --hub ({args.hub}) is not one of the notes under "
                  f"--new-dir ({args.new_dir}). Refusing to skip the check.")
            return 1
        seen, stack = {hub_rel}, [hub_rel]
        while stack:
            for nxt in edges.get(stack.pop(), ()):
                if nxt in edges and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        unreachable = sorted(set(edges) - seen)
        # REACH is transitive, so a sub-hub linking its own children keeps them
        # reachable even when the root hub's map omits them. Step 6 requires the
        # map to list EVERY note in the tree, so check that separately.
        unmapped = sorted(set(edges) - edges[hub_rel] - {hub_rel})
        print(f"\nREACH - {len(edges)} note(s) under {args.new_dir}, "
              f"{len(seen)} reachable from the hub")
        print(f"  unreachable  : {len(unreachable)}")
        for r in unreachable:
            print(f"     {r}.md - nothing in the tree links to it")
        print(f"  not in map   : {len(unmapped)}  (warning - hub's map should list every note)")
        for r in unmapped:
            print(f"     {r}.md - reachable, but the hub does not link it directly")

    ok = not (fatal or broken or bad_anchor or unreachable
              or inbound_broken or inbound_anchor)
    note = f" ({total_missing} content line(s) still to review by eye)" \
        if total_missing and ok else ""
    print("\nRESULT:", ("structure OK" + note) if ok
          else "ERRORS - fix before continuing")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
