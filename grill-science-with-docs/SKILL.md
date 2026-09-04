---
name: grill-science-with-docs
description: A relentless interview that sharpens a scientific claim and closes the loop on it, producing durable records as it goes — a Claim Record (what is asserted, what decision it serves, what would falsify it, what is already known), an Evidence Ledger (what the source actually supports vs what you assumed, with every correction logged), and a Findings Record (what was settled, what was ruled out, what remains open). Four phases — FRAME, GROUND, TEST, CLOSE — each behind a gate that requires human confirmation. Use when forming or testing a hypothesis, analysing evidence you did not generate, extending someone's preliminary result, or deciding whether a line of enquiry is worth continuing.
user-invocable: true
disable-model-invocation: true
---

# Grill Science With Docs

An interview, not a checklist. You are trying to make a claim **fail cheaply** before
it fails expensively.

Most bad scientific work is not bad statistics. It is well-executed work on a claim
nobody stated precisely, grounded in evidence nobody checked, that ends without
anyone recording what is now known.

| Layer | Failure | Symptom |
|---|---|---|
| **Claim** | Answered a proxy question rigorously | Correct answer, wrong question |
| **Ground** | Assumed what the evidence contains | Result moves every time someone looks closer |
| **Test** | Interpretation chosen after seeing results | Story, not finding |
| **Close** | Nothing durable recorded | The next person redoes it |

Four phases, four artifacts, gates between them.

## When to Use

- Forming a hypothesis, or being handed one to test
- Analysing evidence you did not generate
- Extending or checking someone else's preliminary result
- Deciding whether to continue or abandon a line of enquiry

**Not for**: routine exploration with no claim at stake, or work where you generated
the evidence and already know its provenance cold.

## Artifacts

Write these as you go, not afterwards. They are the deliverable as much as the result.

| Artifact | Holds | Analogue |
|---|---|---|
| **Claim Record** | the claim, the decision it serves, prior art, falsifiers | ADR |
| **Evidence Ledger** | what the source supports, what it cannot, every correction | lab notebook |
| **Findings Record** | settled / ruled out / still open, and why | results + limitations |

---

# PHASE 1 · FRAME

**No evidence access yet.** You are deciding what is being claimed and whether it is
worth the work.

### Interrogate the claim

- **State it as something that could be false.** If no observation would contradict
  it, it is not yet a claim. Rewrite until it can lose.
- **What decision moves on the answer, and by when?** If nothing moves, say so and
  stop — a legitimate outcome. If something does, it sets the required precision and
  the deadline.
- **Is this the real question or a tractable stand-in?** Ask directly: *"if I answer
  exactly this, what will you do with it?"* and *"what number would you actually
  quote to someone?"*
- **What is already known?** Search before working. If the field has answered it, the
  deliverable becomes *positioning* — what is supported, what genuinely remains open —
  which is often more valuable and always cheaper.
- **At what level does the claim live?** Description, association, attribution, or
  prediction are four different claims needing different designs and different units.
- **What else could produce the same result?** Confounding, selection, measurement
  artifact, shared construction between cause and outcome. Name them now so the
  design can address them.
- **What is the cheapest observation that could kill it?** Do that first.

> **Worked example — the proxy trap.** A request arrived as *"is this metric novel,
> and does it predict outcome?"* Considerable rigorous work went into exactly that.
> The question actually being asked was *"how much of the effect is attributable to
> the intervention?"* — a different claim, at a different unit, with far stronger
> evidence available. The proxy was answered well and was nearly worthless.

**→ Write the Claim Record.**

### ⛔ FRAME GATE
State back: the falsifiable claim, the decision it serves, the level, prior art, the
top alternative explanation, and the first test. Get confirmation.

---

# PHASE 2 · GROUND

**No analysis yet.** Establish what the evidence can and cannot support.

### Interrogate the source

- **Read the primary description in full**, not its summary. Summaries systematically
  understate or overstate what was captured.
- **Enumerate the source completely before asserting absence.**
  *"I did not find it" is not "it does not exist."* Absence is a claim about the
  whole source; you may only make it after inventorying the whole source.
- **What is one record?** Fix the unit. If the source nests units, say which level
  each quantity lives at — and expect different levels to carry legitimately
  different n.
- **How was this population/sample assembled, and who was left out?** Derive your
  working set as an explicit cascade with a count and a reason at every step.
- **Is your working set the same as the source's?** Compare them. If they differ,
  that is a finding, not a footnote.
- **What is measured directly vs derived vs aggregated?** Aggregated fields may make
  some questions permanently unanswerable — establish that now, not after modelling.
- **Grill the human.** The domain expert knows things the source does not state.
  Ask what exists elsewhere, which definition is in force, what is still open.
  Treat every correction as a Phase-2 defect, not a nuisance.

```bash
python3 scripts/enumerate_source.py <source>   # --grep to check a variable everywhere
```

> **Worked examples.** Absence was twice asserted after inspecting one container of a
> multi-container source; both times the variable existed elsewhere. Separately, the
> working set turned out to be a different population from the source's own — twice
> the severity, majority drawn from records the original authors had excluded — while
> its descriptive statistics were still being quoted from the source.

**→ Write the Evidence Ledger.**

### ⛔ GROUND GATE
State back: units and their mapping, the cascade, working set vs source, what exists,
what is unanswerable. Get confirmation.

> If grounding invalidates the claim, **return to Phase 1**. Do not silently answer a
> different question.

---

# PHASE 3 · TEST

### Pre-specify, then execute

- **Write the interpretation before looking.** For each plausible result, state what
  it would mean and what would follow. Landing on a pre-committed branch is a
  finding; constructing the branches afterwards is a story.
- **Separate outcomes that share construction with the exposure** from those that do
  not. A difference confined to the shared-construction family is an artifact — and
  detecting that is itself a result.
- **Interrogate every denominator.** For each rate, ask who is in it that *cannot*
  exhibit the outcome. They usually do not belong.
- **Run the fatal test first.** Reliability before association; a measure that cannot
  reproduce cannot predict.
- **Inspect your own output.** Rendering and visualisation fail silently. Look at
  every figure; verify every caption against the numbers rather than against intent.

```bash
python3 scripts/check_figure.py <figure> --source <plotting script>
```

> **Worked examples.** A headline moved across four denominators, each revision
> triggered by finally asking who was in it. Four figure defects reached a near-final
> deliverable: axis limits that no longer bracketed the data, binning that silently
> discarded out-of-range values, a hardcoded "n.s." sitting on a significant result,
> and a caption claiming "every" where it held in nine of ten strata.

**→ Update the Evidence Ledger with every correction, as you make them.**

---

# PHASE 4 · CLOSE THE LOOP

The phase most often skipped. Without it the work is not reusable and will be redone.

### Settle the ledger

- **Answer the Phase-1 claim explicitly** — supported, contradicted, or undecided.
  *"Not distinguishable with this evidence"* is a real answer; report it plainly.
- **Separate settled from open.** What is now known, what was ruled out (and by what),
  what remains open and what it would take to close.
- **Put corrections in the artifact.** A number that moved is credible when the moves
  are visible and alarming when discovered later. Regenerate superseded outputs; keep
  the history in prose.
- **Distinguish relative from absolute.** A large relative effect can coexist with
  most events arising in the low-risk group when that group is far bigger. State both.
- **Guard against noise.** With *k* comparisons, one nominal *p* < 0.05 is what chance
  predicts. Report the correction threshold beside it.
- **Name what would change the conclusion**, so the next person knows what to collect.
- **Make it reproducible.** One command per question; dependency-light core; evidence
  stored with the code where licensing allows.

### Report back

When the result touches someone else's work:

1. Lead with what **strengthens** their position
2. Disclose **your own errors first**
3. State the limitation that most threatens **your** result before they find it
4. Frame as *"only you can answer this"* where true — it usually is

**→ Write the Findings Record.**

### ⛔ CLOSE GATE
The loop is closed when someone who was not present can read the three records and
know what was asked, what the evidence could bear, what was found, and what is still
open.

---

## Example Invocations

```
/grill-science-with-docs
```
→ Grills whatever claim is in play, starting at Phase 1

```
/grill-science-with-docs --claim "X drives Y" --evidence data/source.xlsx
```
→ Frames the claim, then grounds it in that source

```
/grill-science-with-docs --close
```
→ Jump to Phase 4 on work already done, to produce the records retrospectively

## Output

Three durable records — **Claim**, **Evidence Ledger**, **Findings** — plus
reproducible analysis and figures that have been inspected.

## Requirements

- `python3` — `enumerate_source.py` is stdlib-only
- `Pillow` *optional* — enables image checks in `check_figure.py`
- **A human at every gate** — this skill does not run unattended

## Skill Structure

```
grill-science-with-docs/
├── SKILL.md
├── README.md
└── scripts/
    ├── enumerate_source.py    # GROUND — inventory before asserting absence
    └── check_figure.py        # TEST — inspect your own output
```
