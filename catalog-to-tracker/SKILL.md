---
name: catalog-to-tracker
description: Turns a reference catalog living in Obsidian tables (course skills, curriculum items, reading list, drill library) into a single-source-of-truth checkbox tracker, and wires selected items into a query-driven schedule page via a tag scheme. Use when the same item exists twice — once as a catalog row, once as a hand-copied scheduled checkbox — or when a catalog needs to become checkable and plannable.
user-invocable: true
---

# Catalog to Tracker

Converts a **catalog** (markdown tables of items) into a **tracker** (one checkbox per
item, grouped, in catalog order), folds any duplicated "scheduled items" section back
into it, and designs the **tag scheme** that lets a separate schedule page assemble
those items with Tasks-plugin queries.

The invariant this skill exists to establish: **one item, one checkbox, one place.**
Everything else — the weekly plan, the progress dashboard — is a *query*, never a copy.

> Related but different: `/hub-from-outline` **builds** the hub → module pages from an
> outline. This skill makes those module pages **checkable and schedulable**. They
> compose: scaffold with `/hub-from-outline`, then run this once the item lists exist.
> For goal-driven work with next actions use `/project-mgr` instead.

## Vocabulary

| Canonical | Is | Typical synonyms |
|---|---|---|
| **Catalog** | the full item list, in a module note | skill tree, syllabus, drill library, TOC |
| **Item** | one leaf with a stable ID | skill, lesson, exercise, chapter |
| **Stable ID** | short code that never changes (`A.1`, `BB.12`) | skill code, item number |
| **Tracker** | the catalog rewritten as checkboxes | progress list |
| **Schedule page** | assembled view built from queries | weekly plan, practice schedule |
| **Cycle** | the repeating plan window (`wk1…wk7`) | week, session, sprint |

## When to Use

- A module note has a catalog table *and* a separate hand-maintained list of scheduled
  items — the same item is checkable in two places and they have drifted
- A catalog needs to become checkable (progress tracking) without losing its structure
- A schedule/dashboard page should assemble items by query instead of by copy-paste
- Examples: kid's IXL/Khan skill plan, gym program, certification study plan, reading list

**Do not use** for: building the module pages themselves (`/hub-from-outline`), one-off
todo capture (the vault's backlog / `#task` convention), or catalogs with no stable IDs
— add IDs first, matching by title text is fragile.

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| **One item, one checkbox** — schedule pages query, never copy | Two checkboxes always diverge; the ✅ date lands on the wrong one |
| **Match items by stable ID, never by title** | Titles get reworded upstream; `S.4` does not |
| **Back up before rewriting, verify after** | No git inside most vaults; a bad regex silently eats rows |
| **Keep unscheduled items in the list, untagged** | The catalog is the menu; scheduling = adding a tag, not moving a line |
| **Fence example tasks in `_Template.md`** | An unfenced `- [ ] … #tag-wk1` in a template shows up as a real task in every query |
| **Scheduled state = day prefix + tag on the existing line** | Reversible, greppable, no second source |
| **Preserve trailing metadata verbatim** when merging (`✅ date`, score notes) | That history is the only record of what was actually done |
| **Document the tag scheme on the durable hub**, not the instance page | The scheme outlives this year's plan |
| Re-read vault files immediately before edit | iCloud/linter races rewrite files between read and edit |
| Bump frontmatter `updated:` on every touched file | Keeps vault metadata honest |

## Instructions

### Step 0: Map the system before touching anything

Read all three layers and state the duplication out loud before editing:

```bash
VAULT="${VAULT_DIR:-$PWD}"
TOPIC="<Folder/Path/To/Topic>"
ls -R "$VAULT/$TOPIC"
grep -rn "^## " "$VAULT/$TOPIC" --include="*.md" | sort -t: -k3 | uniq -c -f2 | sort -rn | head
```

Answer these before writing:
- Which note is the **hub** (durable, instance-agnostic) vs the **instance/track** page?
- Which section holds the **catalog** (`## Items`) and which the **duplicate** (`## Scheduled …`)?
- What is the **stable ID** pattern? (`[A-Z]+\.\d+` covers letter-group codes like `S.4`, `BB.12`)
- Which **queries** already exist (```tasks / ```dataview blocks) and what do they match on?

### Step 1: Back up (there is no git in the vault)

```bash
BK="/tmp/$(basename "$TOPIC" | tr ' ' '_')-backup"
mkdir -p "$BK" && cp "$VAULT/$TOPIC"/Modules/*.md "$BK"/
ls "$BK"
```

### Step 2: Dry-run the conversion

`scripts/table_to_tasks.py` rewrites the catalog section and folds the duplicate section
into it. Always `--dry-run` first and read the per-file counts.

```bash
SKILL_DIR="${SKILL_DIR:-$HOME/.claude/skills/catalog-to-tracker}"
python3 "$SKILL_DIR/scripts/table_to_tasks.py" \
  --file "$VAULT/$TOPIC/Modules/M01 Foo.md" \
  --file "$VAULT/$TOPIC/Modules/M02 Bar.md" \
  --items-heading "## Items" \
  --merge-heading "## 📅 Scheduled Practice" \
  --callout /tmp/items-callout.md \
  --dry-run
```

Output is `M01 Foo.md: 23 items, 12/12 merged`. **`merged` must read `N/N`.** Anything
less means the ID pattern missed lines — the script parks unmatched scheduled items under
a visible `### Scheduled — not found in catalog` bucket rather than dropping them, but
that heading in the result means fix the pattern and re-run from the backup.

What it produces per group row:

```markdown
### A. First group
- [x] Mon · [A.1 Scheduled and done](https://example.com/a1) (score 100) ✅ 2026-01-05 #plan-wk1
- [ ] Wed · [A.2 Scheduled, pending](https://example.com/a2) #plan-wk2
- [ ] [A.3 In the catalog, not scheduled](https://example.com/a3)
```

Write the `--callout` file first — the explainer pinned under the heading so a future
reader knows these checkboxes are load-bearing:

```markdown
> [!info] These checkboxes are the source of truth
> One line per item — tick it when it's done (add a score in parentheses if useful).
> A line tagged **`#<scheme>-wkN`** is scheduled into week N of [[<Schedule Page>]]; that
> page only *queries* these lines, so ticking it there or here updates the same task.
```

Drop `--dry-run` to write. Add `--backup-dir` to snapshot each file as it goes.

### Step 3: Verify against the backup — do not skip

```bash
python3 "$SKILL_DIR/scripts/verify_merge.py" \
  --backup "$BK" --current "$VAULT/$TOPIC/Modules"
```

Checks every ID survived, no ID now appears twice, no URL was lost, and reports how many
duplicate occurrences were merged per file. That merged count must equal the number of
scheduled items you had. Exit code 1 gates the rest of the workflow.

### Step 4: Design the tag scheme

This is the judgment-heavy step and the one worth slowing down for. The tag is what a
schedule page queries, so its shape decides what stays queryable a year from now.

**Shape:** `#<subject><cycle-id>-wk<N>` — e.g. `#ela26-wk3`, `#gym26-wk1`.

| Dimension | In the tag? | Why |
|---|---|---|
| Subject / domain | **Yes** | The one axis a query must never cross |
| Cycle id (school year, season, cohort) | **Yes** | Week numbers recycle; without it, next year's `wk1` collides with this year's. Old tags become the archive |
| Week / session number | **Yes** | It is the grouping the schedule page renders |
| **Level / grade / difficulty** | **No** | A fallback (easier) variant of the same item must share the tag, or a week's query breaks the moment someone drops a level. This is the most common mistake |
| **Person** | **No** | Already in the file path — pair the query with `path includes <Person folder>`. Lets another person reuse the same tag under their own folder |
| Status (done/pending) | **No** | That is the checkbox and the `✅` date |

Ask before committing to a scheme: *"When this item gets swapped for an easier or harder
variant, does the tag still hold?"* If no, the tag is over-specified.

Expect to rename at least once — the first scheme is usually over-specified.
`scripts/rename_tag.py` previews by default and only writes with `--write`:

```bash
python3 "$SKILL_DIR/scripts/rename_tag.py" \
  --path "$VAULT/$TOPIC" --old "oldtag-wk" --new "newtag-wk"            # preview
python3 "$SKILL_DIR/scripts/rename_tag.py" \
  --path "$VAULT/$TOPIC" --old "oldtag-wk" --new "newtag-wk" --write
```

It reports per-file hit counts, bumps `updated:` on changed files, and prints the
`grep` that must come back empty. Run that grep before moving on.

> Vault-wide `grep -r` over an iCloud-synced vault can take minutes and stall the turn.
> Scope it to the topic folder plus the journal year, not the vault root.

### Step 5: Wire the schedule page

Each cycle section on the schedule page is a query pair — tag **plus** a path guard:

````markdown
## Week 3 — <theme>

```tasks
description includes #ela26-wk3
path includes Family/<Person>
sort by description
```
````

And one live-progress query on the track/hub page:

````markdown
```tasks
description includes #ela26-wk
path includes Family/<Person>
done
sort by done reverse
```
````

Add a callout stating the page is an assembled view, not a source. Then confirm the
counts match what the tracker holds:

```bash
for w in 1 2 3 4 5 6 7; do
  n=$(grep -rn "^- \[.\].*#ela26-wk$w\$" --include="*.md" "$VAULT/$TOPIC" | grep -vc Template)
  echo "wk$w: $n"
done
```

### Step 6: Update the template — fence the examples

`_Template.md` must show the new item shape, but its example lines carry real-looking
tags. **Unfenced, they are indexed as live tasks and pollute every query.** Put them in
a fenced block and say why:

````markdown
Shape to copy (fenced so the template's own examples never appear in the queries):

```markdown
### A. Group name
- [x] Mon · [A.1 Scheduled and done](https://example.com/a1) (score 100) ✅ 2026-01-05 #ela26-wk1
- [ ] [A.2 In the catalog, not scheduled yet](https://example.com/a2)
```
````

### Step 7: Document the scheme on the hub

On the **durable hub** (not this year's page), add a `## Tag convention` section with:
the anatomy table, an explicit **"deliberately not in the tag"** list with the reasoning
from Step 4, the one-checkbox rule, and which tags the current schedule page queries.
Future-you will not re-derive this.

### Step 8: Log and report

Delegate the journal entry to `/log-to-journal` if the vault uses that habit. Report:
files converted, items per file, duplicates merged, the tag scheme chosen and what was
deliberately excluded from it, and where the backup lives.

## Gotchas

| Gotcha | Handling |
|---|---|
| Template example tasks appear in live queries | Fence them (Step 6) — code-fenced list items are not indexed by Obsidian |
| Scheduled line and catalog row have different titles | ID match wins; the catalog title is kept, so upstream reworded titles get normalized for free |
| Scheduled ID missing from the catalog | Lands in `### Scheduled — not found in catalog`, never dropped silently |
| Vault-wide `grep -r` hangs on iCloud | Scope to the topic folder; a background grep that outlives the turn should be stopped |
| `Edit` fails on lines with `·`, `→`, emoji or CJK | Do the edit in Python with explicit UTF-8 I/O instead of retrying |
| Linter rewrote the file between read and edit | Re-read immediately before editing |
| A `- [ ]` that is not meant to be a tracked todo | Vaults using an opt-in `#task` rule: these catalog checkboxes are progress marks, not agent tasks — do not tag them `#task` |

## Example Invocations

```
/catalog-to-tracker
```
→ Reads the current note's folder, finds catalog + duplicate section, proposes the plan

```
/catalog-to-tracker Family/Ana/Study/IXL --tag ela26
```
→ Converts that folder's module notes and wires `#ela26-wkN` into the schedule page

## Output

- Every module note's catalog section rewritten as grouped checkboxes, one per item,
  with previously-scheduled items merged in place (day prefix, tag, `✅` date preserved)
- The duplicate scheduled section deleted
- Schedule page queries switched to `tag + path` pairs
- `_Template.md` updated with fenced examples
- A `## Tag convention` section on the hub
- Backup directory retained until the user confirms

## Requirements

- Python 3 (stdlib only)
- Obsidian with the **Tasks** plugin for the query blocks (Dataview works with rewritten queries)
- Catalog items must carry a stable ID; add one first if they do not

## Skill Structure

```
catalog-to-tracker/
├── SKILL.md
├── README.md
└── scripts/
    ├── table_to_tasks.py   # catalog table -> grouped checkboxes, merge duplicate section
    ├── verify_merge.py     # post-conversion audit against the backup
    └── rename_tag.py       # preview/apply a tag-scheme rename across the folder
```
