---
name: create-skill
description: Author and publish a new reusable Claude Code skill to a GitHub repository. Guides the full lifecycle — from understanding the workflow to writing SKILL.md and README.md, privacy-checking all content, and pushing a single clean commit.
user-invocable: true
---

# Create Skill

Turns a repeatable Claude Code workflow into a shareable, installable skill. Handles authoring, privacy review, Mermaid diagram generation, and clean Git publishing — all in one pass.

## When to Use

- User has just completed a multi-step task and wants to capture it as a reusable skill
- User wants to publish a new skill to a Claude skills repository
- User describes a workflow they repeat often and wants to automate it as a slash command

## Instructions

### Step 1: Understand the Workflow to Encode

Ask the user (or infer from context) the following — do not proceed without answers to the first three:

1. **What does the skill do?** (one sentence)
2. **What is the input?** (folder path, URL, file, argument, etc.)
3. **What is the output?** (files written, summary printed, action taken)
4. **Does it need a supporting script?** — Only if the logic involves non-trivial computation (image processing, complex data transforms) that cannot be expressed as a sequence of CLI commands + Claude reasoning. If everything can be done with standard CLI tools and Claude's own Write/Edit/Bash tools, no script is needed.
5. **What is the target GitHub repo?** (default: check if a skills repo is already cloned in `/tmp` or ask)

### Step 2: Explore the Target Repository

Clone or update the skills repo:

```bash
# Check if already cloned
ls /tmp/claude-skills 2>/dev/null || git clone <repo_url> /tmp/claude-skills

# Get current state
cd /tmp/claude-skills && git pull && git log --oneline -3 && ls
```

Read one existing skill (`SKILL.md` + `README.md`) to internalize the conventions before writing:

```bash
cat /tmp/claude-skills/<any-existing-skill>/SKILL.md
```

### Step 3: Design the Skill Structure

Before writing any file, outline:

| Element | Decision |
|---------|----------|
| Skill name | kebab-case, verb-noun preferred (e.g., `tax-history-tracker`, `create-skill`) |
| User-invocable command | `/skill-name [args]` |
| Files needed | Always: `SKILL.md`, `README.md`. Optional: `scripts/` only if Step 1.4 says yes |
| Steps count | Aim for 5–10 numbered steps; each should be a concrete, testable action |

### Step 4: Write SKILL.md

Create `/tmp/claude-skills/<skill-name>/SKILL.md` with this structure:

```markdown
---
name: <skill-name>
description: <one-line description — shown in skill picker, be specific about input/output>
user-invocable: true
---

# <Title>

<2–3 sentence overview of what the skill does and why it's useful.>

## When to Use
- <trigger condition 1>
- <trigger condition 2>

## Instructions

### Step 0: <Prerequisites / setup>
### Step 1: <First action>
...
### Step N: <Generate output / summarize>

## Example Invocations
\`\`\`
/skill-name
/skill-name <arg>
/skill-name <arg> --flag
\`\`\`

## Output
<What files are written or what is printed.>

## Requirements
<CLI tools, language runtimes, packages needed.>

## Skill Structure
\`\`\`
skill-name/
├── SKILL.md
└── README.md          (+ scripts/ if applicable)
\`\`\`
```

**Writing guidelines:**
- Instructions should be imperative and specific — Claude will execute them literally
- Include actual bash commands with placeholders, not vague descriptions
- Use `> **Note**:` callouts for edge cases and gotchas
- Add a reference table for any domain-specific constants (e.g., IRS standard deductions, API rate limits)
- For conditional branching, use `#### Strategy A / B` sub-sections

### Step 5: Write README.md

Create `/tmp/claude-skills/<skill-name>/README.md` with this structure:

```markdown
# <skill-name>

<one-paragraph description>

## What It Does
- bullet 1
- bullet 2

## Workflow
\`\`\`mermaid
flowchart TD
    ...
\`\`\`

## Install
\`\`\`bash
git clone <repo>
ln -s "$(pwd)/claude-skills/<skill-name>" ~/.claude/skills/<skill-name>
\`\`\`

## Usage
\`\`\`bash
/<skill-name>
/<skill-name> <arg>
\`\`\`

## Output
<table of output files/artifacts>

**Sample output** (illustrative values):
<small table with FICTIONAL data — see Step 6>

## Requirements
<tools and versions>

## Supported inputs / edge cases
<table>

## Skill Structure
\`\`\`
skill-name/
├── SKILL.md
└── README.md
\`\`\`
```

#### Mermaid Workflow Diagram

Always include a `flowchart TD` Mermaid diagram under `## Workflow`. Guidelines:

- Start node: the slash command invocation `(["/skill-name\n[args]"])`
- End node: the final artifact or confirmation `(["Done\n..."])`
- Show decision diamonds `{}` for branching (e.g., "file found?", "extractable?")
- Group parallel outputs with separate branches converging to the end node
- Keep node labels short (2–3 lines max); use `\n` for line breaks inside nodes
- Aim for 8–15 nodes — enough to be informative, not so many it becomes unreadable

Example skeleton:
```
flowchart TD
    A(["/<skill-name>\n[args]"]) --> B[Step 1\ndescription]
    B --> C{Decision?}
    C -->|Yes| D[Path A]
    C -->|No| E[Path B]
    D --> F[Common step]
    E --> F
    F --> G(["Done\noutput saved"])
```

### Step 6: Privacy Review (REQUIRED before any git operation)

**This step is mandatory.** Before staging any file, scan every piece of content you wrote for:

| Risk category | What to look for | Action |
|--------------|-----------------|--------|
| Real personal data | Names, emails, SSNs, addresses, phone numbers | Remove entirely |
| Real financial figures | Actual income, tax, account numbers from any real person's documents | Replace with round fictional numbers |
| Real credentials | API keys, tokens, passwords | Remove entirely |
| Real file paths exposing usernames | `/Users/john.doe/...` in examples | Replace with `~/Documents/...` |
| Organization-specific details | Internal project names, proprietary system names | Generalize or anonymize |

**For sample output tables**: always use clearly fictional, round numbers (e.g., `$120,000`, `$14,200`, `12.0%`) — never copy figures from any real document processed during skill development.

> **Lesson learned**: If you accidentally commit real data, do NOT just push a fix commit — that leaves the sensitive data in git history. Instead: `git reset --hard <last-clean-commit>`, rewrite the files correctly, then `git push --force`. See Step 8.

### Step 7: Update the Repository README

Add a row to the skills table in `/tmp/claude-skills/README.md`:

```markdown
| [<skill-name>](<skill-name>/) | `/<skill-name>` | <one-line description> |
```

### Step 8: Commit and Push — Clean History Protocol

Stage and commit **all changes in a single commit**:

```bash
cd /tmp/claude-skills
git add <skill-name>/ README.md
git status   # verify ONLY intended files are staged
git commit -m "add <skill-name> skill

<2–3 sentence description of what the skill does.>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin main
```

**If you need to fix a privacy leak after pushing:**

```bash
# 1. Find the last clean commit (before any leaking commits)
git log --oneline

# 2. Reset hard to that commit — this removes ALL subsequent commits locally
git reset --hard <last-clean-sha>

# 3. Rewrite the files correctly (no sensitive data)
# 4. Stage and commit fresh
git add <skill-name>/ README.md
git commit -m "add <skill-name> skill ..."

# 5. Force push to rewrite remote history
git push --force origin main
```

> **Warning**: `--force` rewrites public history. Acceptable here because the goal is to erase leaked data. Notify any collaborators if the repo is shared.

### Step 9: Verify and Report

```bash
cd /tmp/claude-skills && git log --oneline -5
```

Confirm the skill directory exists on the remote, then report:
- Skill name and command (`/<skill-name>`)
- Commit SHA
- Files published
- How to install (symlink command)

## Example Invocations

```
/create-skill
```
→ Prompts for workflow details interactively

```
/create-skill "summarize PDFs in a folder into a markdown report"
```
→ Uses the description as the starting point

## Output

Two files published to the target GitHub repo:
- `<skill-name>/SKILL.md` — the skill definition
- `<skill-name>/README.md` — user-facing docs with Mermaid workflow diagram

## Requirements

- **Git** with push access to the target skills repository
- **GitHub CLI** (`gh`) optional but useful for verifying the push

## Skill Structure

```
create-skill/
├── SKILL.md    (this file)
└── README.md
```
