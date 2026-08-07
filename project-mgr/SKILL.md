---
name: project-mgr
description: Builds an active Obsidian project note from a one-line goal under Projects/Doing/ — success criteria, workstreams, #task next actions, cross-links, and a daily-journal announcement. Use when the user says "build a project", "start a project", "project for <goal>", or gives a goal that needs agent-collaborative tracking in the vault (not a Microsoft To Do errand).
user-invocable: true
---

# Project Mgr

Turns a one-line **goal** into a durable Obsidian project under `Projects/Doing/`, following the vault's GTD split (agent work → Obsidian; solo errands → Microsoft To Do). Writes success criteria, workstreams, opt-in `#task` next actions, open questions, and related links — then announces the project in today's daily journal.

## When to Use

- User gives a goal that needs multi-step agent collaboration ("publish X", "renew Y", "resolve Z")
- User says "build a project", "start a project", `/project-mgr`, or "project for \<goal\>"
- A backlog item has grown big enough to leave `Dashboard/Backlog.md` and become its own folder

**Do not use** for: one-shot errands, shopping lists, calendar reminders (those stay in Microsoft To Do), or software delivery that belongs in GitHub Issues / CCPM.

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| **Privacy first** — never invent or copy SSNs, account numbers, medical IDs, school IDs, passwords, full street addresses, or card numbers into the project note | Project notes are often linked and searched; minimize sensitive surface |
| When linking people: confirm the profile note **exists**, then append a Related `[[wikilink]]` only — do **not** open or copy profile body fields (DOB, IDs, school, medical, employers, balances) | Keeps PII in one place; cross-link ≠ scrape |
| Prefer `[[wikilinks]]` to people/entities over restating private profile fields | Avoids duplicating PII into every project |
| A checkbox is tracked **only** with `#task` (or if it lives in `Dashboard/Backlog.md`) | Bare `- [ ]` is plain markdown — not a todo |
| Put **outcome → next action** on `#task` lines; add `📅 YYYY-MM-DD` only for real deadlines | Undated tasks live in the next-actions pool |
| Do **not** fabricate deadlines, owners, costs, or facts | Unknowns stay as `—` or open questions |
| Re-read any vault file immediately before editing | iCloud / Obsidian linter rewrites files between read and write |
| Log via the **log-to-journal** skill (or its `scripts/journal_insert.py`) — do not reimplement journal insert logic here | One insert path; handles linter race + Unicode |

## Instructions

### Step 0: Resolve vault and gather the goal

```bash
VAULT="${VAULT_DIR:-$PWD}"
YEAR=$(date "+%Y")
YY=$(date "+%y")
NOW=$(date "+%Y-%m-%dT%H:%M")
```

Confirm `$VAULT` has `Projects/Doing/` and `Journals/`. If not, ask the user for the vault path.

Capture from the user (or the current message):
1. **Goal** — one sentence outcome
2. **Optional** — display names for `[[wikilinks]]`, hard deadline, out-of-scope notes, related existing notes

Optional "people involved" means **display names for wikilinks only** — not a prompt to open or scrape profile notes.

If the goal is clearly a solo errand ("buy milk", "pay bill"), stop and say it belongs in Microsoft To Do — do not create a project.

### Step 1: Deduplicate

Search before creating:

```bash
rg -il "<goal keywords>" "$VAULT/Projects/" "$VAULT/Dashboard/" 2>/dev/null | head -20
```

- If an active project already covers this goal → **update it** (refresh next actions / open questions) instead of duplicating; report the existing path.
  - If next actions or other user-visible content changed → also log a short journal bullet ("refreshed project …").
  - If nothing material changed → skip the journal.
- If a Done project exists and the user wants a sequel → create a new folder; link the old one under Related.

### Step 2: Name the project folder

Pattern: `Projects/Doing/<YY>_<Slug>/`

- `YY` = two-digit year (`date "+%y"`)
- `Slug` = short Title_Case or snake topic, no spaces (e.g. `26_Example_Comic`, `26_Appliance_Replacement`)

```bash
SLUG="<YY>_<Topic_Slug>"
PROJ_DIR="$VAULT/Projects/Doing/$SLUG"
PROJ_NOTE="$PROJ_DIR/$SLUG.md"
mkdir -p "$PROJ_DIR"
```

If `$PROJ_NOTE` already exists, treat as update mode (Step 1).

### Step 3: Write the project note

Create `$PROJ_NOTE` with this skeleton. Fill from the goal; leave unknowns as `—`.

```markdown
---
created: <NOW>
updated: <NOW>
tags:
  - project
status: doing
goal: <one-line goal>
---

# <Emoji> <Title>

> [!abstract] Goal
> **<goal>** — one sentence. Link people with [[wikilinks]] only; do not paste private profile fields.

## 🎯 Success criteria

| Criterion | How we know it's done | Status |
|---|---|---|
| <criterion> | <check> | next |

**Out of scope (for v1):** <bullets, or "—">

## 🗺️ Workstreams

| ID | What | Owner | Status | Depends |
|---|---|---|---|---|
| 1 | <phase> | [[Person]] or — | next | — |

## ✅ Next actions

- [ ] <outcome> → <concrete next action> #task [[<SLUG>]]
	- Done when: <one-line done criterion>

## ❓ Open questions

- <question>

## 📌 Decisions

| When | Decision | Why |
|---|---|---|
| — | — | — |

## 🕰️ Timeline

- **<YYYY-MM-DD>** — Project created; goal set

## 🔗 Related

- [[People or notes]]
```

**Status pills** in tables: `done` / `in progress` / `next` / `blocked` / `⚠ caveat`.

**Privacy when filling:**
- Link `[[Person]]` instead of embedding DOB, IDs, emails, phones, schools, employers, or balances
- If a fact is required to act (e.g. a case/receipt number the user already stated *for this* project), keep it — but do not scrape unrelated fields from profiles
- Sample / illustrative text in chat replies must stay fictional; never paste real vault PII into the skills repo or public docs

Seed **2–4** `#task` next actions that unblock progress. Prefer clarifying questions as open questions when the format/owner/deadline is unknown — do not invent them.

### Step 4: Cross-link related notes

For each person or entity central to the goal:

1. Confirm their profile note **exists** (path / wikilink resolve only — do not read the note body for fields to copy)
2. Append a Related bullet pointing at the project (wikilink with display text)
3. Bump that note's frontmatter `updated:`
4. Stubs via `[[Name]]` are fine when no profile exists yet

### Step 5: Log to today's journal

**Invoke the log-to-journal skill** (preferred). Pass a two-line entry; let that skill resolve the journal path, reverse-chron slot, linter race, and Unicode-safe insert. Do not reimplement those steps here.

Entry shape (log-to-journal rules):
- Headline = `HH:MM 📁 <short title>` only — no `→` or wikilink on the headline
- Details in tab-indented nested sub-bullets, e.g. `Created [[Projects/Doing/<SLUG>/<SLUG>|<Title>]] — goal: <one line>; next: <top next action>`
- Section: `## 🏠 Life` (default) or `## 💼 Work` if work-related
- If today's journal file is **missing**, stop and ask — do not invent a daily note unless the user confirms

### Step 6: Report

Reply with:
- Project path (wikilink)
- Goal + success criteria count
- The `#task` next actions seeded
- Open questions still blocking a fuller plan
- Anything skipped for privacy (e.g. "linked profile only; did not copy IDs")

## Example Invocations

```
/project-mgr publish Alex's first comic book
/project-mgr plan a backyard compost bin
/project-mgr close out the ExampleCo warranty claim for a dishwasher
```

## Output

- `Projects/Doing/<YY>_<Slug>/<YY>_<Slug>.md` — active project note
- Optional updates to related profile notes (Related links only)
- One daily-journal bullet announcing the project (creation always; updates only when content changed)

## Requirements

- Obsidian vault with `Projects/Doing/`, `Journals/YYYY/YYYY-WXX/`, and the `#task` / `Dashboard/Tasks.md` convention
- `date` with `%y` / `%V` support
- **log-to-journal** skill available (or its `scripts/journal_insert.py`) for reliable journal inserts

## Skill Structure

```
project-mgr/
├── SKILL.md
└── README.md
```
