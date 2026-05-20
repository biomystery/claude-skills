---
name: skill-auditor
description: Audits all skills in a Claude skills repository against the official best-practices doc, files themed GitHub issues for every violation found, and implements all fixes in a single clean commit. Use when reviewing a skill collection for quality or discovery issues, or before sharing a repo publicly.
user-invocable: true
---

# Skill Auditor

Reads the official skill best-practices doc, scans every SKILL.md in the repo, groups findings into themed GitHub issues, then implements all fixes — description voice, line count, undefined variables, oversized inline scripts, stale constants — in one commit that auto-closes all issues.

## When to Use

- Auditing a skill collection for quality issues in one pass
- After adding several new skills and wanting consistency enforcement
- Before sharing a skill repo publicly
- Invoke after the skills repo is accessible locally

## Instructions

### Step 0: Resolve Repo

```bash
SKILLS_DIR="${SKILLS_REPO_DIR:-$HOME/projects/claude-skills}"

if [ -d "$SKILLS_DIR/.git" ]; then
  git -C "$SKILLS_DIR" pull
else
  git clone <repo_url> "$SKILLS_DIR"
fi
```

Fetch the best-practices doc with WebFetch:
- URL: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- Extract: all rules, checklists, and anti-patterns

### Step 1: Discover All Skills

```bash
find "$SKILLS_DIR" -name "SKILL.md" | sort
wc -l $(find "$SKILLS_DIR" -name "SKILL.md") | sort -rn | head -20
```

Read all SKILL.md files in parallel (multiple Read calls in one response).

### Step 2: Audit Each Skill

For each SKILL.md, check every item:

#### Description (`description:` frontmatter field)
- [ ] **Third-person voice** — must not start with an imperative (Convert, Build, Tile, Verify, Organize, Audit, Create, Generate). Correct form: "Converts…", "Builds…"
- [ ] **"Use when" trigger** — must include a "Use when…" phrase so Claude can select the right skill among 100+ candidates

#### Structure
- [ ] **Line count ≤ 500** — if over, find the largest conditional section (only needed in some cases) as the split target
- [ ] **`$SKILL_DIR` defined before use** — if any step references `$SKILL_DIR`, there must be a resolution line before first use
- [ ] **Inline scripts ≤ 15 lines** — scripts longer than 15 lines, called multiple times, or in a validation loop should be in `scripts/`

#### Content
- [ ] **Stale year constants** — year-specific figures (rates, limits, caps) need a ⚠️ callout noting the year and a reminder to verify annually
- [ ] **Forward slashes only** — no Windows-style backslashes in bash commands

### Step 3: Group Findings by Theme and File Issues

Group findings across all skills by violation type — do NOT file one issue per skill.

| Theme | Example affected skills |
|---|---|
| Description voice + missing "Use when" | skill-a, skill-b, skill-c |
| SKILL.md over 500 lines | skill-d |
| `$SKILL_DIR` undefined | skill-e, skill-f |
| Inline scripts > 15 lines | skill-g, skill-h |
| Stale year-specific constants | skill-i, skill-j |

```bash
gh issue create --repo <owner>/<repo> \
  --title "<theme>: <brief description>" \
  --body "<which skills, what's wrong, what the fix looks like>"
```

Note all issue numbers — they go in the commit message.

### Step 4: Implement All Fixes

#### Description voice + "Use when"

Edit the `description:` frontmatter line:
- Conjugate the verb: "Convert" → "Converts", "Build" → "Builds"
- Append: `Use when <trigger condition>.`

#### SKILL.md over 500 lines

1. Identify the conditional section (e.g., `## Update Mode`, `## Advanced`)
2. Write it to `<skill-name>/<SectionName>.md`
3. Replace the full section in SKILL.md with a reference stub:

```markdown
## <Section Name>
When <condition>, read [<SectionName>.md](<SectionName>.md) instead of Step N.
```

#### `$SKILL_DIR` undefined

Add immediately before the first use:

```bash
SKILL_DIR="$(dirname "$(realpath ~/.claude/skills/<skill-name>/SKILL.md)")"
```

#### Inline script > 15 lines

1. Write the script to `<skill-name>/scripts/<purpose>.py` with `argparse` or `sys.argv`
2. Replace the inline block in SKILL.md with the invocation:

```bash
python3 "$SKILL_DIR/scripts/<purpose>.py" <args>
```

3. Update `## Skill Structure` to list the new script

#### Stale year constants

Rename `## Key Constants (YYYY)` → `## Key Constants` and add:

```markdown
> ⚠️ Figures below are for **YYYY**. Verify against official publications before using for other years.
```

### Step 5: Commit on a Branch and Open a PR

Resolve all fixes locally first, then:

```bash
cd "$SKILLS_DIR"
BRANCH="fix/skill-audit-$(date +%Y%m%d)"
git checkout -b "$BRANCH"

git add <all changed and new files>
git status   # verify ONLY intended files are staged
git commit -m "audit skills against best-practices docs (closes #N #N #N)

<2–3 sentence summary of themes fixed>

Co-Authored-By: Claude <noreply@anthropic.com>"
git push -u origin "$BRANCH"
```

Create the PR:

```bash
gh pr create \
  --title "audit skills against best-practices docs" \
  --body "$(cat <<'EOF'
## Summary
Fixes found by auditing all SKILL.md files against the official best-practices doc.

- #N — <theme title>
- #N — <theme title>
...

## Changes
- Modified: N SKILL.md files
- Created: <list new files>

## Review checklist
- [ ] All description fixes are third-person with 'Use when' trigger
- [ ] Split files are referenced correctly from SKILL.md
- [ ] Extracted scripts have argparse / sys.argv and are listed in Skill Structure
- [ ] Year-constant callouts use the correct year
EOF
)"
```

### Step 6: HITL Review — wait for human approval

Present the PR URL and **stop**:

> "PR ready for review: **<PR URL>**
> Please check the diff and reply **'approved'** (or **'LGTM'**) to merge, or describe any changes needed."

Do **not** merge until the user explicitly approves.

If changes are requested: make them on the same branch, push, and repeat the approval request.

### Step 7: Merge and Report

Once the user approves:

```bash
gh pr merge --squash --delete-branch
git -C "$SKILLS_DIR" pull
git -C "$SKILLS_DIR" log --oneline -4
```

Report:
- Issues closed (numbers and titles)
- Files changed / created
- Merged commit SHA
- Any findings NOT auto-fixed — flag for manual follow-up

## Audit Checklist Quick Reference

| Check | How to detect | Fix |
|---|---|---|
| Third-person description | Starts with imperative verb | Edit frontmatter |
| "Use when" trigger | No "Use when" phrase in description | Edit frontmatter |
| Line count ≤ 500 | `wc -l` | Split conditional section to new file |
| `$SKILL_DIR` defined | Grep for `$SKILL_DIR` without prior assignment | Add resolution line |
| Inline scripts ≤ 15 lines | Read + count lines | Extract to `scripts/` with argparse |
| Stale year constants | Section title or inline values contain a year | Add ⚠️ callout |

## Example Invocations

```
/skill-auditor
```
→ Audits `$SKILLS_REPO_DIR` or `~/projects/claude-skills`

```
/skill-auditor --repo https://github.com/you/your-skills
```
→ Clones and audits a specific repo

## Output

- GitHub issues filed (one per violation theme)
- All SKILL.md files updated in place
- New `scripts/` files and split `.md` reference files as needed
- One clean commit that auto-closes all issues

## Requirements

- **`gh` CLI** authenticated to GitHub (`gh auth status`)
- **Git** with push access to the skills repository
- Skills repo accessible locally, or provide `--repo <url>` to clone

## Skill Structure

```
skill-auditor/
├── SKILL.md    (this file)
└── README.md
```
