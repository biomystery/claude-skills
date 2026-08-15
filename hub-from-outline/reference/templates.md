# Note templates

Skeletons for every file this skill writes. Domain vocabulary is in SKILL.md.

**Keep the section names and order exactly as written** — SKILL.md Steps 3–5 audit
against them, and the Hub/Track indexes assume them. Domain wording belongs in the
prose inside a section, never in its heading.

`Pxx` is a placeholder for the period prefix derived from `--period-label`
(`W01`, `D01`, `B01`, `S01`); `<folder>` is the matching folder (`Weeks/`, `Days/`,
…). Substitute both before writing anything. Never emit a literal `P01`.

## Contents

- Hub note
- Track note
- `Modules/_Template.md`
- `<folder>/_Template.md` (period)
- Module stub (`M01 ….md`)
- Status legend

## Hub note

```markdown
---
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
tags: [<domain>, hub]
aliases: [<short name>]
---

# <Hub name>

> [!info] What this note is
> Durable home for <hub>. Instance-agnostic: per-person and per-run facts live on
> the Track pages linked below.

## Tracks
| Track | Who / when | Status |
|---|---|---|
| [[<Track>]] | <person or run> | 📝 |

## Contact & location
<address, portal, contacts — no credentials>

## Module index
| # | Module | Items | Note |
|---|---|---|---|
| M01 | <title> | <n> | [[Modules/M01 <title>\|open]] |

## How this folder is organized
<short tree + one line on the fill-in workflow>

## Map
<only when --mermaid; see SKILL.md Step 6>

## Related
[[<parent profile>]] · [[<sibling activity>]]
```

## Track note

```markdown
---
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
tags: [<domain>, track]
---

# <Track name>

> [!abstract] Snapshot
> **Schedule** <days/times> · **Lead** <instructor/facilitator> ·
> **Location** <room/link> · **Materials** <book/kit>

## Participant
- Status: <enrolled / in progress>
- Open items: <bare `- [ ]` unless these are real agent `#task`s>

## Module index
| # | Module | Status | Note |
|---|---|---|---|
| M01 | <title> | ⬜ | [[Modules/M01 <title>\|open]] |

## Period index
| Period | Date | Focus | Status |
|---|---|---|---|
| [[<folder>/Pxx <YYYY-MM-DD>\|Pxx]] | <YYYY-MM-DD> | <module/topic> | ⬜ |
| — | <YYYY-MM-DD> | 🚫 <closure reason> | 🚫 |

Every live row is a wikilink, including periods whose file does not exist yet —
clicking the unresolved link is how the note gets created later. Closure rows are
plain text with no link.

## Materials & logistics
<books, kit, fees, portal links>

## Related
[[<Hub>]]
```

## `Modules/_Template.md`

```markdown
---
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
tags: [<domain>, module]
---

# <Mxx Title>

## Scope
<what this module covers, from the outline>

## Goals
- [ ] <goal>

## Key terms
| Term | Meaning | Notes |
|---|---|---|

## Items
| Item | Period | Status |
|---|---|---|

## Reflection
<what stuck, what to revisit>

## Related
[[<Track>]] · [[<Hub>]]
```

## `<folder>/_Template.md` (period)

```markdown
---
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
tags: [<domain>, period]
---

# <Pxx YYYY-MM-DD>

- **Participated:** <yes/no — attended, read, trained, shipped>
- **Module:** [[Modules/<Mxx …>]]

## Focus
<what this period covered>

## Assignments
| Task | Due | Done |
|---|---|---|

## Notes from the source
<whatever carries the period's information: instructor email, handout, chapter
notes, standup, session recording>

## Follow-up before the next period
- [ ] <item>

## Next
[[<folder>/<Pxx+1> <YYYY-MM-DD>]]
```

The four body sections are deliberately generic. Reword the *content* per domain
(a conference Day has speakers where a class Week has homework); do not rename the
headings.

## Module stub

A stub is the `Modules/_Template.md` skeleton with the title, scope line, and Item
rows filled from the outline, and everything else left empty. Mark any title that
was inferred rather than read verbatim in *italics*.

## Status legend

Use these four glyphs and no others, on both indexes:

| Glyph | Meaning |
|---|---|
| `⬜` | not started |
| `📝` | in progress |
| `✅` | complete |
| `🚫` | cancelled / closure — index row only, no file |
