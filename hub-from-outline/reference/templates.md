# Note templates

Skeletons for every file this skill writes. Adapt headings to the domain (see
[domain-profiles.md](domain-profiles.md)); keep the section order, since the
indexes on the Hub and Track pages assume it.

## Contents

- Hub note
- Track note
- `Modules/_Template.md`
- `Periods/_Template.md`
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
| [[<Track>]] | <person or run> | 🟢 active |

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
| P01 | <YYYY-MM-DD> | <module/topic> | ⬜ |
| — | <YYYY-MM-DD> | 🚫 <closure reason> | 🚫 |

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

## `Periods/_Template.md`

```markdown
---
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
tags: [<domain>, period]
---

# <Pxx YYYY-MM-DD>

- **Attended:** <yes/no>
- **Module:** [[Modules/<Mxx …>]]

## Focus
<what was covered>

## Assignments
| Task | Due | Done |
|---|---|---|

## Notes from the lead
<email/handout summary>

## Practice at home
- [ ] <item>

## Next
[[<P(xx+1) YYYY-MM-DD>]]
```

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
