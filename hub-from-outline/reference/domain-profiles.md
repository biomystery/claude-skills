# Domain profiles

How the canonical **Hub → Track → Module → Item → Period** vocabulary maps onto
each kind of outline, and what changes per domain.

## Contents

- Vocabulary mapping table
- School / course year
- Book or reading run
- Training curriculum (gym, music, martial arts)
- Program or conference calendar
- Multi-part project outline
- Choosing when there is no Track

## Vocabulary mapping table

| Canonical | School course | Book | Training curriculum | Program calendar | Project outline |
|---|---|---|---|---|---|
| **Hub** | school / academy | the book | the discipline | the program | the initiative |
| **Track** | class section (`CH4-1`) | this reading run | current level / belt | this edition / year | this phase set |
| **Module** | unit | part / chapter | level | track / theme | workstream |
| **Item** | lesson | section | skill / drill | session / talk | deliverable |
| **Period** | class week | reading week | training block | conference day | sprint |

Use the canonical term in notes and headings; use the domain term only in prose
where it reads more naturally to the person filling the note in.

## School / course year

- Hub is shared across children and years — roster links out to one Track per child per year.
- Track holds enrollment status, teacher, room, and the dated Period index.
- Prefer dates over official week numbers: published "W1–W31" numbering routinely
  disagrees with the instructional-day count once closures land.
- Closures (holidays, teacher days) are `🚫` index rows with a reason and **no file**.

## Book or reading run

- Hub is the book: bibliographic frontmatter, edition, why you are reading it.
- Track is one pass through it (first read, re-read, book-club run) — a second pass
  gets a second Track page against the same Modules.
- Modules are parts or chapters; Items are sections.
- Periods only if the run is scheduled (book club dates); otherwise skip.

## Training curriculum (gym, music, martial arts)

- Hub is the discipline and its full ladder of levels.
- Track is the level currently being worked, with a promotion/assessment block.
- Modules are levels or belts; Items are the named skills inside them.
- Periods are training blocks rather than calendar weeks — pass `--period-label Block`.
- Items usually need a proficiency column (`⬜` learning / `📝` drilling / `✅` assessed).

## Program or conference calendar

- Hub is the recurring program; Track is one edition (year).
- Modules are tracks/themes; Items are individual sessions.
- Periods are days, not weeks — pass `--period-label Day`.
- Session times belong on the Period note; do not duplicate them into every Module.

## Multi-part project outline

- Only use this skill when the outline is genuinely a fixed multi-part structure to
  work through. For goal-driven work with next actions, use `/project-mgr` instead.
- Hub is the initiative; Modules are workstreams; Periods are sprints.

## Choosing when there is no Track

If exactly one instance will ever exist (a one-off workshop, a book you will read
once), fold the Track into the Hub: one hub note carrying the snapshot callout and
the indexes, no second page. Say so in the report so the user knows the split was
deliberately skipped rather than forgotten.
