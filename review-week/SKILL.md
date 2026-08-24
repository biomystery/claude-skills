---
name: review-week
description: Reviews the past week's Obsidian daily journal entries, synthesizes them by thread into the weekly-note retrospective (split 重要 vs 琐事), writes a per-person family section from the vault owner's perspective, checks progress on primary goals against the long-term → short-term ladder, drafts a plan for any important goal that lacks one, and rolls open items into the current week's priorities. Use when the user says "review my past week", "weekly review", "close out this week", "family weekly review", or "什么 open 了 roll 到这周".
argument-hint: "[just do it]"
user-invocable: true
---

# Review Week

Reads every daily journal entry in the past week, groups them into threads, classifies each as **重要** or **琐事**, then writes three cuts into last week's weekly note: (1) a **per-person family section from the vault owner's perspective**, (2) a **Goals** ladder (long-term compass → short-term trace → this week's progress → plan), (3) the existing Wins/Challenges/Lessons retrospective. Rolls only unresolved items — plus any newly drafted plans — into this week's priorities. Built for `Journals/YYYY/YYYY-WNN.md` + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md` with `journal-start-date`/`journal-end-date` on each weekly note.

Source globs, person-section template, and plan heuristics: [reference.md](reference.md). Read it in Step 1.

## When to Use

- The user says "review my past week", "weekly review", "family weekly review", "log this to last week's journal", "carry open tasks to this week"
- It's the start of a new week and the user wants last week closed out properly
- The user asks what's still open from last week, or whether important goals have a plan

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| Resolve week boundaries from **frontmatter dates**, never from a naive `date +%V` on the target day | Some vaults number Sun–Sat weeks by the ISO week of the *Monday* inside them. See `scripts/find_week_files.py`. |
| Synthesize by **thread/project**, not by day | The same saga usually spans multiple daily entries |
| Split every thread into **🎯 重要** vs **📎 琐事** — never flatten them into one list | Compass: MyMemory / Self-Operating Manual / current quarter note |
| **One subsection per family hub person**, written from the **vault owner's perspective** | The review is "how I showed up for them", not their diary. Quiet week still gets a stub so nobody drops off. |
| **Every important goal has a plan** — if none exists, draft one and put the next action on this week's 本周重点 | Progress without a next action is drift |
| Goals are **guided by long-term, traced by short-term** | Long-term = 3–5yr / year theme / MyMemory big cares; short-term = quarter PRIMARY + this week's moves |
| Only roll forward items that are **still open** | Dedupe; drop resolved; don't roll open 琐事 with no deadline |
| Do **not** copy PII from person notes (IDs, DOB, accounts, medical details) into the weekly note | Link `[[Name]]`; keep private fields in the hub note |
| Re-read a weekly file immediately before editing it | iCloud/Obsidian linter can rewrite between read and edit |
| If `Edit` fails to match template placeholder text, don't retry with tweaks — use `scripts/replace_section.py` | Curly quotes / CJK punctuation break exact string match |
| Bump each edited file's frontmatter `updated:` timestamp | Keeps Obsidian metadata honest |

## Instructions

Copy and track:

```
Review progress:
- [ ] Step 0: Resolve week files
- [ ] Step 1: Read dailies + compass + family hubs
- [ ] Step 2: Three cuts (threads / people / goals+plans)
- [ ] Step 3: Write past week (insert 家人/Goals if missing)
- [ ] Step 4: Roll open items + drafted plans
- [ ] Step 5–6: Stamp + report
```

### Step 0: Resolve the current and past week's files

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/review-week/SKILL.md)")"
VAULT="${VAULT_DIR:-$PWD}"
python3 "$SKILL_DIR/scripts/find_week_files.py" --vault "$VAULT"
```

This prints JSON with `current_week` and `past_week`. Use these paths for every step below.

If `past_week` is `null`, tell the user and stop, or offer to just do the current-week rollup.

### Step 1: Read dailies, family hubs, and the goal compass

Read [reference.md](reference.md) for globs and templates, then:

1. Read every file in `past_week.daily_files` (`## 🏠 Life` / `## 💼 Work` / `## 📖 Study`, time-first bullets).
2. Read the **goal compass** (long-term first, then short-term): Self-Operating Manual (3–5 year items), current yearly note if it exists, current quarterly note (90-day PRIMARY + commitments), MyMemory (big cares + active family/career tracks).
3. List **family hub notes**: top-level `$VAULT/Family/*.md` only (not nested school/activity files). Owner = the person whose `AI Memory/` folder lives under `Family/<Name>/`. Remaining people: MyMemory family-sentence order if present, else alphabetical.
4. For each hub note, read **active goals, next steps, and deadlines only**. Do not copy IDs, DOB, account numbers, or medical details into the weekly note.

If compass files are missing, fall back to: career / next role, AI-as-asset & side projects, family hard deadlines, finance with deadlines, life-as-system → 重要; everything else → 琐事.

### Step 2: Synthesize three cuts

Work from the same daily threads. Produce three cuts before writing.

**A. Threads (existing)** — group by project/`[[wikilink]]`. For each: one-line what happened; resolved or still open; if open: next action + deadline; label 🎯 重要 or 📎 琐事.

**🎯 重要** maps to the compass: career capital / next role; AI products as assets; family hard stakes; finance with real money/deadlines; meta-systems that change how life is run.

**📎 琐事**: warranty ping-pong, small refunds, routine errands, kids' recurring activities unless a decision/deadline hinges on it, exploratory one-offs.

Borderline: household saga with significant money, safety, or multi-day blockage → *decision* under 重要, *noise* under 琐事 (or omit from Highlight).

**B. People (owner's lens)** — one `### [[Name]]` for every family hub person, owner first. Write as the owner ("helped [[Alex]] start X"), never as that person ("I aced the quiz"). 重要 only. Quiet week → one-line stub + the standing plan. Template is in [reference.md](reference.md).

**C. Goals (ladder + plan gate)** — list each important goal (from compass + this week's 重要 threads + person hubs). For each:

| Field | What to fill |
|---|---|
| **Long-term parent** | 3–5yr item / year theme / MyMemory big care it serves |
| **Short-term trace** | Quarter PRIMARY/commitment or this-week move that traces it |
| **Progress** | `moved` / `stalled` / `not started` / `done` + one evidence line from the dailies |
| **Plan** | Existing concrete next action, or `⚠️ drafted:` + one this-week action |

A goal **has a plan** only if a concrete next action exists (project `#task`, quarterly checkbox, person-note next step, or dated 本周重点 line) — restating the goal is not a plan. If missing: draft one next action (this week if possible), `[[wikilink]]` a note, and park it on current-week 本周重点. Do **not** create a `Projects/Doing/` folder (that's `/project-mgr`) unless the user asks.

An activity with no long-term parent is 琐事, or a new important goal that needs naming — don't leave it unparented in the Goals table.

Present **three tables** in chat (People / Goals / Threads 重要+琐事) before writing, unless the user said "just do it." Flag every `⚠️ drafted` plan for confirmation.

### Step 3: Fill in the past week's retrospective

Read `past_week.weekly_file`. Expected shape (People / Goals may be missing on older notes — insert them):

```
## ✨ Highlight
## 📋 本周重点
## 👥 家人
## 🎯 Goals
## 🎉 Wins
## 🚧 Challenges
## 💡 Lessons
## 📅 下周计划
```

Write:

- **✨ Highlight** — one line from **重要 only**. Never lead with 琐事.
- **📋 本周重点** — check off (`- [x]`) what that week's intentions actually got done; leave unchecked what didn't. Optionally append a short outcome note.
- **👥 家人** — Step 2B. Insert the heading before `## 🎉 Wins` if missing.
- **🎯 Goals** — Step 2C table. Insert before `## 🎉 Wins` (after 家人) if missing. Every row must have a Plan cell — never leave it blank.
- **🎉 Wins** / **🚧 Challenges** — `### 🎯 重要` then `### 📎 琐事`. Keep 琐事 to ≤2–3 bullets total across both; omit pure noise.
- **💡 Lessons** — 1–3 bullets, **重要 takeaways only**.
- **📅 下周计划** — same open items as Step 4, split 🎯 / 📎（有截止才跟）. Include every `⚠️ drafted` plan under 🎯.

Prefer `Edit`. If it fails on punctuation drift, or the heading is missing:

```bash
python3 "$SKILL_DIR/scripts/replace_section.py" \
  --file "<past_week.weekly_file>" \
  --heading "## 👥 家人" \
  --insert-before "## 🎉 Wins" \
  --body $'### [[Name]]\n- **This week:** …'
```

Repeat per section. Use `--insert-before` only when the heading does not yet exist (`## 👥 家人` and `## 🎯 Goals` both insert before `## 🎉 Wins` — insert 家人 first, then Goals).

### Step 4: Roll open items into the current week

Read `current_week.weekly_file`. Fill `📋 本周重点` with unresolved **重要** threads **and every drafted/existing goal plan that is still open**, sorted by urgency:

- `### 🔴 紧急` — near-term deadline or actively blocking (琐事 only if hard deadline ≤ ~7 days)
- `### 🟠 本周` — should get done this week (**重要** only, unless a 琐事 has a clear this-week action)
- `### 🟡 跟进` — longer-horizon, waiting on someone else, or 琐事 with a soft/far deadline

Each item: one line, `[[wikilink]]` if a project/person note exists. Same `Edit` / `replace_section.py` fallback as Step 3.

Do **not** roll forward resolved 琐事 or open 琐事 with no deadline and no leverage.

### Step 5: Bump frontmatter timestamps

For both files, set `updated:` to now:

```bash
date "+%Y-%m-%dT%H:%M"
```

### Step 6: Report

Summarize in chat: Highlight; people with a notable move vs quiet stubs; goals moved/stalled and any `⚠️ drafted` plans now sitting on this week's 本周重点; what else rolled forward. Don't re-paste the full files.

## Example Invocations

```
/review-week
```
→ Reviews dailies, fills last week's People / Goals / Wins/Challenges (重要/琐事), drafts missing plans, populates this week's 📋 本周重点.

```
review my past week
```
→ Same, as natural language.

```
/review-week just do it
```
→ Skip the pre-write tables; write directly (still draft missing plans).

## Output

Two weekly notes updated in place:

- Past week — Highlight (重要), checked-off 本周重点, 👥 家人, 🎯 Goals (every important goal has a Plan), Wins/Challenges/下周计划 with 🎯/📎 subsections, Lessons
- Current week — 📋 本周重点 populated with rolled-forward open items **plus drafted goal plans**, 重要-biased, by urgency

## Requirements

- Obsidian vault using `Journals/YYYY/YYYY-WNN.md` + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md`
- Each weekly note has `journal-start-date` / `journal-end-date` frontmatter
- `python3` for both helper scripts
- Optional compass (expected): `Family/<Name>/AI Memory/MyMemory.md`, Self-Operating Manual, `Journals/YYYY/YYYY-QN.md`
- Optional family hubs: `Family/*.md` (top-level). If `Family/` is missing, skip 👥 家人 and still do Goals + threads.

## Skill Structure

```
review-week/
├── SKILL.md
├── README.md
├── reference.md
└── scripts/
    ├── find_week_files.py
    └── replace_section.py
```
