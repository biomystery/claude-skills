---
name: clean-meeting-note
description: Clean a raw shorthand meeting note into a structured md file — preserves author voice, asks before touching ambiguous content (HITL), removes PII, and accepts a detail level parameter (1–3).
user-invocable: true
---

# Clean Meeting Note

Takes a raw meeting note (bullet shorthand, mixed languages, typos, nested structure) and produces a clean version in the same folder. Preserves the author's original voice and shorthand style — it does not rewrite or summarize. Ambiguous items are flagged and clarified with the user before any edits are made.

## When to Use

- You have a raw meeting note and want a clean version to share or archive
- The note has typos, inconsistent casing, or unclear shorthand that needs resolving
- You want structure tidied without losing your original phrasing

## Parameters

| Parameter | Values | Default | Meaning |
|---|---|---|---|
| `--level` | `1`, `2`, `3` | `2` | Grade of cleanup (see below) |
| `<file>` | path to `.md` file | required | The note to clean |

### Cleanup Levels

| Level | What changes |
|---|---|
| **1 — minimal** | Typos, capitalization of proper nouns, frontmatter dates only. Structure and wording untouched. |
| **2 — moderate** | Level 1 + reorder sections if clearly out of logical sequence + fix broken bullet hierarchy |
| **3 — structured** | Level 2 + normalize section headers + expand unclear shorthand (after HITL clarification) |

## Instructions

### Step 1: Read the Note

Read the file provided by the user.

```bash
cat -n "<file_path>"
```

### Step 2: Privacy Scan

Before doing anything else, scan for PII and sensitive content:

| Risk | What to look for | Action |
|---|---|---|
| Real names | Full names of non-public individuals | Flag to user — ask whether to anonymize or keep |
| Contact info | Emails, phone numbers | Remove unless user says keep |
| Org-internal names | Proprietary system/project names | Ask user if safe to include |
| Identifying paths | `/Users/<real-name>/...` | Replace with `~/...` |

Report any findings to the user before proceeding.

### Step 3: HITL — Flag Ambiguous Content

Before editing, identify items that are unclear and would require interpretation. Present them as a numbered list:

```
The following items are ambiguous — please clarify before I edit:

1. "<exact phrase from note>" — what does this refer to?
2. "<exact phrase>" — is this a person, system, or action?
...
```

Wait for the user's answers. Do not guess or skip this step.

If nothing is ambiguous, state: "No ambiguous items found — proceeding with cleanup."

### Step 4: Apply Cleanup

Apply changes according to the requested `--level`. Use the user's HITL answers to resolve ambiguous items.

**Level 1 — minimal only:**
- Fix spelling errors and typos
- Capitalize proper nouns (product names, tools, acronyms)
- Fix frontmatter `created`/`updated` format if malformed
- Do not touch structure, ordering, or wording

**Level 2 — moderate (default):**
- Everything in Level 1
- Reorder top-level sections if user specified a preferred order, or if order is clearly illogical
- Fix broken bullet indentation hierarchy
- Do not rewrite sentences

**Level 3 — structured:**
- Everything in Level 2
- Normalize section headers to `## Title Case`
- Replace resolved shorthand with full terms (using HITL answers)
- Expand acronyms inline on first use where the HITL answer provided the expansion

**Do not:**
- Summarize or compress content
- Add content not in the original
- Translate between languages
- Remove content (except confirmed PII)

### Step 5: Write Output

Write the cleaned note as `<original-filename>_clean.md` in the same folder as the source file.

```
output path: <same directory>/<original-stem>_clean.md
```

Report what changed in a short diff-style summary:
- Sections reordered: yes/no
- Typos fixed: N
- Ambiguous items resolved: N
- PII removed: yes/no

## Example Invocations

```
/clean-meeting-note Meeting Notes 2026-05-21.md
```
→ Level 2 cleanup, HITL for ambiguous items, output: `Meeting Notes 2026-05-21_clean.md`

```
/clean-meeting-note --level 1 rough-notes.md
```
→ Typos and capitalization only, no reordering

```
/clean-meeting-note --level 3 product-review.md
```
→ Full structural cleanup with shorthand expansion after HITL

## Output

A single file: `<original-stem>_clean.md` in the same directory as the input.

- Author voice and shorthand preserved
- Mixed-language content kept as-is
- No added content or summaries

## Requirements

- Input must be a `.md` file
- User must respond to HITL questions before output is written

## Skill Structure

```
clean-meeting-note/
├── SKILL.md
└── README.md
```
