# review-week

Review the past week's Obsidian daily journal entries, synthesize them into last week's weekly-note retrospective (Wins / Challenges / Lessons), **split 重要 vs 琐事**, write a **per-person family section from the vault owner's perspective**, check **primary-goal progress** on a long-term → short-term ladder, **draft a plan for any important goal that lacks one**, add **Honest suggestions** on personal-OS / focus / time-use levers, and roll only the still-open threads (plus drafted plans) into the current week's priorities. Built for `Journals/YYYY/YYYY-WNN.md` + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md`.

## What It Does

- Resolves past-week and current-week notes from **frontmatter dates**, not a guessed week number — handles vaults where Sun–Sat weeks are numbered by the ISO week of the Monday inside them
- Reads every daily note in range, plus the goal compass (Self-Operating Manual, yearly/quarterly notes, MyMemory) and top-level `Family/*.md` hub notes
- Groups entries by **thread/project** across days, labels each **🎯 重要** or **📎 琐事**, and marks resolved vs still-open
- Writes **👥 家人**: one subsection per family hub person, in the owner's voice (how I showed up for them — quiet weeks still get a stub)
- Writes **🎯 Goals**: every important goal with long-term parent, short-term trace, this week's progress, and a Plan cell — drafts a next action when none exists
- Writes Highlight / checked-off intentions / Wins / Challenges / 下周计划 / Lessons (重要·琐事 split)
- Writes **🪞 Honest suggestions**: evidence-based levers on focus, time use, and personal-OS friction (PRIMARY starved by deep work, zombie rolls, hub sprawl, etc.) — pick 1–2 to try next week
- Writes **⏱️ 时间去向 & MITs**: time by domain from explicit timed entries (with [[YYYY-MM-DD]] citations, never estimated), plus exactly 3 MITs for next week tied to open important threads/goals
- Populates the current week's priorities with unresolved 重要 items **and drafted goal plans**, sorted by urgency (🔴 / 🟠 / 🟡)
- Inserts missing People/Goals/Honest headings on older weekly notes; falls back to a Unicode-safe section-replace script when curly quotes or CJK punctuation defeat `Edit`

## Workflow

```mermaid
flowchart TD
    start(["/review-week"])
    resolve["find_week_files.py\nresolve past + current\nweekly notes from\nfrontmatter dates"]
    readdaily["Read dailies + compass\n+ Family/*.md hubs"]
    synth["Four cuts:\nthreads 重要/琐事\npeople owner's lens\ngoals ladder + plan gate\nhonest OS suggestions"]
    present["Present tables +\nHonest outline"]
    fillpast["Fill past week:\nHighlight · 家人 · Goals\nWins / Challenges / Lessons\nHonest suggestions"]
    missing{"家人 / Goals / Honest\nheading exists?"}
    insert["replace_section.py\n--insert-before Wins\nor 下周计划"]
    editok1{Edit matched?}
    fallback1["replace_section.py\n(Unicode-safe)"]
    fillcurrent["Fill current 本周重点\nopen 重要 + drafted plans"]
    editok2{Edit matched?}
    fallback2["replace_section.py\n(Unicode-safe)"]
    stamp["Bump updated:\non both files"]
    done(["Done\nreport Highlight, people,\ngoals, drafted plans,\nHonest headlines"])

    start --> resolve --> readdaily --> synth --> present --> fillpast --> missing
    missing -->|No| insert --> editok1
    missing -->|Yes| editok1
    editok1 -->|Yes| fillcurrent
    editok1 -->|No| fallback1 --> fillcurrent
    fillcurrent --> editok2
    editok2 -->|Yes| stamp
    editok2 -->|No| fallback2 --> stamp
    stamp --> done
```

## Install

```bash
git clone https://github.com/biomystery/claude-skills.git
ln -s "$(pwd)/claude-skills/review-week" ~/.claude/skills/review-week
```

Restart Claude Code — `/review-week` becomes available.

## Usage

```
/review-week
review my past week
close out this week and carry open tasks forward
/review-week just do it
```

## Output

**Sample** (illustrative, fictional values) — past week's weekly note gains:

```markdown
## ✨ Highlight
Locked the job search down to one primary track; closed out a stalled interview thread.

## 👥 家人

### [[Jordan]]
- **This week:** sent 2 Director apps; profile still unrevised
- **Primary:** next-role leap
- **Progress:** stalled — below the 3–5/week cadence
- **Plan:** 3 targeted apps + profile Step 0 this week [[job-search]]

### [[Alex]]
- **This week:** read the grade-9 counseling deck with them
- **Primary:** freshman landing — study skills
- **Progress:** moved (info gathered, no practice loop yet)
- **Plan:** ⚠️ drafted: Sun 20-min planning block

## 🎯 Goals

Guided by: [[Self-Operating Manual]] 3–5yr → [[YYYY-Q3]] PRIMARY → this week's traces.

| Goal | Long-term parent | Short-term trace | This week | Plan |
|---|---|---|---|---|
| Next role | career leap | 3–5 apps/week | stalled (2 apps) | 3 targeted apps this week [[job-search]] |
| Freshman study skills | family rhythm | counseling deck → practice loop | moved (deck read) | ⚠️ drafted: Sun 20-min planning block |

## 🎉 Wins

### 🎯 重要
- Narrowed job search to a single primary track
- Bank funding minimum met for a signup bonus

### 📎 琐事
- Vendor issued a $500 store credit after a failed appliance swap

## 🪞 Honest suggestions
> Levers, not blame. Pick 1–2 next week.

### 1. Deep craft crowding out PRIMARY
Deck work shipped; apps/week still 0.
- **试：** One app before opening the analysis folder each evening

### 2. One-line diagnosis
Strong on hard-problem ops; weak on a non-negotiable daily PRIMARY dose.

## ⏱️ 时间去向 & MITs

### 时间去向（本周已记录）
> 注：仅统计日记中明确标注开始/结束时间的条目。总计不代表总工作时长。

- **Deep work**: ~12h ([[2026-11-10]], [[2026-11-12]], [[2026-11-13]])
- **Meetings**: ~5h ([[2026-11-11]], [[2026-11-14]])
- **Admin**: ~3h ([[2026-11-11]], [[2026-11-15]])
- **Untraced entries**: 2 items 无时长 ([[2026-11-10]], [[2026-11-12]])

### 下周三件要事 (MITs)
1. **Send 3 targeted Director apps** — from [[job-search]] plan ([[2026-W45]]), 🔴 urgent
2. **Sun 20-min planning block with [[Alex]]** — drafted plan ([[2026-W45]] Goals), 🟠 this week
3. **Complete profile revision** — from job-search thread ([[2026-11-13]]), 🟠 this week
```

...and the current week's note gains:

```markdown
## 📋 本周重点

### 🔴 紧急
- [ ] Confirm the rescheduled appointment happens on the new date

### 🟠 本周
- [ ] Send 3 targeted Director apps [[job-search]]
- [ ] Sun 20-min planning block with [[Alex]]

### 🟡 跟进
- [ ] Tax form (~auto-extended) — consider CPA
```

## Requirements

- Obsidian vault using `Journals/YYYY/YYYY-WNN.md` + `Journals/YYYY/YYYY-WNN/YYYY-MM-DD.md`
- Each weekly note has `journal-start-date` / `journal-end-date` frontmatter
- `python3`
- Optional compass: `Family/<Name>/AI Memory/MyMemory.md`, Self-Operating Manual, quarterly note
- Optional family hubs: top-level `Family/*.md`

## Supported inputs / edge cases

| Situation | Handling |
|---|---|
| Week numbered by Monday's ISO week but note spans Sun–Sat | `find_week_files.py` reads frontmatter date ranges instead of computing a week number |
| Review runs Saturday evening before week ends | Use `--closing-current` flag: today's week becomes past_week (to close), next week becomes current_week |
| No earlier weekly note exists | Stop and tell the user, or offer current-week-only rollup |
| `Family/` missing | Skip 👥 家人; still write Goals + threads |
| Older weekly note has no 家人 / Goals heading | `replace_section.py --insert-before "## 🎉 Wins"` |
| Older weekly note has no Time & MITs heading | `replace_section.py --insert-before "## 📅 下周计划"` |
| `Edit` can't match template placeholder text (curly quotes, CJK) | `replace_section.py` does a boundary-based, UTF-8-safe section replace |
| Weekly file rewritten by linter mid-edit | Re-read, then edit |
| A thread already resolved during the week | Goes into Wins/Challenges, not into the current week's open items |
| Important goal with no next action | Draft one this-week action; flag `⚠️ drafted`; put it on current 本周重点. Do not auto-create a project folder |
| Older weekly note has no Honest suggestions heading | `replace_section.py --insert-before "## ⏱️ 时间去向 & MITs"` (or before `## 📅 下周计划` if Time section also missing) |
| Honest suggestion with no evidence this week | Skip that heuristic — do not pad with generic advice |
| Daily entries have no explicit start/end times | Time domain shows 无记录; entries without duration listed as 无时长; never estimate |
| Household saga with money + lots of chat noise | Decision/outcome → 重要; ping-pong → 琐事 (or omit from Highlight) |
| Open 琐事 with no deadline | Do not roll forward |
| Person hub contains IDs / DOB / medical details | Link `[[Name]]` only; never copy those fields into the weekly note |

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
