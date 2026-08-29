---
name: note-to-moc
description: Refactors one overgrown Obsidian note (500+ lines, or any note where the current status is buried and parallel threads are interleaved) into a compact MOC hub plus topic spoke notes grouped into subfolders — extracting by exact line range so verbatim content is never retyped, moving files with the Obsidian CLI so links rewrite themselves, recursing into any spoke that is still overgrown so it becomes a sub-hub of its own, and verifying zero content loss, zero broken links, and zero stranded notes. Use when a long-running note has become unreadable, not when building a new hub from an outline.
user-invocable: true
---

# Note to MOC

Takes a single note that grew past the point of usability and splits it into a **MOC hub**
(routing, status, next actions) plus **spoke notes** (one per durable topic), grouped into
subfolders that mirror how the note is actually read. When a spoke is itself too big, the
same process runs on it and it becomes a **sub-hub** — the refactor is recursive, with a
mechanical stopping rule and a depth ceiling.

The invariant this skill exists to protect: **nothing is retyped and nothing is lost.**
Spokes are built by slicing exact line ranges out of the original, so verbatim material —
quoted correspondence, legal language, clinical text, transcripts — arrives byte-identical.
Only hubs are written fresh, because routing is the one part that is genuinely new.

> Related but different: `/hub-from-outline` **builds** a hub and module pages from an
> outline you supply. This skill **rescues** a note that already exists and has overgrown.
> `/catalog-to-tracker` makes item lists checkable. They compose: rescue with this skill,
> then scaffold or track the result.

## Vocabulary

| Canonical | Is | Typical synonyms |
|---|---|---|
| **Hub / MOC** | short routing note: status, next actions, map | index, dashboard, map of content |
| **Spoke** | one topic's full detail, independently readable | subpage, child note, detail note |
| **Sub-hub** | a spoke promoted to a hub over its own spokes | nested MOC, second-level index |
| **Cluster** | a group of spokes that get read together | section, folder, track |
| **Depth** | hub = 1, its spokes = 2, a sub-hub's spokes = 3 | level, tier |
| **Hotspot** | a section far larger than its siblings | mega-section |
| **Verbatim block** | quoted source text that must not be reworded | evidence, transcript, excerpt |

## When to Use

- A note is 500+ lines, or any length where you scroll to find the current state
- The "Status" / "Current posture" section sits in the bottom half of the file
- Chronological updates are out of order, or newer decisions sit *below* older ones
- Two or more parallel threads (tracks, workstreams, counterparties) are interleaved by date
- Sibling notes in the same folder have competing "Status" sections that have drifted
- A spoke from an earlier refactor has since regrown past the split threshold

**Do not use** for: building new structure from an outline (`/hub-from-outline`), notes under
~300 lines that are merely untidy (reorder in place — splitting adds navigation cost for no
gain), or notes whose bulk is a single indivisible document (a contract, one transcript —
those are already a spoke; give them a hub *neighbour*, do not carve them up).

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| **Extract by line range; never retype verbatim content** | Retyping silently mutates quoted evidence. Slice it. |
| **Back up before the first write** | Every integrity check later diffs against this backup. |
| **Let the note's own structure choose the clusters** | Its existing section groupings already encode how it is read. An imposed taxonomy fights the reader. |
| **A hub holds no verbatim bulk** | The moment a hub carries a long quote, it stops being scannable and you are back where you started. This applies to sub-hubs too. |
| **Move and rename with the Obsidian CLI, never `mv`** | Obsidian's file manager rewrites every inbound link vault-wide. `mv` silently breaks them all, and nothing warns you. |
| **Verify content AND links after every structural step** | These fail independently and both fail silently. |
| **Never delete "superseded" content without confirming it exists elsewhere verbatim** | "This is obviously covered in the newer section" is how the one unique paragraph disappears. |
| **Recurse only after the current level verifies clean** | Splitting a spoke that is already wrong multiplies the error and buries its origin. |
| **Depth 3 is the ceiling; a deeper `SPLIT` means the parent split was wrong** | Past three levels the reader is traversing a tree, not reading notes. See Step 11. |
| **The root original is the only content-loss source of truth** | Per-level backups are undo, not evidence. Every level is checked against the note you started from. |
| **Spoke basenames must be unique vault-wide** | Two notes named `Background.md` make `[[Background]]` resolve by proximity — the hub and a spoke silently point at different notes. |

## Instructions

### Step 0: Prerequisites

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/note-to-moc/SKILL.md)")"
python3 --version                 # slicing + verification
obsidian help | grep -E "^  move" # Obsidian CLI, app must be RUNNING
```

If the `obsidian` CLI is unavailable, you can still do everything except Step 7 —
in that case move files **inside the Obsidian app** (drag in the file explorer), which
performs the same link rewriting. Never fall back to `mv`.

### Step 1: Diagnose before splitting

Do not split on length alone. Find out *how* it is broken:

```bash
python3 "$SKILL_DIR/scripts/measure_sections.py" "path/to/BigNote.md"
```

With `--diagnose-only`, print this report and the proposed split from Step 2, then **stop** —
write nothing, back up nothing.

The script flags `HOTSPOT` (outsized sections), `DENSE` (many bytes per line — mega-bullets
mixing claim and evidence), and `BURIED` (a status heading past the halfway mark), then
prints a `VERDICT`:

| Verdict | Means | Do |
|---|---|---|
| `SPLIT` | big enough, and has ≥3 top-level sections to split into | proceed |
| `INDIVISIBLE` | big but only one or two sections — one document, not a note | leave whole, give it a hub neighbour |
| `WATCH` | borderline | reorder in place; splitting costs more than it saves |
| `LEAVE` | healthy | stop |

The verdict is the mechanical stopping rule, including for recursion (Step 11). It is not a
substitute for reading the table yourself, which is where you see:

- **Broken chronology** — updates whose dates run backwards, or that sit after the status
- **Interleaved threads** — one topic's entries scattered among another's
- **Competing status** — grep sibling notes in the same folder for `^## Status`

Report the diagnosis to the user before touching anything. The split plan should answer the
diagnosis, not just the line count.

### Step 2: Choose clusters from the note's own shape

Look at the existing top-level headings and how they group. Most overgrown notes already
sort into three or four clusters, commonly:

| Cluster | Holds | Changes |
|---|---|---|
| **Foundation** | background, stable facts, reference data | rarely |
| **Threads** | one note per parallel track / counterparty / workstream | often |
| **Decisions** | chronological log, current plan, drafts | constantly |
| **Archive** | superseded material kept for the trail | never |

Confirm the cluster names and file split with the user before writing. Ask whether to keep
redundant filename prefixes (`Track 1 - X.md` inside `Tracks/`) — verbose names are often
preferred for search and graph legibility, so **do not strip prefixes unprompted**.

Before settling on names, check each planned filename against the whole vault. A collision
makes `[[Name]]` ambiguous forever after:

```bash
obsidian search query="Background" </dev/null   # or: find "$VAULT" -name "Background.md"
```

### Step 3: Back up

```bash
cd "<project folder>" && mkdir -p .backup && cp *.md .backup/
```

A leading-dot folder is not indexed by Obsidian, so the backup will not pollute search,
graph view, or link resolution.

### Step 4: Slice sections by exact line range

Get the heading line map, then cut. **Never retype.**

```python
lines = open(src, encoding="utf-8").read().split("\n")
def seg(a, b):                      # 1-indexed, inclusive
    return "\n".join(lines[a-1:b]).rstrip()

S = {"background": seg(15, 22), "timeline": seg(43, 76), ...}
```

Write each segment to a temp dir first and print a line/byte report, so you can confirm the
ranges landed on the right boundaries before assembling anything.

Sub-sections sometimes need splitting across two spokes. Prefer keeping a tightly-argued
block whole in one spoke and cross-linking to it. Fragmenting an argument to satisfy a
filing scheme costs more than the tidiness is worth.

### Step 5: Assemble the spokes

Each spoke gets: frontmatter, a title, a **breadcrumb back to its hub**, a status callout,
then the sliced sections joined by `---`.

```markdown
---
created: <original created>
updated: <today>
tags: [...]
---

# <Spoke title>

[[<Hub note>|← back to hub]]

> [!warning] Status: <one-line current state of this thread>
> <what a reader must know before acting on anything below>

---

<sliced content, verbatim>
```

The status callout at the top of each spoke is what makes the spoke independently readable.
Without it, a reader who lands on the spoke via search has no idea whether it is live or dead.

**At depth 3** (a sub-hub's spokes) the breadcrumb carries the whole chain, so a reader who
arrives by search can climb all the way out:

```markdown
[[<Root hub>]] › [[<Sub-hub>|← back]]
```

Write each spoke **directly into its destination folder**. New files have no inbound links
yet, so nothing needs rewriting — `obsidian move` (Step 7) is only for files that already
exist elsewhere in the vault.

### Step 6: Write the hub fresh

This is the only genuinely new writing. Target **under ~120 lines**:

1. One-paragraph plain-language summary
2. **Current posture** callout — the single most important thing, at the top
3. Cluster/thread status table, each row linking to its spoke
4. **Next actions**, numbered and prioritized
5. **Map** of every note, grouped by cluster, one line of "what's in here" each
6. Standing reference facts (IDs, dates, figures) in a table

The Map lists **every note in the tree, not just direct children**. A spoke that became a
sub-hub is marked as one and its own spokes sit indented beneath it, so the root hub stays
the single entry point no matter how deep the tree goes:

```markdown
- **[[Thread 2 - Vendor]]** — sub-hub: the vendor escalation, three phases
  - [[Vendor - Timeline]] — dated log of every contact
  - [[Vendor - Correspondence]] — letters sent and received, verbatim
```

Then fix anchors that were same-file and are now cross-file:

```bash
grep -n "\[\[#" *.md    # each hit needs [[Note#Heading]], or it silently dead-ends
```

Callout titles are **not** heading anchors. `[[Hub#Current posture]]` does not resolve to a
`> [!info] Current posture` callout — give the section a real heading if you link to it.

### Step 7: Move pre-existing notes into subfolders with the Obsidian CLI

> See the `obsidian-cli` skill for the full command surface. The commands that matter here
> are `move` (relocate/rename a file), `backlinks` (see who points at a note before you touch
> it), and `folders` (confirm the tree). The Obsidian app must be **running** — the CLI drives
> the live app, not the files on disk.

This step is for notes that **already existed** and have inbound links. Spokes you just
created in Step 5 were written straight into their folder and need nothing here.

**`obsidian move` operates on FILES ONLY.** Verified: passing a folder path returns
`Error: "<path>" is a folder, not a file.` So create the destination folders on disk first,
then move each note individually:

```bash
mkdir -p Foundation Threads Decisions Archive     # plain mkdir is fine; folders carry no links

mv_one() {   # $1 = source path relative to vault, $2 = destination folder
  obsidian vault="<VaultName>" move path="$1" to="$2" </dev/null
}
mv_one "<folder>/Thread 1 - Vendor.md"   "<folder>/Threads"
mv_one "<folder>/Decision Log.md"        "<folder>/Decisions"
```

Verified behaviour: moving a file this way rewrites inbound links across the whole vault.
A link written as `[[project/sub/Note|alias]]` becomes `[[Note|alias]]` after the move —
Obsidian normalises to the shortest unique form. That is correct; do not revert it.

Three gotchas, all hit in practice:

- **`</dev/null` is required** in loops. The `obsidian` CLI reads stdin, so a `while read`
  loop over a heredoc has its input consumed after the first iteration and the rest silently
  never run. Redirect stdin on every invocation.
- **Keep the hub where it is.** Notes elsewhere (daily journals, other projects) link to the
  hub; leaving it put means those links never need rewriting at all. Same for a spoke you
  promote to a sub-hub in Step 11 — it keeps its name and path, so its inbound links survive
  untouched.
- **To move or rename a whole folder**, do it **inside the Obsidian app** (drag in the file
  explorer, or right-click → Rename). The app performs the same link rewriting. There is no
  CLI equivalent. Never `mv` a folder.

To rename a note rather than relocate it, use `obsidian rename path="<path>" name="<new name>"`
— also file-only, also link-preserving.

### Step 8: Handle superseded sibling notes

When a sibling note duplicates the hub's status:

1. Merge its **unique** content into the right spoke or the decisions log
2. Replace merged sections with a pointer table (was-here → now-lives-here)
3. Keep genuinely unique material **verbatim in place** under an `## Archived` heading
4. Add a superseded banner naming which conclusions are now wrong and why

Do not delete the file. A superseded note with a banner is a useful record; a deleted note
is a hole in the reasoning trail.

### Step 9: Verify — content, links, and reachability

```bash
python3 "$SKILL_DIR/scripts/verify_refactor.py" \
  --original "<folder>/.backup/BigNote.md" \
  --original "<folder>/.backup/Sibling.md" \
  --new-dir  "<folder>" \
  --vault    "<VAULT ROOT>" \
  --hub      "<folder>/Overview.md"
```

`--new-dir` is walked recursively, so **one run covers the whole tree however deep it nests**.
Pass the *root* originals only — per-level backups are undo, not evidence.

`--vault` must be the **vault root** (the folder containing `.obsidian/`), not the project
subfolder. Passing the subfolder makes every vault-relative link look broken — a very
convincing false alarm. The script warns when `.obsidian/` is missing.

Three reports, each failing independently:

- **CONTENT** — every substantive original line still exists somewhere in the tree
- **LINKS** — broken targets and bad anchors (fatal); duplicate basenames (`ambiguous`,
  a warning — Obsidian resolves by proximity, but the hub and a spoke may now mean
  different notes by the same name)
- **REACH** — with `--hub`, every note reachable by following links from the hub. This is
  what catches a promoted sub-hub whose children were never wired into the map: the bytes
  survive, but nothing points at them.

Read the content misses one at a time. A line reported missing is either:

- **Rewritten on purpose** (the old Status became the hub's posture section) — fine, confirm and move on
- **Silently dropped** — a bug; restore it from `.backup/`

Both happen. Only a human can tell them apart, which is why this check reports rather than fails.

### Step 10: Fix hard-wrapped lines you introduced

**Obsidian renders a single newline as a line break.** If you hard-wrapped the prose you
wrote in Step 5/6 at ~80–110 characters, it renders with breaks mid-sentence. Most mature
vaults write one long line per paragraph.

Join wrapped lines in **content you authored**. Leave these alone — the breaks are intentional:

| Leave alone | Why |
|---|---|
| YAML frontmatter | line-per-key is the format |
| Tables, list items | structural |
| Letter/email signature blocks | visual line breaks are wanted |
| `**Bold label:**` ⏎ `body text` | a deliberate label-then-body pattern |
| `→ [[Link]]` pointer lines | meant to stand alone |

After joining a paragraph that sits directly above a list or table, **re-check the blank
line** between them — joining can consume it and the list will stop rendering.

### Step 11: Recurse into spokes that are still overgrown

Only once Step 9 is clean. Measure every spoke in one pass — use `find`, not a shell glob,
so depth-3 notes are included once a sub-hub exists:

```bash
find . -name '*.md' -not -path './.backup/*' -print0 \
  | xargs -0 python3 "$SKILL_DIR/scripts/measure_sections.py" --brief
```

With `--no-recurse`, print this verdict list, say which spokes would have been promoted, and
**stop**. Otherwise act on the verdicts: `SPLIT` → promote; `INDIVISIBLE` → leave whole; `WATCH`/`LEAVE` → stop.
Show the user the verdict list and confirm the promotions before writing — a hub that spawns
four sub-hubs at once is usually a sign the Step 2 clusters were too coarse, not that four
promotions are needed.

To promote spoke `<Cluster>/Thread 2 - Vendor.md`:

```bash
obsidian backlinks path="<Cluster>/Thread 2 - Vendor.md" </dev/null   # who points here
mkdir -p ".backup/<Cluster>" && cp "<Cluster>/Thread 2 - Vendor.md" ".backup/<Cluster>/"
mkdir -p "<Cluster>/Thread 2 - Vendor"          # children live in a folder beside the sub-hub
```

Then re-enter **Steps 1, 2, 4, 5 and 6 with the spoke as the source**: diagnose it, choose
its sub-clusters, slice it by line range, write its sub-spokes directly into the new folder
with a depth-3 breadcrumb, and rewrite the spoke itself as a sub-hub.

Four things that make recursion safe rather than a slow-motion mess:

| | |
|---|---|
| **The sub-hub keeps its filename and path** | Every inbound link — root hub, daily journals, other projects — still resolves. Nothing is moved, so nothing is rewritten. |
| **The root hub's Map gains the children, indented** | Otherwise the promotion hides content one click deeper with no sign it exists. The root hub's status row for the spoke does not change; it still points at the same note. |
| **The per-level backup is undo only** | Content is still verified against the root original in Step 9. Never swap `--original` to a spoke backup — that would let a level-1 loss pass unnoticed. |
| **Re-run Step 9 from the project root** | `--new-dir` walks recursively and `--hub` checks reachability, so one run re-verifies every level at once. Do not verify per level. |

**Depth 3 is the ceiling.** Hub → sub-hub → spoke is as far as a reader will follow. If a
depth-3 spoke still reports `SPLIT`, that is evidence the *level-1* cluster boundary was
wrong: the material belongs as its own top-level cluster, not as a great-grandchild. Go back
to Step 2 and re-cut, rather than adding a fourth level.

Recursion terminates when every note reports `WATCH`, `LEAVE`, or `INDIVISIBLE`.

### Step 12: Report

Give the user: line count before/after, the full file tree with depth marked, what each
cluster holds, which spokes were promoted to sub-hubs and why, the verification result, and
where the backup lives.

## Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Vault-wide `grep -r` hangs for minutes | iCloud/OneDrive-backed vault; every file is a network read | Use `os.walk` in Python with a skip-list, or scope to the project folder |
| `Edit` tool fails on a line that looks identical | Obsidian's linter reformatted it (table column padding) between read and edit | Re-read, then use a regex replace instead of exact-string |
| Link checker flags `[[Note#Heading\|alias]]` inside a table | The escaped pipe `\|` gets captured into the anchor | Strip a trailing `\` before comparing (the bundled script does) |
| Everything reported as a broken link | `--vault` pointed at the project folder | Pass the vault root |
| `Error: "..." is a folder, not a file` | `obsidian move` only accepts files | `mkdir` the destination, move notes one by one; move *folders* inside the app |
| Only the first file in a move loop actually moved | The CLI ate the loop's stdin | Add `</dev/null` to every `obsidian` call |
| Numbered list renders as one paragraph | The blank line above it was consumed while unwrapping | Reinsert the blank line |
| `[[Hub#Current posture]]` dead-ends | A callout title is not a heading anchor | Give the section a real `##` heading |
| Sub-spokes exist but nobody can find them | The sub-hub was written but the root hub's Map was never updated | Step 9's `REACH` check catches this; add the indented children |
| `[[Background]]` opens the wrong note | Two spokes share a basename; Obsidian resolves by proximity | Check names against the vault in Step 2; rename with `obsidian rename` |
| Recursion keeps finding `SPLIT` at depth 3 | The level-1 clusters were too coarse | Re-cut at Step 2 — do not add a fourth level |

## Example Invocations

```
/note-to-moc
```
→ Claude asks which note, diagnoses it, proposes clusters, and refactors on approval

```
/note-to-moc Projects/Doing/big-project/Everything.md
```
→ Diagnoses and refactors that note, then recurses into any spoke still reporting `SPLIT`

```
/note-to-moc --diagnose-only Research/Literature.md
```
→ Prints the size/structure report and a proposed split; writes nothing

```
/note-to-moc --no-recurse Projects/Doing/big-project/Everything.md
```
→ One level only; reports which spokes would have been promoted, and stops

## Output

- `<Hub>.md` — rewritten as a compact MOC (typically 10–20% of the original length)
- `<Cluster>/<Spoke>.md` — several spokes, each independently readable, content byte-identical to the original
- `<Cluster>/<Sub-hub>/` — where a spoke was promoted, its own spokes sit in a folder beside it
- `.backup/` — every touched file, pre-refactor, mirroring the tree
- A verification report: content misses reviewed, links and anchors resolving, every note reachable from the hub

## Requirements

- **Python 3** — section slicing and verification
- **Obsidian CLI** (`obsidian`) with the app **running** — link-preserving moves and renames (see the `obsidian-cli` skill). Optional only if you move files inside the app instead; `mv` is never an acceptable substitute.
- An Obsidian vault (the verifier locates the root by its `.obsidian/` directory)

## Skill Structure

```
note-to-moc/
├── SKILL.md
├── README.md
└── scripts/
    ├── measure_sections.py   # Steps 1 & 11 — diagnose; VERDICT drives recursion
    └── verify_refactor.py    # Step 9 — content-loss, link, and reachability checks
```
