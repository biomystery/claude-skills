---
name: note-to-moc
description: Refactors one overgrown Obsidian note (500+ lines, or any note where the current status is buried and parallel threads are interleaved) into a compact MOC hub plus topic spoke notes grouped into subfolders — extracting by exact line range so verbatim content is never retyped, moving files with the Obsidian CLI so links rewrite themselves, and verifying zero content loss and zero broken links. Use when a long-running note has become unreadable, not when building a new hub from an outline.
user-invocable: true
---

# Note to MOC

Takes a single note that grew past the point of usability and splits it into a **MOC hub**
(routing, status, next actions) plus **spoke notes** (one per durable topic), grouped into
subfolders that mirror how the note is actually read.

The invariant this skill exists to protect: **nothing is retyped and nothing is lost.**
Spokes are built by slicing exact line ranges out of the original, so verbatim material —
quoted correspondence, legal language, clinical text, transcripts — arrives byte-identical.
Only the hub is written fresh, because the hub is the one part that is genuinely new.

> Related but different: `/hub-from-outline` **builds** a hub and module pages from an
> outline you supply. This skill **rescues** a note that already exists and has overgrown.
> `/catalog-to-tracker` makes item lists checkable. They compose: rescue with this skill,
> then scaffold or track the result.

## Vocabulary

| Canonical | Is | Typical synonyms |
|---|---|---|
| **Hub / MOC** | short routing note: status, next actions, map | index, dashboard, map of content |
| **Spoke** | one topic's full detail, independently readable | subpage, child note, detail note |
| **Cluster** | a group of spokes that get read together | section, folder, track |
| **Hotspot** | a section far larger than its siblings | mega-section |
| **Verbatim block** | quoted source text that must not be reworded | evidence, transcript, excerpt |

## When to Use

- A note is 500+ lines, or any length where you scroll to find the current state
- The "Status" / "Current posture" section sits in the bottom half of the file
- Chronological updates are out of order, or newer decisions sit *below* older ones
- Two or more parallel threads (tracks, workstreams, counterparties) are interleaved by date
- Sibling notes in the same folder have competing "Status" sections that have drifted

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
| **The hub holds no verbatim bulk** | The moment a hub carries a long quote, it stops being scannable and you are back where you started. |
| **Move and rename with the Obsidian CLI, never `mv`** | Obsidian's file manager rewrites every inbound link vault-wide. `mv` silently breaks them all, and nothing warns you. |
| **Verify content AND links after every structural step** | These fail independently and both fail silently. |
| **Never delete "superseded" content without confirming it exists elsewhere verbatim** | "This is obviously covered in the newer section" is how the one unique paragraph disappears. |

## Instructions

### Step 0: Prerequisites

```bash
python3 --version                 # slicing + verification
obsidian help | grep -E "^  move" # Obsidian CLI, app must be RUNNING
```

If the `obsidian` CLI is unavailable, you can still do everything except Step 7 —
in that case move files **inside the Obsidian app** (drag in the file explorer), which
performs the same link rewriting. Never fall back to `mv`.

### Step 1: Diagnose before splitting

Do not split on length alone. Find out *how* it is broken:

```bash
python3 scripts/measure_sections.py "path/to/BigNote.md"
```

The script flags `HOTSPOT` (outsized sections), `DENSE` (many bytes per line — mega-bullets
mixing claim and evidence), and `BURIED` (a status heading past the halfway mark). Also read
the raw table yourself for:

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

Each spoke gets: frontmatter, a title, a **backlink to the hub**, a status callout, then the
sliced sections joined by `---`.

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

### Step 6: Write the hub fresh

This is the only genuinely new writing. Target **under ~120 lines**:

1. One-paragraph plain-language summary
2. **Current posture** callout — the single most important thing, at the top
3. Cluster/thread status table, each row linking to its spoke
4. **Next actions**, numbered and prioritized
5. **Map** of every note, grouped by cluster, one line of "what's in here" each
6. Standing reference facts (IDs, dates, figures) in a table

Then fix anchors that were same-file and are now cross-file:

```bash
grep -n "\[\[#" *.md    # each hit needs [[Note#Heading]], or it silently dead-ends
```

### Step 7: Move into subfolders with the Obsidian CLI

> See the `obsidian-cli` skill for the full command surface. The commands that matter here
> are `move` (relocate/rename a file) and `folders` (confirm the tree). The Obsidian app
> must be **running** — the CLI drives the live app, not the files on disk.

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
  hub; leaving it put means those links never need rewriting at all.
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

### Step 9: Verify — content and links

```bash
python3 scripts/verify_refactor.py \
  --original "<folder>/.backup/BigNote.md" \
  --original "<folder>/.backup/Sibling.md" \
  --new-dir  "<folder>" \
  --vault    "<VAULT ROOT>"
```

`--vault` must be the **vault root** (the folder containing `.obsidian/`), not the project
subfolder. Passing the subfolder makes every vault-relative link look broken — a very
convincing false alarm. The script warns when `.obsidian/` is missing.

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

### Step 11: Report

Give the user: line count before/after, the file tree, what each cluster holds, the
verification result, and where the backup lives.

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

## Example Invocations

```
/note-to-moc
```
→ Claude asks which note, diagnoses it, proposes clusters, and refactors on approval

```
/note-to-moc Projects/Doing/big-project/Everything.md
```
→ Diagnoses and refactors that note

```
/note-to-moc --diagnose-only Research/Literature.md
```
→ Prints the size/structure report and a proposed split; writes nothing

## Output

- `<Hub>.md` — rewritten as a compact MOC (typically 10–20% of the original length)
- `<Cluster>/<Spoke>.md` — several spokes, each independently readable, content byte-identical to the original
- `.backup/` — every touched file, pre-refactor
- A verification report: content misses reviewed, links and anchors resolving

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
    ├── measure_sections.py   # Step 1 — diagnose where the note is overgrown
    └── verify_refactor.py    # Step 9 — content-loss + broken-link verification
```
