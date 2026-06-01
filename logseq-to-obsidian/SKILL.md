---
name: logseq-to-obsidian
description: Migrates a Logseq vault (journals, pages, assets) into an Obsidian vault — converts filenames, cleans Logseq-specific syntax, converts page properties to YAML frontmatter, resolves iCloud conflict copies, removes empty files, and backfills created/updated timestamps from source mtimes. Use when moving a Logseq graph to Obsidian, or cleaning up a partially migrated vault.
user-invocable: true
---

# Logseq to Obsidian Migration

Migrates a Logseq vault into an existing Obsidian vault. Handles the full conversion pipeline: journal filename normalization, weekly folder placement, syntax cleanup, YAML frontmatter generation, iCloud conflict resolution, empty-file pruning, and timestamp backfilling. The migration script is idempotent and non-destructive — it never modifies the Logseq source.

## When to Use

- You have a Logseq vault (local or iCloud) and want to move its history into Obsidian
- Your Obsidian vault uses a `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md` layout
- You want pages staged for manual sorting before committing them to final folders

## Instructions

### Step 0: Gather Paths

Ask the user for:
1. **Logseq root** — the folder containing `journals/`, `pages/`, `assets/` (e.g. `~/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents`)
2. **Obsidian vault root** — the vault folder (e.g. `~/Documents/MyVault`)

Confirm both paths exist:

```bash
ls "<logseq_root>/journals/" | head -5
ls "<obsidian_root>/Journals/" | head -5
```

### Step 1: Audit the Source Vault

Run a quick inventory before touching anything:

```bash
# Journal file count and date range
ls "<logseq_root>/journals/" | wc -l
ls "<logseq_root>/journals/" | head -3
ls "<logseq_root>/journals/" | tail -3

# iCloud " 2" conflict copies (keep the larger one)
ls "<logseq_root>/journals/" | grep " 2" | wc -l

# Page counts
ls "<logseq_root>/pages/" 2>/dev/null | wc -l
ls "<logseq_root>/pages 2/" 2>/dev/null | wc -l

# Near-empty files (Logseq empty bullets = just "-")
find "<logseq_root>/journals" -name "*.md" -size -20c | wc -l
```

Report the counts to the user and confirm they want to proceed.

### Step 2: Dry-Run

Run the script in dry-run mode to preview what will happen without writing anything:

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/logseq-to-obsidian/SKILL.md)")"
python3 "$SKILL_DIR/scripts/logseq_migrate.py" \
    "<logseq_root>" \
    "<obsidian_root>"
```

Review the output with the user. Key things to check:
- Journal date range looks right
- Page count is plausible
- No unexpected `[WARN]` lines

### Step 3: Apply Migration

```bash
python3 "$SKILL_DIR/scripts/logseq_migrate.py" \
    "<logseq_root>" \
    "<obsidian_root>" \
    --apply
```

**What gets created:**

| Source | Destination |
|---|---|
| `journals/YYYY_MM_DD.md` | `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md` |
| `pages/*.md` + `pages 2/*.md` | `Logseq-Import/Pages/` (staging) |
| `assets/*` | `Logseq-Import/Assets/` |

**Conflict resolution (iCloud " 2" files):**
- Logseq + iCloud sometimes creates `2023_11_17 2.md` alongside `2023_11_17.md`
- Script keeps whichever has more meaningful content (larger file wins)
- Near-empty files (< 20 bytes of real content after stripping Logseq bullets) are skipped

**Syntax cleaned automatically:**

| Logseq syntax | Obsidian result |
|---|---|
| `collapsed:: true` (indented property) | Removed |
| `:LOGBOOK:` … `:END:` blocks | Removed |
| `TODO` / `DONE` / `DOING` / `LATER` | `- [ ]` / `- [x]` |
| `![img](blob:https://…)` | Removed (dead mobile captures) |
| `[[Mon, 06/15/2023]]` date links | `[[2023-06-15]]` |
| `((uuid))` standalone block ref bullet | Whole line removed |
| `((uuid))` inline in text | Ref stripped, surrounding text kept |
| `tags:: val1, [[link]], #tag` | YAML `tags:` list (normalized) |
| `alias:: name` | YAML `aliases:` list |
| `title:: Page Title` | YAML `title:` |
| `Tags::` / `TAGS::` (any case) | Same as above — case-insensitive |

**Edge case — YAML already prepended by Obsidian:**
If Obsidian's plugin has already added `created`/`updated` YAML to the file, the script peels it off, extracts the Logseq properties from the body below it, then re-injects the properties into that existing YAML block. Never creates a double `---` fence.

### Step 4: Fixup Pass (run after Step 3)

Re-apply cleaning to all migrated files — catches any files where Obsidian had already added its own YAML block before migration ran:

```bash
python3 "$SKILL_DIR/scripts/logseq_migrate.py" \
    "<logseq_root>" \
    "<obsidian_root>" \
    --fixup
```

Expect most files to show `unchanged`. Only files that still had residual Logseq syntax will show `[FIX]`.

### Step 5: Stamp Timestamps (run after Step 4)

Backfill `created` / `updated` YAML fields and sync filesystem `mtime` from the Logseq source files:

```bash
python3 "$SKILL_DIR/scripts/logseq_migrate.py" \
    "<logseq_root>" \
    "<obsidian_root>" \
    --stamp
```

**Timestamp strategy:**

| File type | `created` | `updated` |
|---|---|---|
| Journals | Midnight of the journal date (from filename) | Source file `mtime` |
| Pages | Source file `mtime` | Source file `mtime` |

> **Why not `st_birthtime`?** For iCloud-synced Logseq vaults, `st_birthtime` reflects when the file was first downloaded to this machine — not when it was originally written. `mtime` is more reliable. For journals, the filename date is the most semantically meaningful "created" date regardless.

The stamp also sets `os.utime()` on each vault file so that Obsidian plugins that read filesystem timestamps will see the correct date when they first open the file.

### Step 6: Verify

```bash
# No Logseq property lines should remain at column 0
grep -r "^[A-Za-z][A-Za-z0-9_-]*::" "<obsidian_root>/Journals" "<obsidian_root>/Logseq-Import" | wc -l
# → should be 0

# No block references should remain
grep -r "(([0-9a-f-]\{36\}))" "<obsidian_root>/Journals" "<obsidian_root>/Logseq-Import" | wc -l
# → should be 0

# No collapsed:: should remain
grep -r "collapsed::" "<obsidian_root>/Journals" | wc -l
# → should be 0
```

Open Obsidian, check the Tags panel and the Unresolved Links panel. Pages in `Logseq-Import/Pages/` are already found by Obsidian's global link resolver — `[[wikilinks]]` pointing to them will resolve even before manual sorting.

### Step 7: Sort Pages (manual)

`Logseq-Import/Pages/` is a staging area. Guide the user to sort pages into their final vault folders:

| Page type | Suggested destination |
|---|---|
| Trip / vacation notes | `Projects/Done/` |
| People notes | `People/` or `Family/` |
| Topic / reference notes | `Clean/` |
| Saved web articles | `Clippings/` |

The Logseq-Import folder can be deleted once all pages are sorted.

## Example Invocations

```
/logseq-to-obsidian
```
→ Prompts for Logseq root and Obsidian vault root, then runs full pipeline

```
/logseq-to-obsidian ~/logseq-vault ~/Documents/MyVault
```
→ Skips path prompts if provided as args

## Output

```
Logseq-Import/
├── Pages/          ← 300+ migrated pages (staging)
└── Assets/         ← images, audio files

Journals/
├── 2022/
│   ├── 2022-W41/
│   │   ├── 2022-10-14.md   ← created: 2022-10-14T00:00
│   │   └── ...
│   └── ...
├── 2023/
└── 2024/
```

## Requirements

- Python 3.8+
- Logseq vault with `journals/` folder (and optionally `pages/`, `pages 2/`, `assets/`)
- Obsidian vault with an existing `Journals/` folder (any content — migration skips existing files)

## Skill Structure

```
logseq-to-obsidian/
├── SKILL.md
├── README.md
└── scripts/
    └── logseq_migrate.py   ← 4-mode migration script (dry-run/apply/fixup/stamp)
```
