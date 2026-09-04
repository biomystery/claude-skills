# grill-science-with-docs

A two-phase interrogation for analysing a dataset you did not create. Phase 1 grills the data **and** the domain expert until the picture is provably aligned. A hard gate. Then Phase 2 does the analysis.

Most wrong analyses are not statistical errors. They are **alignment errors** — you analysed a different cohort, unit, or denominator than the question was about, and found out four revisions later.

## What It Does

- Reads the **source document's methods**, not its abstract — abstracts systematically understate what was collected
- **Enumerates every container** in the source, so "there is no X" is never claimed from a partial scan
- Pins the **unit of analysis** and the **derivation cascade**, with an n and a reason at every step
- Compares your analysis set against the **source cohort** — they are often not the same population
- Forces you to **grill the human** for facts the file cannot state
- **Blocks analysis** until the picture is written down and confirmed
- Then: pre-specified interpretation grid → analysis → **rendered and inspected** figures → correction log → an explicit statement of what the data cannot settle

## Workflow

```mermaid
flowchart TD
    start(["/grill-science-with-docs\n[data] [--paper URL]"])
    paper["Read source METHODS\nnot the abstract"]
    enum["enumerate_source.py\nevery sheet / table / column"]
    unit["Pin unit of analysis\nwhat is one row?"]
    casc["Derive analysis set\nas an attrition cascade"]
    cmp{"Analysis set ==\nsource cohort?"}
    diff["Record the difference\nit is a finding"]
    human["Grill the domain expert\nfacts not in the file"]
    gate{"⛔ ALIGNMENT GATE\npicture confirmed?"}
    grid["Pre-specify interpretation grid\ncontaminated vs clean outcomes"]
    run["Analyse + adjust\nfor baseline"]
    fig["check_figure.py\nthen LOOK at it"]
    log["Correction log\ninto the artifact"]
    done(["Done\nresult + honest null"])

    start --> paper --> enum --> unit --> casc --> cmp
    cmp -->|No| diff --> human
    cmp -->|Yes| human
    human --> gate
    gate -->|No| enum
    gate -->|Yes| grid --> run --> fig --> log --> done
```

## Install

```bash
git clone https://github.com/biomystery/claude-skills ~/projects/claude-skills
ln -s ~/projects/claude-skills/grill-science-with-docs ~/.claude/skills/grill-science-with-docs
```

## Usage

```bash
/grill-science-with-docs
/grill-science-with-docs data/cohort.xlsx --paper https://doi.org/10.xxxx/yyyy
```

Standalone, outside a session:

```bash
python3 scripts/enumerate_source.py data/cohort.xlsx --grep 'dose|drug|treat'
python3 scripts/check_figure.py figures/fig1.png --source analysis/plots.py
```

## Output

**Sample enumeration** (illustrative values):

```
cohort.xlsx  —  6 sheet(s), 88 columns total
==============================================================================

[sheet] Measurements   rows=400   cols=52
       0  Subject ID
       1  Visit
    ...

FLAT INDEX — 88 columns across 6 sheet(s)
grep 'dose|drug|treat': 3 hit(s)
    [Prescriptions] Daily dose
    [Prescriptions] Drug class
    [MedChange] Treatment switched
```

The point of the flat index: the variable you were about to declare missing is usually sitting in a sheet you did not open.

**Sample figure lint** (illustrative values):

```
FIGURE  fig1.png
  1200x700, 18.4% non-background

SOURCE  plots.py
  [HIGH] line 42: hardcoded p-value in a string — interpolate the computed value
  [MED]  line 77: explicit bins silently DROP out-of-range values
  [HIGH] line 91: absolute claim in a caption — verify it holds in every stratum
```

## Requirements

- `python3` — `enumerate_source.py` is stdlib-only (reads `.xlsx` via the OOXML zip, no `openpyxl`)
- `Pillow` *optional* — enables the image half of `check_figure.py`; source linting works without it
- Network access to fetch the source document
- **A human at the alignment gate** — this skill does not run unattended

## Supported inputs / edge cases

| Input | Handling |
|---|---|
| `.xlsx` / `.xlsm` | Every sheet enumerated, including ones the analysis never touches |
| `.csv` / `.tsv` | Headers + row count |
| `.sqlite` / `.db` | Every table and view, with row counts |
| Aggregated columns | Flagged in the picture — record what granularity is **unrecoverable** |
| Analysis set ≠ paper cohort | Treated as a finding, not a footnote |
| Multiple defensible denominators | Enumerate all, choose deliberately, state which is in force |
| An honest null | A legitimate deliverable — "not distinguishable here" is an answer |

## Skill Structure

```
grill-science-with-docs/
├── SKILL.md
├── README.md
└── scripts/
    ├── enumerate_source.py
    └── check_figure.py
```
