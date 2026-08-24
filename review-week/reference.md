# review-week — compass globs, templates, plan heuristics

Read this in Step 1. Keep PII out of weekly notes: `[[wikilink]]` people; never copy IDs, DOB, account numbers, or medical details from hub notes.

## Contents

- Compass files (long-term first)
- Person section template (owner's lens)
- Goals table
- What counts as a plan
- Drafting a missing plan

## Compass files (long-term first)

Resolve `$YEAR` and quarter from today (`Q = ((month-1)//3)+1`). Skip any path that does not exist.

```bash
VAULT="${VAULT_DIR:-$PWD}"
YEAR=$(date "+%Y")
Q=$(( ($(date +%-m) - 1) / 3 + 1 ))

ls "$VAULT/Family/"*.md
ls "$VAULT"/Family/*/AI\ Memory/MyMemory.md
ls "$VAULT"/Family/*/AI\ Memory/Self-Operating\ Manual.md
ls "$VAULT/Journals/$YEAR/${YEAR}.md"
ls "$VAULT/Journals/$YEAR/${YEAR}-Q${Q}.md"
```

| Source | Role on the ladder |
|---|---|
| Self-Operating Manual (3–5 year items) | Long-term parent |
| `Journals/YYYY/YYYY.md` year theme | Long-term parent (if the note exists) |
| MyMemory — "big cares" + active family/career tracks | Long-term parent + 重要 classifier |
| `Journals/YYYY/YYYY-QN.md` 90-day PRIMARY + commitments | Short-term trace |
| Past week's `📋 本周重点` | Short-term trace (what was intended) |
| Person hub notes — active goals / next steps / deadlines only | Short-term trace per person |
| `Projects/Doing/` notes linked from the above | Where a plan often already lives |

MyMemory fallback path if not under `Family/<Name>/AI Memory/`: `AI Memory/MyMemory.md`, then `**/MyMemory.md`.

Owner = the `Family/<Name>/` folder that contains `AI Memory/`. Family roster = top-level `Family/*.md` basenames only (ignore nested school/activity notes).

## Person section template (owner's lens)

Always emit every hub person. Owner first, then MyMemory family-sentence order if present, else alphabetical.

```markdown
### [[Name]]
- **This week:** 1–2 lines of what *I* did or noticed (owner's voice)
- **Primary:** the 1–2 important goals that involve this person
- **Progress:** moved / stalled / not started / done — one evidence clause
- **Plan:** next action + when · `[[note]]` · or `⚠️ drafted: …`
```

Quiet week (no daily bullets about them, standing goal still open):

```markdown
### [[Name]]
- **This week:** quiet — no notable move
- **Primary:** <standing goal>
- **Progress:** stalled / not started
- **Plan:** <existing next action, or ⚠️ drafted>
```

**Owner's perspective — do / don't**

| Do | Don't |
|---|---|
| "Helped [[Alex]] start a 10-min study block; BTSN is Thursday." | "I finished my homework and felt great." (that's their diary) |
| "[[Sam]]'s night-guard claim still blocked — I call the insurer this week." | Copy member IDs, DOB, MRN, or claim numbers into the weekly note |
| Self section = *my* career/health/system goals in first person | Skip a person because the week was quiet |

Fictional example (not a real family):

```markdown
### [[Jordan]]
- **This week:** sent 2 Director apps; profile still unrevised
- **Primary:** next-role leap (quarter PRIMARY)
- **Progress:** stalled — volume below the 3–5/week cadence
- **Plan:** 3 targeted apps + profile Step 0 this week [[job-search]]

### [[Alex]]
- **This week:** read the grade-9 counseling deck with them; checked one club page
- **Primary:** freshman landing — study skills + one committed activity
- **Progress:** moved (info gathered, no practice loop yet)
- **Plan:** ⚠️ drafted: 20-min Sunday planning block — timer, homework list, when to ask for help
```

## Goals table

```markdown
Guided by: [[Self-Operating Manual]] 3–5yr → [[YYYY-QN]] PRIMARY → this week's traces.

| Goal | Long-term parent | Short-term trace | This week | Plan |
|---|---|---|---|---|
| Next role | career leap | Q PRIMARY: 3–5 apps/week | stalled (0 apps) | 3 targeted apps this week [[job-search]] |
| Freshman study skills | family rhythm | counseling deck → practice loop | moved (deck read) | ⚠️ drafted: Sun 20-min planning block |
```

Every important goal is a row. Every Plan cell is filled. 琐事 does not get a row.

## What counts as a plan

**Has a plan** — at least one concrete next action exists in any of:

- A `Projects/Doing/` note with an open `#task` or explicit next step
- An unchecked quarterly commitment that is an *action* ("send VRI follow-up"), not a restated goal ("get a new role")
- A person-hub next-step bullet with a verb
- A dated/urgent line already on a weekly 本周重点

**Does not have a plan**

- The goal restated ("improve study skills", "find next role")
- A project folder with all next actions checked or empty
- "Keep an eye on it" / "figure it out later"
- A wish with no owner-action this month

## Drafting a missing plan

One line, this week if possible:

`<verb> <object> — <when or deadline if real> [[note]]`

Examples (fictional): `Send 3 targeted apps this week [[job-search]]` · `Call the insurer re: coinsurance leftover [[claim-note]]` · `Sun 20-min planning block with [[Alex]]`

Then:

1. Put `⚠️ drafted: …` in the Goals Plan cell (and the matching person Plan line).
2. Put the same next action on **current-week** `📋 本周重点` (🔴 if ≤7-day deadline, else 🟠).
3. Do **not** create `Projects/Doing/` — `/project-mgr` is for that, and only if the user asks.
4. Do **not** invent deadlines. If timing is unknown, "this week" is enough.

If several important goals lack plans, draft all of them; don't stop after the first.
