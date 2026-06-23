---
name: morning-plan
description: Morning planning routine for an Obsidian vault — retroactively logs yesterday's activities, identifies today's MITs, schedules urgent todos via ⏳ on the weekly note, and surfaces imminent deadlines. Designed for a Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md vault layout with Obsidian Tasks plugin.
user-invocable: true
---

# Morning Plan

Runs the full start-of-day planning loop for the vault: reviews the weekly note and recent journals, prompts the user for yesterday's highlights and today's work tasks, logs everything to the right files, schedules urgent todos via the Tasks plugin `⏳` syntax, and surfaces any deadlines due today or tomorrow.

## When to Use

- The user starts a session without a specific task ("今天该做什么?", "what should I work on?", "morning check-in")
- The user explicitly invokes `/morning-plan`
- You detect it's early in the day and no daily journal Work section has been populated yet

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| Re-read any file immediately before editing | iCloud/Obsidian linter rewrites files between read and edit — stale reads cause edit failures |
| `⏳` goes on the SOURCE file (weekly note), NOT the daily inbox | Daily Scheduled section uses a Tasks plugin query that surfaces `⏳`-tagged tasks automatically; duplicating to inbox creates noise |
| MITs: caveman mode — 2–3 bullets, 5–8 words each | User preference; no prose in the Highlight section |
| Time comes FIRST in every journal entry: `08:02 ⚽ ...` | Vault convention — timestamp is the sort key |
| Reverse-chronological within a section | Newer timestamps go above older ones |
| Get real time from `date "+%H:%M"` | Never guess the time |

## Instructions

### Step 0: Resolve file paths

```bash
VAULT="${VAULT_DIR:-$PWD}"
DATE=$(date "+%Y-%m-%d")
YESTERDAY=$(date -v-1d "+%Y-%m-%d" 2>/dev/null || date -d "yesterday" "+%Y-%m-%d")
YEAR=$(date "+%Y")
WEEK=$(date "+%Y-W%V")
YESTERDAY_WEEK=$(date -v-1d "+%Y-W%V" 2>/dev/null || date -d "yesterday" "+%Y-W%V")

TODAY_JOURNAL="$VAULT/Journals/$YEAR/$WEEK/$DATE.md"
YESTERDAY_JOURNAL="$VAULT/Journals/$YEAR/$YESTERDAY_WEEK/$YESTERDAY.md"
WEEKLY_NOTE="$VAULT/Journals/$YEAR/$WEEK.md"
```

Verify all three files exist before proceeding. If the weekly note is missing, check `$VAULT/Journals/$YEAR/$WEEK/` for a file named like `$WEEK.md` one level up.

### Step 1: Read context files

Read in this order:
1. Today's daily journal — check if MITs / Work section already populated
2. Yesterday's daily journal — scan for incomplete entries, gaps to fill
3. Weekly note — scan open `- [ ]` tasks and any deadline markers (⚠️, 截止, due)

If today's journal Work section already has substantial entries, skip Step 3 (MITs already set) and go directly to Step 4.

### Step 2: Ask user for yesterday's highlights

Prompt: *"昨天重点是什么？Any notable events, decisions, or completions to log?"*

Accept a mix of Chinese and English shorthand. Extract:
- **Completions** → log with `✅` emoji
- **Pending/follow-ups** → log with `⚠️` or plain text + note action needed
- **Life events** (purchases, calls, personal) → `## 🏠 Life` section
- **Work events** (meetings, deliverables, interviews) → `## 💼 Work` section

Log each item to yesterday's journal under the correct section, reverse-chronological. Re-read the file immediately before each edit.

### Step 3: Identify today's MITs

Ask the user: *"今天要做什么？What are the 2–3 most important tasks?"*

Format the MITs as caveman-mode bullets (5–8 words each) and write them to today's journal Highlight section:

```
> - MITs: 1) <short task> 2) <short task> 3) <short task if any>
```

Also log the tasks to today's `## 💼 Work` section with timestamp and checkboxes:

```
- HH:MM 今日工作任务梳理
	- [ ] **Task owner — short description**
	- [ ] **Task owner — short description**
```

### Step 4: Schedule urgent todos

Scan the weekly note for `- [ ]` tasks that are:
- Due today or tomorrow (look for 截止, deadline, ⚠️ within the task text)
- Explicitly mentioned by the user as needing action today

For each, add `⏳ YYYY-MM-DD` (today's date) to the task **in the weekly note** — do NOT copy to the daily inbox.

```
- [ ] Submit vendor renewal form ⏳ 2026-06-23
```

Re-read the weekly note before each edit.

### Step 5: Surface deadline reminders

After all edits, output a brief caveman summary:

```
**Today's MITs:**
1. <task>
2. <task>

**⚠️ Deadlines:**
- <item> — due <date>
```

If no deadlines, omit that section.

## Example Invocations

```
/morning-plan
```
→ Claude reads context, asks for yesterday's highlights + today's tasks, logs everything

```
/morning-plan
昨天：team meeting，跑腿办了银行的事，看了球赛
今天：1) 数据分析任务 2) 准备汇报材料
```
→ User front-loads both answers; Claude logs without further prompting

## Output

- Yesterday's journal updated with retroactive entries under `🏠 Life` and `💼 Work`
- Today's journal Highlight section updated with caveman-mode MITs
- Today's journal Work section populated with timestamped task list
- Weekly note updated with `⏳` on any todos scheduled for today
- Deadline summary output to the user

## Requirements

- Obsidian vault with `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md` daily note structure
- Weekly notes at `Journals/YYYY/YYYY-WXX.md`
- Obsidian Tasks plugin (for `⏳` scheduled-date queries in daily notes)
- CLAUDE.md in vault root documenting vault conventions (section names, emoji usage, wikilink style)

## Skill Structure

```
morning-plan/
├── SKILL.md
└── README.md
```
