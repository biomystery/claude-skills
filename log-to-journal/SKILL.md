---
name: log-to-journal
description: Appends a thin, timestamped record to today's Obsidian daily journal — time-first (prefer start–end), one-line outcome plus [[wikilinks]] to hubs/spokes instead of restating detail, optional short inspiration lines — and handles path resolution, reverse-chronological insert, linter races, and Unicode-safe fallbacks. Use when the user says "log this", "add to journal", "记录到 journal", or after meaningful work that should leave a timeline pointer (not a full archive dump).
user-invocable: true
---

# Log to Journal

Appends one **thin** timestamped entry to the user's Obsidian **daily journal**. The daily note is a **timeline / index**, not the archive — durable detail lives in hub/spoke notes; the journal points at them with time + a one-line outcome. Resolves `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`, inserts reverse-chronologically, bumps `updated:`, and falls back to a UTF-8-safe inserter when `Edit` fails.

## When to Use

- The user just did something worth recording: a decision, purchase, booking, errand, fix, or research result
- The user explicitly says "log this", "add to journal", "记录到 journal"
- You finished a task and the vault's CLAUDE.md asks you to proactively log meaningful work
- A short inspiration / thought should be captured without opening a new note

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| **Journal = timeline pointer, not archive** | Restating spoke content bloats dailies and makes weekly review expensive |
| **Time comes FIRST**: `08:02 …` or `08:02–08:40 …` — never emoji-before-time | Vault sort key; prefer **start–end** when session length is known |
| **One line is the default** — headline may include the outcome + links | Scannable day; details are a click away |
| **If a `[[wikilink]]` exists (or you just created one), do not paste its body into the journal** | Single source of truth stays in the hub/spoke |
| **Nested sub-bullets are rare** — at most 1–2 short lines (money, next action, caveat). Never nested lists of content that belongs in a spoke | Prevents the encyclopedic dump pattern |
| **Inspiration OK** as 1–2 lines with no fake structure | Not everything needs a project note |
| Get the time from `date "+%H:%M"` (and end time if the block just finished); never guess | Honest clock |
| **Reverse-chronological within a section** — newer timestamps above older ones | Vault convention |
| Link related notes with `[[wikilinks]]` | Weaves the day into the vault |
| Bump frontmatter `updated:` after editing | Metadata honesty |
| Re-read immediately before editing | iCloud/Obsidian linter race |
| **If today's log already has the entry, enrich thinly** — append at most one short sub-bullet or tighten the headline; don't grow a novel under the same timestamp | Follow-ups extend the pointer, not the archive |

### How detailed is enough? (resolves the tension)

| Enough for the journal | Too much — put it in a spoke instead |
|---|---|
| Who / what + outcome in **≤1 line** + links | Background narrative, multi-bullet body, full lists (rules, findings, quotes) |
| Optional: amount, deadline, or next action in **one** short sub-bullet | Re-stating anything already written under a `[[wikilink]]` |
| Inspiration / open question in 1–2 lines | Meeting-minutes or analysis-novel under Life/Work |

**Division of labor:** write or update the hub/spoke **first** when detail must persist → then log a thin pointer with time + links. If there is no note yet and detail is large, create a minimal spoke and link it — don't expand the journal entry.

## Instructions

### Step 0: Resolve the journal file path

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/log-to-journal/SKILL.md)")"
VAULT="${VAULT_DIR:-$PWD}"
DATE=$(date "+%Y-%m-%d")
YEAR=$(date "+%Y")
# Sunday (%u=7): use tomorrow's ISO week. Mon–Sat: today's %V is correct.
if [ "$(date "+%u")" = "7" ]; then
  WEEK=$(date -v+1d "+%Y-W%V" 2>/dev/null || date -d "tomorrow" "+%Y-W%V")
else
  WEEK=$(date "+%Y-W%V")
fi
TIME=$(date "+%H:%M")
JOURNAL="$VAULT/Journals/$YEAR/$WEEK/$DATE.md"
echo "$JOURNAL" && ls -la "$JOURNAL"
```

> Example: `2026-08-16` (Sunday) → `Journals/2026/2026-W34/`. Prefer the weekly note's `journal-start-date` / `journal-end-date` if `%V` and the folder disagree.

If the file does not exist, the vault's Calendar plugin normally creates it from a template. Create a minimal one only if the user confirms — otherwise stop and ask.

### Step 1: Read the file and pick the section

| Section | What goes here |
|---|---|
| `## 🏠 Life` | Home, errands, purchases, family, health, personal admin |
| `## 💼 Work` | Job / employer tasks |
| `## 📖 Study` | Learning, reading, research for self-education |

When in doubt, default to `🏠 Life`. If the user named a section, use that.

### Step 2: Compose a thin entry

**Default shape (preferred):**

```markdown
- HH:MM <emoji> <one-line outcome> [[Spoke Or Hub]] · [[Other]]
```

**With duration** (when you know start and end):

```markdown
- HH:MM–HH:MM <emoji> <one-line outcome> → [[Spoke]]
```

**Rare sub-bullet** (money / next action / caveat only):

```markdown
- 14:44 🛒 HD 购入新热水器 [[Home/Water Heater]]
	- Rheem 50gal **$1,054.87** · next: book plumber
```

**Inspiration** (no forced project structure):

```markdown
- 22:15 💡 Idea: career floor = 20-min Tue/Thu block before deep work
```

#### Anti-pattern → fix

❌ Dumping spoke content into the journal:

```markdown
- 20:10 🎒 [[April]] 4th Grade — 复盘「LEVEL UP」…
	- **背景**：…
	- **7 大规则**：L / E / V / E / L / U / P …
	- **案卷归档**：新建 [[How to Level Up at School]] …
```

✅ Pointer only:

```markdown
- 20:10 🎒 [[April]] 4th Grade — 复盘「LEVEL UP」→ [[How to Level Up at School]] · 回写 [[2026-09-13 Fourth Grade Updates]]
```

or shorter:

```markdown
- 20:10–20:40 🎒 [[April]] LEVEL UP 复盘 + 准则卡 [[How to Level Up at School]]
```

Rules of thumb:

- Emoji optional (🛒 🔧 ✅ 🚗 💰 📄 ☎️ 💡 🎒 …).
- `**bold**` only for key figures/outcomes on the thin line.
- Indent any rare sub-bullet with a **tab**, not spaces.
- Prefer linking people as `[[Name]]` and artifacts as the spoke you just wrote.

### Step 3: Insert in reverse-chronological position

Within the chosen section, find where the new `HH:MM` belongs so that **newer is higher**:
- Newer than every existing entry → insert as the **first** bullet under the section header.
- Otherwise → insert immediately **above** the first existing entry whose time is **earlier** than the new one.

Prefer the `Edit` tool, anchoring on the existing bullet you're inserting above/below.

### Step 4: Handle the two edge cases that break `Edit`

**A. Linter race** — *"File has been modified since read."* **Fix:** Read again, then immediately Edit.

**B. Unicode mismatch** — `Edit` fails on `→ ⏳ ❌ —` / CJK / NBSP. **Fix:** use the helper (don't retry `Edit`):

```bash
python3 "$SKILL_DIR/scripts/journal_insert.py" \
  --file "$JOURNAL" \
  --anchor "- 13:07 🔧 [[Logseq-Import/Pages/gas heater|热水器]]" \
  --position before \
  --text $'- 20:00–20:45 ✅ [[...]] 新机安装完成 · 安装费 \$690'
```

See `scripts/journal_insert.py`.

### Step 5: Bump the frontmatter `updated:` timestamp

```
updated: YYYY-MM-DDTHH:MM
```

Use `date "+%Y-%m-%dT%H:%M"`.

### Step 6: Report

Tell the user the time (or range), section, and the one-line pointer that was logged. Don't paste the whole file.

## Example Invocations

```
/log-to-journal bought a new water heater, Rheem XG50T12HN38U2, $1,054.87
```
→ Thin `🛒` Life line + amount sub-bullet only if useful; link a home note if one exists.

```
/log-to-journal
```
→ After a task: reconstruct **time + outcome + links to notes you wrote** — not the full session transcript.

## Output

One thin timestamped bullet (optional 1 short sub-bullet) in today's `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`, with `updated:` bumped.

## Requirements

- Obsidian vault using `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`
- `date` with `%V` ISO-week support (GNU/BSD)
- `python3` for the Unicode-safe insert fallback

## Skill Structure

```
log-to-journal/
├── SKILL.md
├── README.md
└── scripts/
    └── journal_insert.py
```
