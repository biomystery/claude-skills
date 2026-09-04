---
name: log-to-journal
description: Append a timestamped entry to today's Obsidian daily journal following vault conventions — resolves the YYYY/YYYY-WXX/YYYY-MM-DD.md path, inserts under the right section (Life/Work/Study) in reverse-chronological order, bumps the frontmatter updated: stamp, and handles the iCloud linter race and Unicode characters that break exact-string edits. Use whenever the user does meaningful work (decisions, purchases, fixes, errands) that should be recorded in the daily note.
user-invocable: true
---

# Log to Journal

Appends one concise, timestamped entry to the user's Obsidian **daily journal**, following the vault's logging conventions exactly. Resolves the correct dated file path, inserts the entry into the right section in reverse-chronological order, links related notes with `[[wikilinks]]`, and updates the frontmatter `updated:` timestamp. Built for a vault where raw daily records live in `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`.

## When to Use

- The user just did something worth recording: a decision, purchase, booking, errand, fix, or research result
- The user explicitly says "log this", "add to journal", "记录到 journal"
- You finished a task and the vault's CLAUDE.md asks you to proactively log meaningful work

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| **Time comes FIRST** in every entry: `08:02 ⚽ ...` — never `⚽ 08:02` | Vault convention; the timestamp is the sort key |
| **Reverse-chronological within a section** — newer timestamps go **above** older ones | Vault convention; most recent work is read first |
| Get the time from `date "+%H:%M"`, never guess | Entries must reflect the real clock |
| **Headline + detail split**: the top bullet is only `HH:MM <emoji> <short title>`; put ALL details in a nested sub-bullet underneath — even a single detail goes on its own sub-line | User's preferred style; keeps the section scannable |
| Link related notes with `[[wikilinks]]` | Keeps the daily note woven into the vault |
| Bump frontmatter `updated:` after editing | Keeps Obsidian metadata honest |
| Re-read the file immediately before editing | The iCloud/Obsidian linter rewrites files between read and edit |
| **If today's log already has the entry, enrich it in place** — append sub-bullets via `journal_insert.py --anchor <existing line> --position after`; don't add a duplicate timestamped bullet | Following up on earlier work should extend that entry, not create a redundant one |

## Instructions

### Step 0: Resolve the journal file path

The daily note lives at `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`. **This vault's week starts Sunday.** Folder `WXX` is the ISO week of the **Monday** in that Sun–Sat range — **not** `date +%V` on Sunday (Sunday `%V` is off by one).

```bash
VAULT="${VAULT_DIR:-$PWD}"          # repo root / vault root
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

Read the journal. Daily notes have these `##` sections — choose by entry type:

| Section | What goes here |
|---|---|
| `## 🏠 Life` | Home, errands, purchases, family, health, personal admin |
| `## 💼 Work` | Job / employer tasks |
| `## 📖 Study` | Learning, reading, research for self-education |

When in doubt, default to `🏠 Life`. If the user named a section, use that.

### Step 2: Compose the entry

**Two-line style (required):** the headline bullet is only `HH:MM <emoji> <short title>` — a few words, no details, no `—`-appended prose. Every detail goes in a **nested sub-bullet** below it, even when there's just one.

```
- 14:44 🛒 HD 购入新热水器
	- Rheem XG50T12HN38U2（50gal, 12年质保）$979 + 税 $75.87 = **$1,054.87**，Pickup 免费
	- 下一步：找水工安装

- 16:20 🏦 US Bank 注资开始
	- 从 Discover 转了 **$3,000**（当日 instant 额度已满）；绑定 checking (7377)，等 trial deposits 确认（~7/10）。剩 **~$22k** 待转（8/6 前存满 $25k）
```

Don't cram the description onto the headline line (`- 14:44 🛒 HD 购入新热水器 — Rheem…`) — split it.

- The emoji is optional but matches the vault's visual style (🛒 purchase, 🔧 fix, ✅ done, 🚗 car, 💰 finance, 📄 new doc, ☎️ call).
- Use `**bold**` for key figures/outcomes; `[[wikilinks]]` for related notes, people, dates.
- Indent sub-bullets with a **tab**, not spaces (matches existing entries).

### Step 3: Insert in reverse-chronological position

Within the chosen section, find where the new `HH:MM` belongs so that **newer is higher**:
- Newer than every existing entry → insert as the **first** bullet under the section header.
- Otherwise → insert immediately **above** the first existing entry whose time is **earlier** than the new one.

Prefer the `Edit` tool, anchoring on the existing bullet you're inserting above/below.

### Step 4: Handle the three edge cases that break the write

These bit real sessions — expect them:

**A. Linter race** — *"File has been modified since read."* The iCloud/Obsidian linter rewrites the file (e.g. bumps `updated:`) between your Read and Edit. **Fix:** Read the file again, then immediately Edit.

**B. Unicode mismatch** — `Edit` fails to match a line containing characters like `→ ⏳ ❌ —` or CJK text, even though it looks identical (NBSP, full-width punctuation, or escape-normalization differences). **Fix:** Don't fight it with more `Edit` retries — use the helper script for an exact byte-level replace. See `scripts/journal_insert.py`.

**C. ⚠️ zsh rejects `\U` escapes — never write emoji as escape sequences.**

`$'...'` in **zsh** supports `\u` (4 hex digits) but **not `\U` (8 hex digits)**. Every emoji lives above U+FFFF, so it needs 8 digits — and zsh aborts the entire command:

```console
$ printf '%s' $'\U0001F3AF eight-digit'
zsh: character not in range          # the whole tool call fails
$ printf '%s' $'- 16:38 🎯 literal emoji'
- 16:38 🎯 literal emoji             # literal emoji is fine
```

**Fix: paste the emoji literally.** `$'- 16:38 🎯 …'` works; `$'- 16:38 \U0001F3AF …'` does not.
*(Verified on zsh 5.9. bash's `$'...'` does accept `\U`, so this is zsh-specific — and zsh is the macOS default shell.)*

**Preferred for anything multi-line:** skip shell quoting entirely and do the insert in a Python heredoc. No `$'...'`, no escape rules, no `\$` for literal dollars, and the entry text stays readable:

```bash
python3 - <<'PY'
import io, re
p = "Journals/2026/2026-W36/2026-09-03.md"
s = io.open(p, encoding='utf-8').read()

entry = """- 16:38 🎯 归因分析
\t- **关节级**:肿胀消退 → 压痛消退 **73.9%**;肿胀持续 → **23.3%**
\t- → [[Projects/Doing/.../03 Attribution|03 Attribution]]
"""

anchor = "- 10:00 🗂️ 前一条目"
i = s.index(anchor)                      # raises if the anchor moved — fail loud
s = s[:i] + entry + s[i:]
s = re.sub(r"^updated: .*$", "updated: 2026-09-03T16:38", s, count=1, flags=re.M)
io.open(p, 'w', encoding='utf-8').write(s)
PY
```

This bumps the frontmatter in the same pass, so Step 5 comes free.

### Step 5: Bump the frontmatter `updated:` timestamp

Set the YAML `updated:` field to now (the linter often does this for you, but do it explicitly if it didn't):

```
updated: 2026-06-13T20:00
```

### Step 6: Report

Tell the user the time, section, and a one-line summary of what was logged. Don't paste the whole file back.

## Example Invocations

```
/log-to-journal bought a new water heater, Rheem XG50T12HN38U2, $1,054.87
```
→ Inserts a `🛒` entry under `🏠 Life` at the current time, in reverse-chronological order.

```
/log-to-journal
```
→ After finishing a task; reconstructs what was done this session and logs it.

## Output

One timestamped bullet (plus optional sub-bullets) inserted into today's `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`, with the frontmatter `updated:` field bumped.

## Requirements

- An Obsidian vault using the `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md` daily-note layout
- `date` with `%V` ISO-week support (GNU/BSD date both work)
- `python3` for the Unicode-safe insert fallback — **and preferred over `$'...'` for any multi-line entry, since zsh cannot parse the `\U` escapes that emoji require**

## Skill Structure

```
log-to-journal/
├── SKILL.md
├── README.md
└── scripts/
    └── journal_insert.py
```
