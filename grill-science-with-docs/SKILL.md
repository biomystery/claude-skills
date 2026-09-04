---
name: grill-science-with-docs
description: A two-phase interrogation for analysing someone else's dataset — Phase 1 grills the data AND the domain expert until the picture is provably aligned (source paper methods, complete structure enumeration, unit of analysis, candidate denominators, what actually exists), then a hard gate, then Phase 2 does pre-specified analysis with rendered-and-inspected figures and an honest statement of what the data cannot settle. Use when asked to test a claim, reproduce a finding, or answer a colleague's question with a dataset you did not create.
user-invocable: true
disable-model-invocation: true
---

# Grill Science With Docs

Most wrong analyses are not statistical errors. They are **alignment errors** — you analysed a different cohort, unit, or denominator than the one the question was about, and found out four revisions later.

This skill forbids analysis until the picture is written down and confirmed.

## When to Use

- Someone hands you a dataset and a question ("does X hold?", "can you check this in that data?")
- You are testing a claim from a paper, or extending a colleague's preliminary result
- The data has a **source document** — a paper, protocol, or data dictionary — that you have not read in full

**Do not use** for data you generated yourself, or for exploratory plotting with no claim at stake.

---

# PHASE 1 · GRILL

**No analysis in this phase. No statistics, no plots, no `groupby`.** You are building a picture, not a result.

### Step 1: Read the source document — the methods, not the abstract

Fetch the full text. Abstracts systematically understate what was collected.

```bash
# papers: get the manuscript XML/full text, not the landing page
curl -sL -o paper.xml "<publisher full-text or PMC URL>"
```

Extract and read, in this order: **Methods → Table 1 → the selection/CONSORT cascade → Limitations**. Record:

| Question | Why it bites |
|---|---|
| What was **actually measured**, at what granularity? | An abstract may imply a subset while methods describe the full instrument |
| What does the **published file** expose vs what was collected? | Files often aggregate; the raw granularity may be unrecoverable |
| **Who was excluded, and why?** | Your analysable set is frequently *not* the paper's cohort |
| What are the authors' **own stated limitations**? | Free list of the objections you will otherwise discover late |

### Step 2: Enumerate the structure exhaustively — never assert absence

> **"I did not find it" is not "it does not exist."** Assert absence only after enumerating every container.

```bash
python3 scripts/enumerate_source.py <file.xlsx|file.csv|db.sqlite>
```

Read the **whole** inventory before concluding anything is missing. Multi-sheet workbooks, side tables, and companion files routinely hold the variable you are about to declare absent.

### Step 3: Fix the unit of analysis — and never mix

Write down explicitly: **what is one row?** A patient? An observation? A sub-unit nested in a patient?

Different units answer different questions and legitimately carry **different n**. Conflating them is the single most common source of confusion in the write-up. Record the mapping, e.g.:

```
70 measured sub-units → 26 analysis units  (22 resolved individually + 2 + 2 aggregated)
Counts use all 70. The paired statistic uses the 26.
```

Both numbers are correct. Say which is which, every time.

### Step 4: Derive the analysis set as a cascade

Write the attrition explicitly, with an n at every step and the **reason** for each drop:

```
N   all records
 ↓  complete at timepoint 1
 ↓  complete at timepoint 2
 ↓  eligible for the statistic (state the eligibility rule)
n   ANALYSIS SET
```

Then **compare your analysis set against the source cohort** on the key clinical/descriptive variables. If they differ, that is a finding, not a footnote — quoting the paper's Table 1 as if it described your set is a common and serious error.

### Step 5: List every candidate denominator

For the question asked, enumerate the defensible denominators and state what each one means. Choose deliberately.

Ask of each: *who is in this denominator who **cannot** exhibit the outcome?* Anyone who cannot should usually be excluded — including them silently dilutes the rate.

### Step 6: Grill the human

The data cannot answer these. The domain expert can, and will correct you.

- "Is this the cohort you mean?"
- "Which denominator answers *your* question?"
- "Does your own dataset collect X separately?" *(often yes, which changes the plan entirely)*
- "Is decision Y still open?" *(determines whether this is urgent or academic)*
- "What would change your mind?"

Expect to be corrected on facts that are not in the file. Treat every correction as a Phase-1 defect, not a nuisance.

### ⛔ ALIGNMENT GATE

Write the picture as a short document — **units, cascade, analysis set vs source cohort, chosen denominator, what exists, what does not** — and get **explicit confirmation** before continuing.

Do not proceed on assumed agreement. This gate is the entire point of the skill.

---

# PHASE 2 · WORK

### Step 7: Pre-specify the interpretation grid — in writing, before looking

State the outcomes, the model, and **what each possible result would mean**, before running anything.

Where the exposure and the outcome share arithmetic, split outcomes into families and commit to reading the contrast:

| Outcome family | |
|---|---|
| **Contaminated** — shares components with the exposure | a difference here alone ⇒ artifact |
| **Clean** — independent of the exposure's construction | a difference here ⇒ candidate real effect |

Landing on a cell of a **pre-committed** grid is a finding. Constructing the grid afterwards is a story.

### Step 8: Analyse, adjusting for the obvious confounders

Adjust for baseline value and anything the grill flagged. Report effect sizes with n; do not lead with p-values at small n.

### Step 9: Render every figure and LOOK at it

Never ship a figure you have not viewed. Plotting libraries fail **silently**.

```bash
python3 scripts/check_figure.py <figure.png> --source <plotting_script.py>
```

Real defects caught this way, each of which would have shipped:

- **Clipped axes** — hardcoded limits that no longer bracket the data
- **Silently dropped data** — explicit histogram bins discard out-of-range values with no warning
- **Stale annotations** — a hardcoded `n.s.` label sitting on a `p = 0.006` result
- **Overclaiming captions** — "at every position" when it held at 9 of 10

Verify the caption against the numbers, not against your intent.

### Step 10: Put corrections IN the artifact

When a number changes, record the chain — old value, new value, and *why* — in the deliverable itself. A headline that moved four times is credible **if the moves are visible** and alarming if discovered later.

Do not annotate superseded figures; **regenerate them** and keep the changelog in prose.

### Step 11: Separate what the data can and cannot settle

State the honest null plainly. "These two groups are not distinguishable in this dataset" is a legitimate, useful answer.

Guard against reading noise as signal: with `k` comparisons, one nominal `p < 0.05` is what chance predicts. Report the Bonferroni threshold next to it.

Also separate **relative** from **absolute**: a 30× relative risk can coexist with most events occurring in the low-risk group when that group is far larger. State both.

---

## Reproducibility

- Keep the analysis core **stdlib-only** where possible, so it runs anywhere without an environment
- **Commit the data with the code** when the licence allows; note the source URL and licence
- **One command per analysis** — a named entry point per question
- Put heavy virtualenvs **outside** any synced folder (iCloud/Dropbox) — they are large and sync badly

## Reporting Back

When the result touches a colleague's own work:

1. **Lead with what strengthens their position**, not with your correction
2. **Disclose your own errors first**, before presenting conclusions
3. **State the limitation that most threatens your result**, before they find it
4. Frame open questions as *"only you can answer this"* where that is true — it usually is

## Example Invocations

```
/grill-science-with-docs
```
→ Runs Phase 1 on the dataset in context, stops at the alignment gate

```
/grill-science-with-docs data/cohort.xlsx --paper https://doi.org/10.xxxx/yyyy
```
→ Reads the paper first, enumerates the workbook, drafts the picture for confirmation

## Output

- A written **data picture** (units, cascade, analysis set vs source cohort, denominators) confirmed before analysis
- A **pre-specified analysis plan** with its interpretation grid
- Reproducible analysis code with one entry point per question
- Figures that have been rendered and inspected
- A **correction log** in the deliverable
- An explicit statement of what the data cannot settle

## Requirements

- `python3` (the enumerator is stdlib-only)
- A headless browser or image viewer for figure inspection
- Network access to fetch the source document
- **A human available at the alignment gate** — this skill does not run unattended

## Skill Structure

```
grill-science-with-docs/
├── SKILL.md
├── README.md
└── scripts/
    ├── enumerate_source.py    # Phase 1 — complete structure inventory
    └── check_figure.py        # Phase 2 — render, measure, lint captions
```
