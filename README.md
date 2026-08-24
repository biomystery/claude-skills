# claude-skills

A collection of reusable [Claude Code](https://claude.ai/claude-code) skills — slash commands that encapsulate repeatable workflows into concise, invocable prompts.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [logseq-to-obsidian](logseq-to-obsidian/) | `/logseq-to-obsidian` | Migrate a Logseq vault into Obsidian — converts filenames, cleans syntax, converts page properties to YAML, resolves iCloud conflicts, and backfills timestamps |
| [data-dictionary](data-dictionary/) | `/data-dictionary` | Generate a markdown data dictionary from a Prisma schema + live SQLite DB |
| [photo-year-collage](photo-year-collage/) | `/photo-year-collage` | Create a year-labeled photo collage grid from annual photos (visa applications, timelines) |
| [tax-history-tracker](tax-history-tracker/) | `/tax-history-tracker` | Build a multi-year U.S. tax history tracker from Form 1040 PDFs — extracts income, AGI, deductions, tax, effective rate, and refund/owe across all years |
| [photo-print-layout](photo-print-layout/) | `/photo-print-layout` | Tile any fixed-size ID/passport photo onto a 4×6, 5×7, or other print canvas at 300 DPI — auto-calculates optimal grid, margins, and gaps for photo lab printing |
| [passport-photo-check](passport-photo-check/) | `/passport-photo-check` | Given a print-lab layout JPEG, verify each individual photo meets official ID/passport requirements — visual check (face proportion, expression, background, gaze) + pixel-level dimension measurement in mm |
| [session-to-skill](session-to-skill/) | `/session-to-skill` | At the end of a Claude Code session, abstract what you just did into a reusable skill — Claude reconstructs the workflow from context, writes SKILL.md + README.md with Mermaid diagram, runs a privacy review, and pushes a single clean commit |
| [md-to-docx](md-to-docx/) | `/md-to-docx` | Convert a Markdown file to Word (.docx), rendering any Mermaid diagrams as embedded PNG images — uses pandoc + mermaid-cli via npx (no global install needed) |
| [md-to-pptx-editable](md-to-pptx-editable/) | `/md-to-pptx-editable` | Convert a Marp markdown deck to PowerPoint — renders Mermaid blocks as images, produces a text-editable PPTX (via LibreOffice) plus pixel-perfect PDF and image-PPTX fallbacks, and preserves Marp speaker notes |
| [ppt-template-to-css](ppt-template-to-css/) | `/ppt-template-to-css` | Generate a Marp theme CSS from a PowerPoint template (.pptx/.potx) — extracts the OOXML color scheme, fonts, and title/body sizes so Marp decks match a brand template; pairs with `/md-to-pptx-editable --theme` (pure stdlib, no deps) |
| [backdoor-roth-review](tax/backdoor-roth-review/) | `/backdoor-roth-review` | Verify Form 8606 for a backdoor Roth IRA conversion — checks Line 1/2 basis, Code G vs Code 2 separation, pro-rata calculation, and Form 1040 Line 4a/4b — outputs expected value for every line |
| [tax-draft-review](tax/tax-draft-review/) | `/tax-draft-review` | Audit a U.S. Form 1040 draft return against known income documents — catches missing 1099-Rs, wrong IRA basis, omitted Schedule C deductions, and SALT errors before filing |
| [schedule-c-tracker](tax/schedule-c-tracker/) | `/schedule-c-tracker` | Build a complete Schedule C from bank exports and receipts — reconciles gross income, categorizes deductions (home office, Section 179, phone/internet), and outputs ready-to-file line values with SE tax and QBI estimates |
| [skill-auditor](skill-auditor/) | `/skill-auditor` | Audit all skills in a repo against the official best-practices doc — files themed GitHub issues and implements every fix (description voice, line count, $SKILL_DIR, inline scripts, stale constants) in one clean commit |
| [clean-meeting-note](clean-meeting-note/) | `/clean-meeting-note` | Clean a raw shorthand meeting note — fixes typos, repairs structure, flags ambiguous content for HITL clarification, removes PII, and writes `_clean.md` at a chosen detail level (1–3) |
| [normalize-date-filenames](normalize-date-filenames/) | `/normalize-date-filenames` | Normalize dated filenames (Office Lens, Microsoft Lens, "Scan from", compact MDY) to YYYY-MM-DD-<time-or-desc>.ext — dry-runs first, optionally deduplicates .pptx/.docx when a .pdf exists |
| [vault-entity-note](vault-entity-note/) | `/vault-entity-note` | Synthesize a structured Obsidian reference note about a real-world entity (house, car, account, policy) by merging user facts, public web records, and portal-pulled data — classifies the folder, labels every source, marks estimates, cross-links, and logs to the daily journal |
| [browser-quote-shop](browser-quote-shop/) | `/browser-quote-shop` | Use the Playwright MCP browser to shop one item across multiple online providers and compile a sorted comparison table — classifies each outcome, captures quote IDs, and handles form gotchas (address autocomplete, press-and-hold CAPTCHAs, ng-select multi-selects, broker auto-pull) |
| [log-to-journal](log-to-journal/) | `/log-to-journal` | Append a timestamped entry to today's Obsidian daily journal (Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md) following vault conventions — picks the right section, inserts time-first in reverse-chronological order, links `[[wikilinks]]`, bumps `updated:`, and handles the iCloud linter race + Unicode characters that break exact-string edits |
| [epub-to-kindle](epub-to-kindle/) | `/epub-to-kindle` | Convert an EPUB (or any Calibre-supported ebook) to a Kindle format — AZW3 (modern) or MOBI (legacy) — via Calibre's ebook-convert; auto-locates the CLI inside the macOS .app bundle, installs Calibre through Homebrew if missing, and surfaces the exact sudo chown command when /opt/homebrew permissions block the install |
| [morning-plan](morning-plan/) | `/morning-plan` | Morning planning routine for an Obsidian vault — retroactively logs yesterday's activities, identifies today's MITs (caveman mode), schedules urgent todos via `⏳` on the weekly note, and surfaces imminent deadlines |
| [review-week](review-week/) | `/review-week` | Review the past week's daily journals into last week's retrospective (重要/琐事), write a per-person family section from the owner's perspective, check primary-goal progress on a long-term → short-term ladder, draft a plan for any important goal that lacks one, and roll open items plus drafted plans into this week's priorities |
| [project-mgr](project-mgr/) | `/project-mgr` | Build an active Obsidian project from a one-line goal under `Projects/Doing/` — success criteria, workstreams, `#task` next actions, privacy-safe cross-links, and a daily-journal announcement |
| [hub-from-outline](hub-from-outline/) | `/hub-from-outline` | Scaffold any structured outline — course syllabus, book TOC, training curriculum, program calendar — into an Obsidian hub → module pages → optional dated period notes, with an optional Mermaid outline-index graph |
| [catalog-to-tracker](catalog-to-tracker/) | `/catalog-to-tracker` | Turn a catalog living in Obsidian tables (skill tree, curriculum, drill library) into a single-source-of-truth checkbox tracker — merges any hand-copied "scheduled" duplicates back by stable ID, verifies nothing was lost against a backup, and designs the tag scheme a query-driven schedule page runs on |

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
