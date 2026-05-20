#!/usr/bin/env python3
"""
logseq_migrate.py  —  Migrate a Logseq vault → Obsidian vault

Usage:
    python3 logseq_migrate.py <logseq_root> <obsidian_root> [options]

Options:
    --apply   Write files (default is dry-run)
    --fixup   Re-clean already-migrated files in place
    --stamp   Backfill created/updated YAML from source file timestamps

Folder layout produced:
    <obsidian_root>/Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md
    <obsidian_root>/Logseq-Import/Pages/
    <obsidian_root>/Logseq-Import/Assets/
"""

import os
import re
import shutil
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

# ── CLI args ───────────────────────────────────────────────────
if len(sys.argv) < 3 and "--help" not in sys.argv:
    print(__doc__)
    sys.exit(1)

LOGSEQ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
VAULT  = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

PAGES_DEST  = VAULT / "Logseq-Import" / "Pages"
ASSETS_DEST = VAULT / "Logseq-Import" / "Assets"

DRY_RUN = "--apply" not in sys.argv and "--fixup" not in sys.argv and "--stamp" not in sys.argv
FIXUP   = "--fixup" in sys.argv
STAMP   = "--stamp" in sys.argv

EMPTY_THRESHOLD = 20   # bytes of meaningful content below which a file is skipped
TS_FMT = "%Y-%m-%dT%H:%M"

# ──────────────────────────────────────────────────────────────
# Content helpers
# ──────────────────────────────────────────────────────────────

def meaningful_size(path: Path) -> int:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    return len(re.sub(r"^[\s\-]*$", "", raw, flags=re.MULTILINE).strip())


def _parse_prop_values(raw: str) -> list[str]:
    """Split a Logseq property value into clean tag strings.
    Handles '#tag', '[[link]]', '#[[link]]', and plain words.
    Nested tags like 'family/trips' are preserved (Obsidian supports them).
    """
    results = []
    for part in raw.split(","):
        val = part.strip()
        val = re.sub(r"^#?\[\[(.+)\]\]$", r"\1", val)
        val = val.lstrip("#").strip().rstrip(".")
        if val:
            results.append(val)
    return results


_PROP_RE = re.compile(r'^([A-Za-z][A-Za-z0-9_-]*)::[ \t]*(.*?)[ \t]*$')


def _extract_page_props(body: str) -> tuple[dict, str]:
    """Remove top-level (col-0) Logseq page properties from the body.

    Works even when Obsidian has already prepended its own YAML block.
    Skips leading blank lines, then consumes consecutive property lines.
    Unknown keys (e.g. 'public::') are silently consumed — removed from body.
    Returns (props_dict, cleaned_body).
    """
    props: dict = {}
    lines = body.split("\n")
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    start = i
    while i < len(lines):
        m = _PROP_RE.match(lines[i])
        if not m:
            break
        key, val = m.group(1).lower(), m.group(2).strip()
        if key == "tags":
            props["tags"] = _parse_prop_values(val)
        elif key in ("alias", "aliases"):
            props["aliases"] = _parse_prop_values(val)
        elif key == "title":
            t = val.rstrip(".")
            if t:
                props["title"] = t
        elif key == "category":
            props["tags"] = list(props.get("tags", [])) + _parse_prop_values(val)
        elif key == "date":
            date_val = re.sub(r"^\[\[(\d{4}-\d{2}-\d{2}).*\]\]$", r"\1", val)
            props["date"] = date_val
        # all other keys silently consumed (removed from body)
        i += 1
    remaining = lines[:start] + lines[i:]
    return props, "\n".join(remaining)


def _split_yaml(content: str) -> tuple[str, str]:
    """Split off an existing leading YAML block. Returns (inner_text, body)."""
    if not content.startswith("---\n"):
        return "", content
    end = content.find("\n---\n", 4)
    if end == -1:
        return "", content
    return content[4:end], content[end + 5:]


def _inject_into_yaml(yaml_inner: str, props: dict) -> str:
    """Append new property entries to an existing YAML block (no fences)."""
    lines = yaml_inner.rstrip("\n").split("\n")
    existing = {re.match(r'^(\w+)\s*:', l).group(1).lower()
                for l in lines if re.match(r'^(\w+)\s*:', l)}
    if props.get("title") and "title" not in existing:
        lines.append(f'title: "{props["title"]}"')
    if props.get("date") and "date" not in existing:
        lines.append(f'date: {props["date"]}')
    if props.get("tags") and "tags" not in existing:
        lines += ["tags:"] + [f"  - {t}" for t in props["tags"]]
    if props.get("aliases") and "aliases" not in existing:
        lines += ["aliases:"] + [f'  - "{a}"' for a in props["aliases"]]
    return "\n".join(lines)


def _build_yaml(props: dict) -> str:
    """Build a fresh YAML frontmatter block from props."""
    if not props:
        return ""
    lines = ["---"]
    if "title" in props:
        lines.append(f'title: "{props["title"]}"')
    if "date" in props:
        lines.append(f'date: {props["date"]}')
    if props.get("tags"):
        lines += ["tags:"] + [f"  - {t}" for t in props["tags"]]
    if props.get("aliases"):
        lines += ["aliases:"] + [f'  - "{a}"' for a in props["aliases"]]
    lines.append("---")
    return "\n".join(lines) + "\n"


def clean(content: str) -> str:
    """Convert Logseq-specific syntax to plain Obsidian markdown."""

    # Peel off any YAML Obsidian already added
    yaml_inner, body = _split_yaml(content)

    # Extract page-level properties (case-insensitive, after any blank lines)
    props, body = _extract_page_props(body)

    # Indented block properties: "  collapsed:: true" or "  - collapsed:: true"
    body = re.sub(
        r"^[ \t]+(?:-\s+)?[A-Za-z][A-Za-z0-9_-]*::[ \t]*.*$",
        "", body, flags=re.MULTILINE,
    )

    # LOGBOOK / CLOCK time-tracking blocks
    body = re.sub(r"[ \t]*:LOGBOOK:.*?:END:[ \t]*\n?", "", body, flags=re.DOTALL)

    # Task markers → Obsidian checkbox syntax
    for marker in ("LATER", "WAITING", "NOW"):
        body = re.sub(rf"^(\s*)-\s+{marker}\s+", r"\1- [ ] ", body, flags=re.MULTILINE)
    body = re.sub(r"^(\s*)-\s+TODO\s+",  r"\1- [ ] ", body, flags=re.MULTILINE)
    body = re.sub(r"^(\s*)-\s+DOING\s+", r"\1- [ ] ", body, flags=re.MULTILINE)
    body = re.sub(r"^(\s*)-\s+DONE\s+",  r"\1- [x] ", body, flags=re.MULTILINE)

    # Dead blob: image links (Logseq mobile captures)
    body = re.sub(r"!\[[^\]]*\]\(blob:[^)]+\)", "", body)

    # Logseq date wikilinks: [[Mon, 06/15/2023]] → [[2023-06-15]]
    def _date_link(m: re.Match) -> str:
        try:
            return f"[[{datetime.strptime(m.group(1), '%m/%d/%Y').strftime('%Y-%m-%d')}]]"
        except ValueError:
            return m.group(0)
    body = re.sub(r"\[\[\w+,\s*(\d{2}/\d{2}/\d{4})\]\]", _date_link, body)

    # Block references: standalone bullet → remove line; inline → strip ref
    body = re.sub(
        r"^[ \t]*-[ \t]+\(\([0-9a-f-]{36}\)\)[ \t]*$",
        "", body, flags=re.MULTILINE,
    )
    body = re.sub(r"\(\([0-9a-f-]{36}\)\)", "", body)

    # Collapse excessive blank lines
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    # Reassemble with YAML
    if yaml_inner and props:
        return f"---\n{_inject_into_yaml(yaml_inner, props)}\n---\n\n{body}\n"
    elif yaml_inner:
        return f"---\n{yaml_inner}\n---\n\n{body}\n"
    elif props:
        return _build_yaml(props) + "\n" + body + "\n"
    return body + "\n"


# ──────────────────────────────────────────────────────────────
# Path helpers
# ──────────────────────────────────────────────────────────────

def iso_week_folder(dt: datetime) -> Path:
    """YYYY/YYYY-WXX using ISO year so Jan 1 2023 → 2022/2022-W52."""
    iso = dt.isocalendar()
    return Path(str(iso[0])) / f"{iso[0]}-W{iso[1]:02d}"


def safe_page_name(stem: str) -> str:
    name = urllib.parse.unquote(stem)
    name = name.replace("/", " - ").replace("\\", " - ")
    name = re.sub(r'[<>:"|?*\x00-\x1f]', "_", name).strip(". ")
    return name or "_unnamed"


# ──────────────────────────────────────────────────────────────
# Migration
# ──────────────────────────────────────────────────────────────

def migrate_journals() -> dict:
    src = LOGSEQ / "journals"
    if not src.exists():
        print("  [WARN] No journals/ folder found in Logseq root")
        return dict(migrated=0, skipped_empty=0, skipped_exists=0, used_conflict=0)

    stats = dict(migrated=0, skipped_empty=0, skipped_exists=0, used_conflict=0)
    base_files = [f for f in src.glob("*.md") if " 2" not in f.stem]

    for base in sorted(base_files):
        try:
            dt = datetime.strptime(base.stem, "%Y_%m_%d")
        except ValueError:
            print(f"  [WARN] Cannot parse date: {base.name}")
            continue

        conflict  = src / f"{base.stem} 2.md"
        base_ms   = meaningful_size(base)
        conf_ms   = meaningful_size(conflict) if conflict.exists() else 0

        if base_ms < EMPTY_THRESHOLD and conf_ms < EMPTY_THRESHOLD:
            stats["skipped_empty"] += 1
            continue

        if conflict.exists() and conf_ms > base_ms:
            chosen = conflict
            stats["used_conflict"] += 1
        else:
            chosen = base

        content  = clean(chosen.read_text(encoding="utf-8", errors="replace"))
        date_str = dt.strftime("%Y-%m-%d")
        dest_dir = VAULT / "Journals" / iso_week_folder(dt)
        dest     = dest_dir / f"{date_str}.md"

        if dest.exists():
            stats["skipped_exists"] += 1
            continue

        print(f"  {'[DRY]' if DRY_RUN else '[OK ]'} journal → {dest.relative_to(VAULT)}")
        if not DRY_RUN:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        stats["migrated"] += 1

    return stats


def migrate_pages() -> dict:
    stats = dict(migrated=0, skipped_empty=0, conflicts_merged=0)
    page_map: dict[str, Path] = {}

    for folder in ("pages 2", "pages"):
        src_dir = LOGSEQ / folder
        if not src_dir.exists():
            continue
        for f in src_dir.glob("*.md"):
            safe = safe_page_name(f.stem)
            existing = page_map.get(safe)
            if existing is None or meaningful_size(f) > meaningful_size(existing):
                if existing is not None:
                    stats["conflicts_merged"] += 1
                page_map[safe] = f

    for safe_stem, src_file in sorted(page_map.items()):
        if meaningful_size(src_file) < EMPTY_THRESHOLD:
            stats["skipped_empty"] += 1
            continue
        content = clean(src_file.read_text(encoding="utf-8", errors="replace"))
        dest = PAGES_DEST / f"{safe_stem}.md"
        print(f"  {'[DRY]' if DRY_RUN else '[OK ]'} page   → Logseq-Import/Pages/{safe_stem}.md")
        if not DRY_RUN:
            PAGES_DEST.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        stats["migrated"] += 1

    return stats


def migrate_assets() -> int:
    src = LOGSEQ / "assets"
    if not src.exists():
        return 0
    count = 0
    for f in sorted(src.iterdir()):
        if f.is_file():
            print(f"  {'[DRY]' if DRY_RUN else '[OK ]'} asset  → Logseq-Import/Assets/{f.name}")
            if not DRY_RUN:
                ASSETS_DEST.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, ASSETS_DEST / f.name)
            count += 1
    return count


# ──────────────────────────────────────────────────────────────
# Fixup
# ──────────────────────────────────────────────────────────────

def fixup() -> dict:
    """Re-apply clean() to every already-migrated file in place."""
    stats = dict(updated=0, unchanged=0)
    targets = list((VAULT / "Journals").rglob("*.md")) + list(PAGES_DEST.rglob("*.md"))
    for path in sorted(targets):
        original = path.read_text(encoding="utf-8", errors="replace")
        cleaned  = clean(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            print(f"  [FIX] {path.relative_to(VAULT)}")
            stats["updated"] += 1
        else:
            stats["unchanged"] += 1
    return stats


# ──────────────────────────────────────────────────────────────
# Stamp
# ──────────────────────────────────────────────────────────────

def _src_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def _patch_timestamps(vault_file: Path, created: datetime, updated: datetime) -> bool:
    """Inject/replace created+updated in YAML and sync filesystem mtime.

    If fields are absent, injects them (into existing YAML block or as new block).
    Always syncs os.utime so plugins read the right date on first open.
    """
    content = vault_file.read_text(encoding="utf-8", errors="replace")
    new = content
    c_str, u_str = created.strftime(TS_FMT), updated.strftime(TS_FMT)

    new = re.sub(r"^created:.*$", f"created: {c_str}", new, flags=re.MULTILINE)
    new = re.sub(r"^updated:.*$", f"updated: {u_str}", new, flags=re.MULTILINE)

    if "created:" not in new:
        if new.startswith("---\n"):
            end = new.find("\n---\n", 4)
            if end != -1:
                inner = new[4:end] + f"\ncreated: {c_str}\nupdated: {u_str}"
                new = f"---\n{inner}\n---\n" + new[end + 5:]
        else:
            new = f"---\ncreated: {c_str}\nupdated: {u_str}\n---\n\n" + new

    changed = new != content
    if changed:
        vault_file.write_text(new, encoding="utf-8")

    mtime_ts = updated.timestamp()
    os.utime(vault_file, (mtime_ts, mtime_ts))
    return changed


def _best_source(src_dir: Path, logseq_stem: str) -> Path | None:
    base     = src_dir / f"{logseq_stem}.md"
    conflict = src_dir / f"{logseq_stem} 2.md"
    if base.exists() and conflict.exists():
        return conflict if conflict.stat().st_size > base.stat().st_size else base
    return base if base.exists() else (conflict if conflict.exists() else None)


def stamp_journals() -> dict:
    src = LOGSEQ / "journals"
    stats = dict(stamped=0, skipped=0)
    for vault_file in sorted((VAULT / "Journals").rglob("*.md")):
        try:
            dt = datetime.strptime(vault_file.stem, "%Y-%m-%d")
        except ValueError:
            continue
        chosen = _best_source(src, dt.strftime("%Y_%m_%d"))
        if not chosen:
            stats["skipped"] += 1
            continue
        # created = journal date midnight (semantically meaningful)
        # updated = source file mtime  (st_birthtime unreliable for iCloud)
        created = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        if _patch_timestamps(vault_file, created, _src_mtime(chosen)):
            print(f"  [STAMP] {vault_file.relative_to(VAULT)}")
            stats["stamped"] += 1
        else:
            stats["skipped"] += 1
    return stats


def stamp_pages() -> dict:
    stats = dict(stamped=0, skipped=0)
    page_map: dict[str, Path] = {}
    for folder in ("pages 2", "pages"):
        src_dir = LOGSEQ / folder
        if not src_dir.exists():
            continue
        for f in src_dir.glob("*.md"):
            safe = safe_page_name(f.stem)
            existing = page_map.get(safe)
            if existing is None or meaningful_size(f) > meaningful_size(existing):
                page_map[safe] = f

    for safe_stem, src_file in page_map.items():
        vault_file = PAGES_DEST / f"{safe_stem}.md"
        if not vault_file.exists():
            stats["skipped"] += 1
            continue
        ts = _src_mtime(src_file)
        if _patch_timestamps(vault_file, ts, ts):
            print(f"  [STAMP] Logseq-Import/Pages/{safe_stem}.md")
            stats["stamped"] += 1
        else:
            stats["skipped"] += 1
    return stats


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    if FIXUP:
        print(f"\n{'='*60}\n  [FIXUP] re-cleaning migrated files\n{'='*60}\n")
        s = fixup()
        print(f"\n  updated={s['updated']}  unchanged={s['unchanged']}\n{'='*60}\n")
        return

    if STAMP:
        print(f"\n{'='*60}\n  [STAMP] backfilling timestamps\n{'='*60}\n")
        print("── Journals ──")
        j = stamp_journals()
        print(f"  stamped={j['stamped']}  skipped={j['skipped']}")
        print("── Pages ──")
        p = stamp_pages()
        print(f"  stamped={p['stamped']}  skipped={p['skipped']}\n{'='*60}\n")
        return

    mode = "DRY-RUN — pass --apply to write" if DRY_RUN else "APPLY"
    print(f"\n{'='*60}\n  Logseq → Obsidian  [{mode}]\n{'='*60}\n")

    print("── Journals ──")
    j = migrate_journals()
    print(f"  migrated={j['migrated']}  empty={j['skipped_empty']}"
          f"  exists={j['skipped_exists']}  conflict_resolved={j['used_conflict']}\n")

    print("── Pages ──")
    p = migrate_pages()
    print(f"  migrated={p['migrated']}  empty={p['skipped_empty']}"
          f"  deduped={p['conflicts_merged']}\n")

    print("── Assets ──")
    a = migrate_assets()
    print(f"  copied={a}\n")

    print(f"{'='*60}")
    print(f"  Total: journals={j['migrated']}  pages={p['migrated']}  assets={a}")
    if DRY_RUN:
        print("  → Re-run with --apply to write files.")
    else:
        print("  → Done. Run --fixup then --stamp next.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
