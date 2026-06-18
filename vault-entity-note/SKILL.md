---
name: vault-entity-note
description: Synthesize a structured Obsidian reference note about a real-world entity (house, car, account, policy) by merging user-provided facts, public web records, and auto-pulled portal data — classifies the note into the correct vault folder, cross-links related notes, labels every source, and logs the work to the daily journal. Use when you finish researching or transacting on an asset and want a durable reference card.
user-invocable: true
---

# Vault Entity Note

Builds one clean, durable reference note about a single real-world entity from multiple data sources. The note lives in the correct vault folder (per the vault's classification rules), uses tables for structured facts, cross-links related notes with `[[wikilinks]]`, clearly labels where each fact came from, and is announced in the daily journal. Designed for an Obsidian vault that separates distilled knowledge (`Clean/`) from raw records (`Journals/`) and active work (`Projects/`).

## When to Use

- You just researched or transacted on an asset (home, vehicle, account, insurance policy) and want a reference card
- Facts are scattered across the user's head, public web records, and a portal/document you processed this session
- You want the note placed, linked, and journaled correctly without re-deriving the vault's conventions each time

## Core Rules (non-negotiable)

| Rule | Why |
|---|---|
| Label every fact's source | Public records, user-provided, and portal-pulled data have different reliability; future you must be able to recheck |
| Mark public-record data as **estimated** | Web lookups often return data for *adjacent* units (neighbor's sq ft, tax, HOA) — never present as exact |
| Never fabricate figures | Purchase price, tax, balances: if unknown, leave blank with "— (to confirm)", do not invent |
| Verify a file exists before hard-linking | A `[[wikilink]]` to a non-existent note is fine as a stub, but don't claim a "see X" note exists if it doesn't |
| Respect journal order | Newer timestamped entries go **above** older ones within a section (reverse chronological) |

## Instructions

### Step 0: Identify the Entity and Classify the Target Folder

Determine what the entity is and where the note belongs. Apply the vault's classification decision tree:

| Question | If yes → folder |
|---|---|
| Final, distilled reference knowledge? | `Clean/<Domain>/` |
| New analysis still awaiting a decision? | `Inbox/` |
| Project-specific and active? | `Projects/Doing/<project>/` |
| Raw daily record only? | `Journals/YYYY/YYYY-WXX/` |

A reusable entity reference card is almost always `Clean/<Domain>/` (e.g. `Clean/Home/`, `Clean/Auto/`). Confirm the domain subfolder exists:

```bash
ls "$VAULT/Clean/"
```

### Step 1: Gather and Tag the Three Sources

Collect facts from up to three sources, and **track which source each fact came from**:

1. **User-provided** — facts the user stated this session (most authoritative for things only they know: renovations, devices, purchase date).
2. **Public web records** — search for the entity. Treat results as **estimates**, especially when only neighboring units are found.

   ```
   WebSearch: "<address or identifier> <city> <zip> property details"
   WebSearch: "<nearest matching unit> details HOA beds baths"   # fallback when exact unit missing
   ```

   Capture: year built, size, style, structure, taxes, community/HOA — each flagged "(est., public records)".
3. **Portal / document auto-pull** — data a quote engine, portal, or scanned document surfaced this session (e.g. a Bolt/quote engine pulling assessor records). Note the source portal.

### Step 2: De-duplicate and Cross-link

Search the vault for existing notes on this entity or related ones, to avoid duplicates and to wire up links:

```bash
grep -rl "<entity identifier or key term>" "$VAULT/Clean/" "$VAULT/Projects/" 2>/dev/null
```

- If a note already covers this entity → **update it** instead of creating a duplicate.
- Identify related notes (insurance, maintenance, legal) and link them with `[[wikilinks]]`.
- Link liberally — a `[[name]]` to a not-yet-existing note is an acceptable stub.

### Step 3: Write the Structured Note

Create `Clean/<Domain>/<Entity Name>.md` with this skeleton:

```markdown
---
created: <ISO8601 now>
updated: <ISO8601 now>
tags:
  - <domain>
  - reference
---

# <Entity Title>

## Identity
| Field | Value |
|---|---|
| ... | ... |

## <Structured Section(s)>
<tables grouping facts: Structure, Finishes, Financials, etc.>

## Sources & Confidence
- User-provided: <list>
- Public records (estimated): <list> — from <site/date>
- Portal-pulled: <list> — from <portal>

## References
- [[Related Clean note]]
- [[Related Project note]]
```

Use round, honest numbers; mark estimates inline (`~$8,774/yr (est.)`); leave unknowns as `— (to confirm)`.

### Step 4: Log to the Daily Journal and Touch Related Notes

Get the time and append a reverse-chronological entry to today's journal:

```bash
date "+%H:%M"   # e.g. 19:20
```

Journal path: `Journals/YYYY/YYYY-WXX/YYYY-MM-DD.md`. Insert under the right section (🏠 Life / 💼 Work / 📖 Study), **newest on top**, format `HH:MM <emoji> <text>` with `[[wikilink]]` to the new note. Then:

- Update the new note's and any edited related note's frontmatter `updated:` timestamp.

### Step 5: Report

Tell the user: the note path, which folder/classification was chosen, the three sources used (and which facts are estimates vs confirmed), and any fields left blank to confirm.

## Example Invocations

```
/vault-entity-note my house at <address>
```
→ Builds `Clean/Home/House - <address>.md` from user facts + public records + any portal data, logs to journal

```
/vault-entity-note 2021 Honda Odyssey
```
→ Builds `Clean/Auto/...` reference card, cross-links the existing maintenance log

## Output

- One reference note in `Clean/<Domain>/`
- A reverse-chronological journal entry linking to it
- Updated `updated:` timestamps on touched notes

## Requirements

- An Obsidian vault with `Clean/`, `Journals/YYYY/YYYY-WXX/`, `Projects/` structure
- `WebSearch` (optional, for public records)
- `$VAULT` set to the vault root, or pass the path

## Skill Structure

```
vault-entity-note/
├── SKILL.md
└── README.md
```
