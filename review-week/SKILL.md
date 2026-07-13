---
name: review-week
description: Review the past week's Obsidian daily journal entries, synthesize them by theme into the weekly note's Wins/Challenges/Lessons retrospective, and roll any unresolved loose ends forward into the current week's priorities list. Use for "review my past week", "weekly review", "close out this week", or "什么 open 了 roll 到这周".
user-invocable: true
---

# Review Week

Reads every daily journal entry in the past week, groups them into threads (not by day — the same saga often spans several days), writes that synthesis into last week's weekly note as a proper retrospective, and carries only the genuinely unresolved items into this week's priorities. Built for a vault using the `Journals/YYYY/YYYY-WNN.md` (weekly) + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md` (daily) layout with a `journal-start-date`/`journal-end-date` frontmatter pair on each weekly note.

## When to Use

- The user says "review my past week", "weekly review", "log this to last week's journal", "carry open tasks to this week"
- It's the start of a new week and the user wants last week closed out properly
- The user asks what's still open / outstanding from last week

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| Resolve week boundaries from **frontmatter dates**, never from a naive `date +%V` on the target day | Some vaults number Sun–Sat weeks by the ISO week of the *Monday* inside them — a Sunday's own ISO week number is off by one from the folder it lives in. See `scripts/find_week_files.py`. |
| Synthesize by **thread/project**, not by day | The same saga (an appliance issue, an insurance claim) usually spans multiple daily entries; a day-by-day recap just repeats itself |
| Only roll forward items that are **still open** | Don't copy-paste every bullet into the new week — dedupe, and drop anything already resolved |
| Re-read a weekly file immediately before editing it | The iCloud/Obsidian linter can rewrite the file between read and edit |
| If `Edit` fails to match template placeholder text, don't retry with tweaks — use `scripts/replace_section.py` | Weekly-note templates often use curly quotes (`'`) or CJK punctuation in their prompt lines that look identical to plain ASCII but fail an exact string match |
| Bump each edited file's frontmatter `updated:` timestamp | Keeps Obsidian metadata honest |

## Instructions

### Step 0: Resolve the current and past week's files

```bash
VAULT="${VAULT_DIR:-$PWD}"
python3 "$SKILL_DIR/scripts/find_week_files.py" --vault "$VAULT"
```

This prints JSON with `current_week` and `past_week`, each giving `weekly_file`, `daily_dir`, `start`/`end`, and the list of `daily_files` that actually exist in range. Use these paths for every step below — don't re-derive them by hand.

If `past_week` is `null` (no earlier weekly note exists), tell the user and stop, or offer to just do the current-week rollup.

### Step 1: Read the past week's daily notes

Read every file in `past_week.daily_files`. Each has `## 🏠 Life`, `## 💼 Work`, `## 📖 Study` sections with time-first bullets (`HH:MM emoji text`, detail nested below).

### Step 2: Synthesize by thread

Group entries across days by the project/topic they share (usually visible via a common `[[wikilink]]`), not by calendar day. For each thread, determine:
- What happened (one line)
- Resolved, or still open?
- If open: what's the next concrete action and any deadline

Present this synthesis to the user in chat before writing anything, unless they've already said "just do it."

### Step 3: Fill in the past week's retrospective

Read `past_week.weekly_file`. It has this template shape:

```
## ✨ Highlight
## 📋 本周重点
### 🔴 紧急
### 🟠 本周
### 🟡 跟进
## 🎉 Wins
## 🚧 Challenges
## 💡 Lessons
## 📅 下周计划
```

Write:
- **✨ Highlight** — one line, the single most notable thing
- **📋 本周重点** subsections — check off (`- [x]`) whatever that week's pre-existing intentions actually got done; leave unchecked what didn't
- **🎉 Wins** — resolved threads and genuine positives, one bullet each
- **🚧 Challenges** — what went sideways and briefly why
- **💡 Lessons** — 1-3 bullets, only include a lesson if it's a real generalizable takeaway, not filler
- **📅 下周计划** — the same open items you're about to roll into the current week (this field is optional/redundant with Step 4, but the template has it — fill it briefly)

Prefer the `Edit` tool. If it fails to match because of curly quotes or other punctuation drift in the placeholder text, fall back to:

```bash
python3 "$SKILL_DIR/scripts/replace_section.py" \
  --file "<past_week.weekly_file>" \
  --heading "## 🎉 Wins" \
  --body $'- bullet one\n- bullet two'
```

Repeat per section (`## ✨ Highlight`, `### 🔴 紧急`, `## 🚧 Challenges`, `## 💡 Lessons`, `## 📅 下周计划`).

### Step 4: Roll open items into the current week

Read `current_week.weekly_file`. Fill its `📋 本周重点` block with only the unresolved threads from Step 2, sorted by urgency:
- `### 🔴 紧急` — has a near-term deadline or is actively blocking something
- `### 🟠 本周` — should get done this week, no hard deadline
- `### 🟡 跟进` — longer-horizon or waiting on someone else

Each item: one line, linked back to its project note via `[[wikilink]]` if one exists. Same `Edit` / `replace_section.py` fallback rule as Step 3.

### Step 5: Bump frontmatter timestamps

For both files, set `updated:` to now:

```bash
date "+%Y-%m-%dT%H:%M"
```

### Step 6: Report

Summarize in chat: what got written to last week's retrospective, what got rolled into this week's priorities (grouped by urgency), and don't re-paste the full file contents.

## Example Invocations

```
/review-week
```
→ Reviews the past week's daily notes, fills in last week's Wins/Challenges/Lessons, and populates this week's 📋 本周重点 with open items.

```
review my past week
```
→ Same, invoked as natural language rather than a slash command.

## Output

Two weekly notes updated in place:
- `Journals/YYYY/YYYY-WNN.md` (past week) — Highlight, checked-off 本周重点, Wins, Challenges, Lessons, 下周计划
- `Journals/YYYY/YYYY-WNN.md` (current week) — 📋 本周重点 populated with rolled-forward open items by urgency

## Requirements

- Obsidian vault using `Journals/YYYY/YYYY-WNN.md` + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md` layout
- Each weekly note has `journal-start-date` / `journal-end-date` frontmatter (used instead of computed week numbers)
- `python3` for both helper scripts

## Skill Structure

```
review-week/
├── SKILL.md
├── README.md
└── scripts/
    ├── find_week_files.py
    └── replace_section.py
```
