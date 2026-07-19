---
name: review-week
description: Review the past week's Obsidian daily journal entries, synthesize them by theme into the weekly note's Wins/Challenges/Lessons retrospective (split 重要 vs 琐事), and roll any unresolved loose ends forward into the current week's priorities list. Use for "review my past week", "weekly review", "close out this week", or "什么 open 了 roll 到这周".
argument-hint: "[just do it]"
user-invocable: true
---

# Review Week

Reads every daily journal entry in the past week, groups them into threads (not by day — the same saga often spans several days), classifies each thread as **重要** or **琐事**, writes that synthesis into last week's weekly note as a proper retrospective, and carries only the genuinely unresolved items into this week's priorities. Built for a vault using the `Journals/YYYY/YYYY-WNN.md` (weekly) + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md` (daily) layout with a `journal-start-date`/`journal-end-date` frontmatter pair on each weekly note.

## When to Use

- The user says "review my past week", "weekly review", "log this to last week's journal", "carry open tasks to this week"
- It's the start of a new week and the user wants last week closed out properly
- The user asks what's still open / outstanding from last week

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| Resolve week boundaries from **frontmatter dates**, never from a naive `date +%V` on the target day | Some vaults number Sun–Sat weeks by the ISO week of the *Monday* inside them — a Sunday's own ISO week number is off by one from the folder it lives in. See `scripts/find_week_files.py`. |
| Synthesize by **thread/project**, not by day | The same saga (an appliance issue, an insurance claim) usually spans multiple daily entries; a day-by-day recap just repeats itself |
| Split every thread into **🎯 重要** vs **📎 琐事** — never flatten them into one list | Highlight and priorities should surface career/family/system leverage, not warranty chats and small refunds. Compass: `AI Memory/MyMemory.md` |
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

### Step 1: Read the past week's daily notes + priority compass

1. Read every file in `past_week.daily_files`. Each has `## 🏠 Life`, `## 💼 Work`, `## 📖 Study` sections with time-first bullets (`HH:MM emoji text`, detail nested below).
2. Read `AI Memory/MyMemory.md` (especially **§10 反复在意的几件大事** and **§5–6 长期项目 / 家庭进行中**) — this is the classifier for Step 2. If the file is missing, fall back to: career / next role, AI-as-asset & side projects, family hard deadlines (immigration, medical, kids' travel), finance bonuses with deadlines, and life-as-system improvements → 重要; everything else → 琐事.

### Step 2: Synthesize by thread, then classify 重要 vs 琐事

Group entries across days by the project/topic they share (usually visible via a common `[[wikilink]]`), not by calendar day. For each thread, determine:
- What happened (one line)
- Resolved, or still open?
- If open: what's the next concrete action and any deadline
- **Label: 🎯 重要 or 📎 琐事**

**🎯 重要** — maps to MyMemory's big cares or active high-stakes family/career tracks, e.g.:
- Career capital / next role / comp / LinkedIn positioning
- AI products & reusable assets (side projects, job tools, personal knowledge graph) when they serve the primary bet
- Family hard stakes: immigration, medical bills/insurance fights, kids' major travel
- Finance with real money/deadlines (account bonuses, tax filings)
- Meta-systems that change how life is run (GTD redesign, quarterly lock)

**📎 琐事** — real effort, low leverage on the above, e.g.:
- Appliance warranty ping-pong, small refunds, misplaced gadgets
- Routine errands, kids' recurring activities (unless a decision/deadline hinges on it)
- Exploratory one-offs with no commitment (optional consulting outreach, tool trials)

Borderline rule: if a "household" saga involves **significant money, product safety, or multi-day blockage**, put the *decision outcome* under 重要 and the *back-and-forth noise* under 琐事 (or omit noise from Highlight).

Present the synthesis to the user in chat **as two tables** (重要 / 琐事) before writing anything, unless they've already said "just do it."

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
- **✨ Highlight** — one line from **重要 only** (the single most notable career/family/system move). Never lead with 琐事.
- **📋 本周重点** subsections — check off (`- [x]`) whatever that week's pre-existing intentions actually got done; leave unchecked what didn't. Optionally append a short outcome note after the checkbox line.
- **🎉 Wins** and **🚧 Challenges** — use two subsections:
  ```markdown
  ### 🎯 重要
  - …
  ### 📎 琐事
  - …
  ```
  Keep 琐事 to ≤2–3 bullets total across Wins+Challenges; omit pure noise.
- **💡 Lessons** — 1-3 bullets, **重要 takeaways only** (generalizable). No lessons from trivia.
- **📅 下周计划** — same open items as Step 4, also split:
  ```markdown
  ### 🎯 重要
  - 🔴 … / 🟠 … / 🟡 …
  ### 📎 琐事（有截止才跟）
  - …
  ```

Prefer the `Edit` tool. If it fails to match because of curly quotes or other punctuation drift in the placeholder text, fall back to:

```bash
python3 "$SKILL_DIR/scripts/replace_section.py" \
  --file "<past_week.weekly_file>" \
  --heading "## 🎉 Wins" \
  --body $'### 🎯 重要\n- bullet one\n\n### 📎 琐事\n- bullet two'
```

Repeat per section (`## ✨ Highlight`, `## 📋 本周重点`, `## 🎉 Wins`, `## 🚧 Challenges`, `## 💡 Lessons`, `## 📅 下周计划`).

### Step 4: Roll open items into the current week

Read `current_week.weekly_file`. Fill its `📋 本周重点` block with unresolved threads from Step 2, sorted by urgency — **重要 first**:

- `### 🔴 紧急` — near-term deadline or actively blocking (**重要** preferred; 琐事 only if hard deadline ≤ ~7 days)
- `### 🟠 本周` — should get done this week (**重要** only, unless a 琐事 has a clear this-week action)
- `### 🟡 跟进` — longer-horizon, waiting on someone else, or 琐事 with a soft/far deadline

Each item: one line, linked back to its project note via `[[wikilink]]` if one exists. Same `Edit` / `replace_section.py` fallback rule as Step 3.

Do **not** roll forward resolved 琐事 or open 琐事 with no deadline and no leverage.

### Step 5: Bump frontmatter timestamps

For both files, set `updated:` to now:

```bash
date "+%Y-%m-%dT%H:%M"
```

### Step 6: Report

Summarize in chat: what got written to last week's retrospective (call out the 重要 Highlight), what got rolled into this week's priorities (grouped by urgency), and don't re-paste the full file contents.

## Example Invocations

```
/review-week
```
→ Reviews the past week's daily notes, fills in last week's Wins/Challenges/Lessons (重要/琐事 split), and populates this week's 📋 本周重点 with open items.

```
review my past week
```
→ Same, invoked as natural language rather than a slash command.

```
/review-week just do it
```
→ Skip the pre-write synthesis confirmation; write directly.

## Output

Two weekly notes updated in place:
- `Journals/YYYY/YYYY-WNN.md` (past week) — Highlight (重要), checked-off 本周重点, Wins/Challenges/下周计划 with 🎯/📎 subsections, Lessons
- `Journals/YYYY/YYYY-WNN.md` (current week) — 📋 本周重点 populated with rolled-forward open items by urgency (重要 biased)

## Requirements

- Obsidian vault using `Journals/YYYY/YYYY-WNN.md` + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md` layout
- Each weekly note has `journal-start-date` / `journal-end-date` frontmatter (used instead of computed week numbers)
- `python3` for both helper scripts
- Priority compass (optional but expected in this vault): `AI Memory/MyMemory.md`

## Skill Structure

```
review-week/
├── SKILL.md
├── README.md
└── scripts/
    ├── find_week_files.py
    └── replace_section.py
```
