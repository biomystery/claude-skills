---
name: session-to-skill
description: Abstracts a just-completed Claude Code task into a reusable, publishable skill by reconstructing the workflow from session context. Use immediately after finishing a non-trivial task — captures steps, tools, edge cases, and privacy risks without re-explanation.
user-invocable: true
---

# Session to Skill

Invoked right after finishing a task in Claude Code. Claude looks back at what it just did — the steps taken, tools used, decisions made, edge cases handled — and drafts a complete, publishable skill from that context. The user only needs to confirm the name, review the privacy check, and approve the push.

## When to Use

- You just finished a non-trivial task in Claude Code and want to capture the process
- The task involved a repeatable workflow that others (or your future self) could reuse
- Invoke this **before closing the session** — Claude needs the current context to reconstruct the workflow

## Instructions

### Step 1: Reconstruct the Workflow from Session Context

Do **not** ask the user to re-describe the task. Instead, look back at the current session and answer these questions from what you observed:

1. **What was the task?** Summarize in one sentence.
2. **What were the inputs?** (folder path, file type, URL, argument, etc.)
3. **What were the outputs?** (files written, data extracted, action taken)
4. **What were the key steps?** List them in order — include decision points (e.g., "if PDF has no text → skip"), fallback strategies, and special-case handling.
5. **What tools/CLIs were essential?** (e.g., `pdftotext`, `gh`, `ffmpeg`)
6. **What gotchas or lessons emerged?** (things that failed first, edge cases discovered, privacy risks encountered)
7. **Is a supporting script needed?** Create a file in `scripts/` if ANY of these apply:
   - The code is 15+ lines
   - It will be called more than once in the workflow
   - It's part of a validation/feedback loop
   - Complex argument composition makes it error-prone to type each time

   If it's a one-shot bash one-liner or simple install command, keep it inline. When in doubt, extract to a script — it saves tokens and ensures consistency across runs.

Present this reconstruction to the user as a brief outline and ask:
- Does this capture the workflow accurately?
- Any steps to add, remove, or reframe?
- Confirm the skill name (suggest one in `kebab-case`, verb-noun preferred)

### Step 2: Explore the Target Repository

If `--repo <url>` was passed, use that URL. Otherwise, ask the user: *"What is the URL of your skills repository?"* before proceeding.

```bash
REPO_URL=<url-from-above>
SKILLS_DIR="${SKILLS_REPO_DIR:-$HOME/projects/claude-skills}"

# Use existing clone if present, otherwise clone fresh
if [ -d "$SKILLS_DIR/.git" ]; then
  git -C "$SKILLS_DIR" pull
else
  git clone "$REPO_URL" "$SKILLS_DIR"
fi

git -C "$SKILLS_DIR" log --oneline -3 && ls "$SKILLS_DIR"
```

Read one existing skill to internalize conventions before writing:

```bash
head -60 "$SKILLS_DIR"/<any-existing-skill>/SKILL.md
```

### Step 3: Write SKILL.md

Create `$SKILLS_DIR/<skill-name>/SKILL.md`:

```markdown
---
name: <skill-name>
description: <one-line — be specific about input and output>
user-invocable: true
---

# <Title>

<2–3 sentence overview.>

## When to Use
- <trigger condition>

## Instructions

### Step 0: Prerequisites
### Step 1: ...
...
### Step N: Generate output / summarize

## Example Invocations

## Output

## Requirements

## Skill Structure
```

> If Step 1 question 7 determined a script is needed, add a `scripts/` subdirectory and list it under `## Skill Structure`:
> ```
> <skill-name>/
> ├── SKILL.md
> ├── README.md
> └── scripts/
>     └── <helper>.py
> ```

**Writing guidelines:**
- Instructions must be imperative and concrete — Claude executes them literally
- Include real bash commands with placeholders, not vague prose
- Use `#### Strategy A / B` sub-sections for branching paths
- Add reference tables for domain constants (standard deductions, API limits, etc.)
- Capture every lesson and edge case discovered during the original session

### Step 4: Write README.md

Create `$SKILLS_DIR/<skill-name>/README.md`:

```markdown
# <skill-name>

<one-paragraph description>

## What It Does
- bullet list

## Workflow
\`\`\`mermaid
flowchart TD
    ...
\`\`\`

## Install
## Usage
## Output
**Sample output** (illustrative values):  ← MUST be fictional
## Requirements
## Supported inputs / edge cases
## Skill Structure
```

#### Mermaid Diagram Rules

Always include a `flowchart TD` under `## Workflow`:
- Start: `(["/skill-name\n[args]"])`
- End: `(["Done\n..."])`
- Decisions: `{Question?}` with labeled edges `-->|Yes|` and `-->|No|`
- Parallel outputs: two branches both pointing to the end node
- Target 8–15 nodes — informative but not overwhelming
- Use `\n` inside node labels for line breaks

### Step 5: Privacy Review (REQUIRED — do before any git operation)

Scan every line of both files against this checklist:

| Risk | What to look for | Action |
|------|-----------------|--------|
| PII | Real names, emails, SSNs, phone numbers, addresses | Remove entirely |
| Real financial figures | Actual income, tax amounts, account numbers from any document processed in the session | Replace with round, fictional numbers |
| Credentials | API keys, tokens, passwords | Remove entirely |
| Identifying paths | `/Users/actual-username/...` | Replace with `~/Documents/...` |
| Org-specific details | Internal project names, proprietary system names | Generalize |

**For sample output tables**: use clearly fictional, round values (e.g., `$80,000`, `12.0%`, `42 rows`) — never copy figures from real documents processed during skill development.

> **If you accidentally commit real data**: a follow-up fix commit is NOT sufficient — sensitive data remains in git history. Recovery procedure:
> ```bash
> git reset --hard <last-clean-sha>   # erase leaking commits locally
> # rewrite files cleanly, then:
> git push --force origin main        # rewrite remote history
> ```

### Step 6: Update Repository README

Add a row to the skills table in `$SKILLS_DIR/README.md`:

```markdown
| [<skill-name>](<skill-name>/) | `/<skill-name>` | <one-line description> |
```

### Step 7: Single Clean Commit

```bash
cd "$SKILLS_DIR"
git add <skill-name>/ README.md
git status   # verify ONLY intended files are staged — nothing else
git commit -m "add <skill-name> skill

<2–3 sentence description>

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

Publish as **one commit**. Do not push an iterative series of "add / fix / fix privacy" commits. Resolve everything locally before pushing.

### Step 8: Verify and Report

```bash
git -C "$SKILLS_DIR" log --oneline -4
```

Report back:
- Skill name and slash command
- Commit SHA
- Files published
- Install command for the user

## Example Invocations

```
/session-to-skill
```
→ Immediately after finishing a task; Claude reconstructs the workflow from context

```
/session-to-skill --repo https://github.com/you/your-skills
```
→ Targets a specific skills repository

## Output

Two files committed to the target GitHub repository:
- `<skill-name>/SKILL.md` — the executable skill definition
- `<skill-name>/README.md` — user-facing docs with Mermaid workflow diagram

## Requirements

- **Git** with push access to the target skills repository
- Must be invoked **within the same Claude Code session** as the task being abstracted

## Skill Structure

```
session-to-skill/
├── SKILL.md    (this file)
└── README.md
```
