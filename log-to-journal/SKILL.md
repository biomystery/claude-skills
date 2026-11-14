---
name: log-to-journal
description: Appends a thin, timestamped record to today's Obsidian daily journal — time-first (prefer start–end), either a one-line outcome or a `scope:` headline plus one thin action sub-bullet with [[wikilinks]]/PR links (never restating spoke bodies), optional short inspiration lines — and handles path resolution, reverse-chronological insert, linter races, and Unicode-safe fallbacks. Also supports `/log-to-journal simplify` to rewrite fat entries in today's daily note into thin timeline pointers in place. Use when the user says "log this", "add to journal", "记录到 journal", "simplify" (journal), or after meaningful work that should leave a timeline pointer (not a full archive dump).
user-invocable: true
---

# Log to Journal

Appends one **thin** timestamped entry to the user's Obsidian **daily journal**. The daily note is a **timeline / index**, not the archive — durable detail lives in hub/spoke notes; the journal points at them with time + a one-line outcome. Resolves `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`, inserts reverse-chronologically, bumps `updated:`, and falls back to a UTF-8-safe inserter when `Edit` fails.

**Modes:** default = append one thin entry; **`simplify`** = rewrite fat entries already in today's journal into thin pointers (no new timestamp).

## When to Use

- The user just did something worth recording: a decision, purchase, booking, errand, fix, or research result
- The user explicitly says "log this", "add to journal", "记录到 journal"
- The user says `/log-to-journal simplify`, "simplify journal", or "thin today's journal" → run **Mode: simplify** (below), not append
- You finished a task and the vault's CLAUDE.md asks you to proactively log meaningful work
- A short inspiration / thought should be captured without opening a new note

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| **Journal = timeline pointer, not archive** | Restating spoke content bloats dailies and makes weekly review expensive |
| **Time comes FIRST**: `08:02 …` or `08:02–08:40 …` — never emoji-before-time | Vault sort key; prefer **start–end** when session length is known |
| **Thin by default** — don't restate spoke bodies; links carry detail | Scannable day; weekly review stays cheap |
| **Scoped work → split headline / action** — `HH:MM <emoji> <scope>:` on the top line; **one** thin action sub-bullet below (links OK) | Long one-liners with multiple PR/issue links are hard to scan in Live Preview |
| **If a `[[wikilink]]` exists (or you just created one), do not paste its body into the journal** | Single source of truth stays in the hub/spoke |
| **Nested sub-bullets stay thin** — at most **one** action/money/next-action line. Never nested lists of content that belongs in a spoke | #35 ban on encyclopedic dumps still stands; scope:/action is not a license to dump |
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
| Who / what + outcome thinly + links (single line **or** `scope:` + one action line) | Background narrative, multi-bullet body, full lists (rules, findings, quotes) |
| Optional: amount, deadline, or next action on that same thin action line | Re-stating anything already written under a `[[wikilink]]` |
| Inspiration / open question in 1–2 lines | Meeting-minutes or analysis-novel under Life/Work |

**Division of labor:** write or update the hub/spoke **first** when detail must persist → then log a thin pointer with time + links. If there is no note yet and detail is large, create a minimal spoke and link it — don't expand the journal entry.

## Mode: simplify

Triggered by `/log-to-journal simplify` (also: `simplify`, `simplify journal`, `thin today's journal`). **Do not append a new entry.** Rewrite fat bullets already in **today's** daily note so they match the thin rules above.

### Simplify steps

1. **Resolve** today's journal path (same Step 0 as append). Stop if missing.
2. **Re-read** the full file immediately before editing.
3. **Scope:** only `## 🏠 Life`, `## 💼 Work`, and `## 📖 Study`. Leave Highlight, Tasks, inbox, templates, and other sections untouched.
4. **Walk top-level timestamp bullets** (`- HH:MM` or `- HH:MM–HH:MM`). For each entry (headline + its nested sub-bullets), decide:
   - **Already thin** → leave unchanged (still eligible for step 7 consolidate).
   - **Fat** → rewrite in place using the same timestamp (and emoji if present).
5. **What counts as fat** (any one is enough):
   - Mega-line: scope + long action / many clauses packed onto the timestamp line
   - Encyclopedic dump: 2+ nested sub-bullets of background, lists, rules, findings, or spoke body
   - Restates content that a `[[wikilink]]` on the line already covers
   - Nested depth beyond one action/money/next-action line (except the consolidate form in step 7)
6. **Rewrite targets** (pick the thinnest fit):
   - Clear project/person/domain → pattern **B**: `HH:MM <emoji> <scope>:` + **one** tab-indented action line (keep important `[[wikilinks]]`, PR links, key figures)
   - Single outcome / one primary link → pattern **A**: one thin line
   - Money / next action only → pattern **C**
   - Collapse multi-bullet dumps to one pointer line; **do not** invent a new spoke — if detail has nowhere to live, keep the single most important outcome + existing links only
7. **Consolidate same primary link/scope** (after thinning): when **2+** top-level bullets in a section share the same primary `[[wikilink]]` (or the same clear scope label, e.g. `3d-printing`), merge them into **one** block:
   - Headline: `HH:MM–HH:MM <emoji> [[Spoke]]:` (or scope label) using earliest–latest edit times in that group
   - Sub-bullets: **one thin line per original edit**, each starting with its own `HH:MM` (reverse-chron within the group)
   - Split mixed bullets first if needed (e.g. repo push stays under `3d-printing:`; knowledge-base prose moves under the spoke)
   - Do **not** flatten distinct timestamps into a single undated line; do **not** merge unrelated subjects that merely share an emoji
8. **Preserve:** meaning/outcome; existing wikilinks and critical numbers; section placement. Re-sort the section reverse-chron by each top-level headline’s **end** time after consolidate. Do **not** delete outcomes; do **not** move detail into new notes unless the user asked.
9. **Bump** frontmatter `updated:` (`date "+%Y-%m-%dT%H:%M"`).
10. **Report:** thinned count, consolidated groups (with the new range headlines), left alone; show only changed one-liners (not the whole file). If nothing needed work: say so and stop.

### Consolidate example

```markdown
- 10:55–16:40 📚 [[Projects/Doing/26_AD5X_3D_Printing/3D Printing 知识库]]:
	- 16:40 省料实测表 + 用料饼图
	- 15:58 示意图/阈值更正被覆盖 → 重写 + Changelog
	- 15:51 加示意图；更正支撑阈值角度
	- 10:55 新建知识库（参数取自蝠鲼实机档案）
```

### Simplify anti-patterns

| Don't | Do |
|---|---|
| Append a new `HH:MM … simplify` bullet | Edit/consolidate existing bullets only |
| Strip every sub-bullet blindly | Keep **one** thin action per *edit*; consolidate groups may have many timestamped lines |
| Drop `[[wikilinks]]` or key `$` / durations to "shorten" | Keep links and critical figures; cut narrative |
| Merge unrelated topics that share an emoji | Group only by primary `[[wikilink]]` / same scope label |
| Collapse several edits into one undated sub-bullet | Keep each edit’s `HH:MM` on its own sub-line |
| "Simplify" Highlight / Tasks / non-journal sections | Life / Work / Study only |

## Instructions (append mode)

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

Pick the shape by how link-heavy the action is:

**A. Tiny / single-link (one line is fine):**

```markdown
- HH:MM <emoji> <one-line outcome> [[Spoke Or Hub]]
- HH:MM–HH:MM <emoji> <one-line outcome> → [[Spoke]]
```

**B. Scoped session with links / multi-item action (preferred when a project/repo/person is clear):**

```markdown
- HH:MM–HH:MM <emoji> <scope>:
	- <verb> [PR #N](url) <short title> + [PR #M](url) <short title> (#issue)
```

Example:

```markdown
- 09:24–09:48 🛠️ claude-skills:
	- merged [PR #34](https://github.com/biomystery/claude-skills/pull/34) review-week Honest suggestions + [PR #36](https://github.com/biomystery/claude-skills/pull/36) log-to-journal thin records (#35)
```

- Headline = time + emoji + **scope label ending in `:`** only (repo, project, person, domain) — no action verbs on this line.
- Sub-bullet = **one** thin action line (links OK). Still no background / lists / spoke body.

**C. Money / next action only** (still one thin sub-bullet):

```markdown
- 14:44 🛒 HD 购入新热水器 [[Home/Water Heater]]
	- Rheem 50gal **$1,054.87** · next: book plumber
```

**D. Inspiration** (no forced project structure):

```markdown
- 22:15 💡 Idea: career floor = 20-min Tue/Thu block before deep work
```

#### Anti-pattern → fix

❌ Mega-line packing scope + action + many links onto the timestamp line:

```markdown
- 09:24–09:48 🛠️ claude-skills: merged [PR #34](...) … + [PR #36](...) …
```

✅ Scope headline + thin action sub-bullet (pattern B above).

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

or with a clear scope:

```markdown
- 20:10–20:40 🎒 [[April]]:
	- LEVEL UP 复盘 + 准则卡 [[How to Level Up at School]]
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

```
/log-to-journal simplify
```
→ No new bullet. Thin fat Life/Work/Study entries, then consolidate same-`[[wikilink]]` edits into one range + timestamped sub-lines; report what changed.

## Output

**Append mode:** one thin timestamped bullet (optional 1 short sub-bullet) in today's `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`, with `updated:` bumped.

**Simplify mode:** in-place thinned + consolidated bullets in that same file; report counts + the new range/one-liners only.

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
