# claude-skills

A collection of reusable [Claude Code](https://claude.ai/claude-code) skills — slash commands that encapsulate repeatable workflows into concise, invocable prompts.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [data-dictionary](data-dictionary/) | `/data-dictionary` | Generate a markdown data dictionary from a Prisma schema + live SQLite DB |
| [photo-year-collage](photo-year-collage/) | `/photo-year-collage` | Create a year-labeled photo collage grid from annual photos (visa applications, timelines) |
| [tax-history-tracker](tax-history-tracker/) | `/tax-history-tracker` | Build a multi-year U.S. tax history tracker from Form 1040 PDFs — extracts income, AGI, deductions, tax, effective rate, and refund/owe across all years |
| [session-to-skill](session-to-skill/) | `/session-to-skill` | At the end of a Claude Code session, abstract what you just did into a reusable skill — Claude reconstructs the workflow from context, writes SKILL.md + README.md with Mermaid diagram, runs a privacy review, and pushes a single clean commit |
| [backdoor-roth-review](tax/backdoor-roth-review/) | `/backdoor-roth-review` | Verify Form 8606 for a backdoor Roth IRA conversion — checks Line 1/2 basis, Code G vs Code 2 separation, pro-rata calculation, and Form 1040 Line 4a/4b — outputs expected value for every line |
| [tax-draft-review](tax/tax-draft-review/) | `/tax-draft-review` | Audit a U.S. Form 1040 draft return against known income documents — catches missing 1099-Rs, wrong IRA basis, omitted Schedule C deductions, and SALT errors before filing |
| [schedule-c-tracker](tax/schedule-c-tracker/) | `/schedule-c-tracker` | Build a complete Schedule C from bank exports and receipts — reconciles gross income, categorizes deductions (home office, Section 179, phone/internet), and outputs ready-to-file line values with SE tax and QBI estimates |

## What is a Claude Code Skill?

A skill is a markdown file (`SKILL.md`) that Claude Code loads as a slash command. When invoked, Claude follows the instructions inside to complete the task autonomously. Skills live in `~/.claude/skills/<skill-name>/SKILL.md` (personal) or `.claude/skills/<skill-name>/SKILL.md` (project-level).

## Installation

### Install a single skill

```bash
# Clone the repo
git clone https://github.com/biomystery/claude-skills.git

# Symlink the skill(s) you want into your Claude skills directory
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/data-dictionary" ~/.claude/skills/data-dictionary
```

Then restart Claude Code — the `/data-dictionary` command will be available in any project.

### Install all skills

```bash
git clone https://github.com/biomystery/claude-skills.git
cd claude-skills
for skill in */; do
  ln -sf "$(pwd)/${skill%/}" ~/.claude/skills/"${skill%/}"
done
```

## Adding a New Skill

1. Create a directory: `mkdir <skill-name>`
2. Write `<skill-name>/SKILL.md` with this frontmatter:
   ```markdown
   ---
   name: skill-name
   description: One-line description shown in the Claude skill picker.
   user-invocable: true
   ---
   ```
3. Add instructions, examples, and an output spec inside the file.
4. Add a row to the table in this README.
5. Open a PR.

## License

MIT
