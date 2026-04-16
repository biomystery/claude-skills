---
name: backdoor-roth-review
description: Verify Form 8606 for a backdoor Roth IRA conversion — checks Line 1/2 basis, Code G vs Code 2 separation, pro-rata calculation, and Form 1040 Line 4a/4b — and outputs the expected value for every line.
user-invocable: true
---

# Backdoor Roth IRA Review

Audits a backdoor Roth IRA conversion for a given tax year. Given broker transaction records and the prior year's Form 8606 Line 14, it computes the expected value for every Form 8606 line, flags the most common preparer errors, and verifies that Form 1040 Lines 4a/4b are consistent.

Works for both spouses independently (each files their own Form 8606).

## When to Use

- You or your preparer just completed a backdoor Roth conversion and want to verify Form 8606 is correct
- Reviewing a tax return draft and suspecting an IRA error
- AGI exceeds the Roth IRA direct contribution limit (~$240K MFJ in 2025) and you used the nondeductible Traditional IRA → conversion route

## Instructions

### Step 0: Gather Inputs

Ask the user for the following (or read from provided documents):

```
Per person (file separately for each spouse):

1. Prior year Form 8606 Line 14  →  carryover basis
2. Broker transaction log for current year Traditional IRA:
   - Date and amount of any contributions (note if "PRIOR YEAR" / current year)
   - 1099-R entries: Code G amounts (rollover to 401k) and Code 2 amounts (Roth conversion)
3. Traditional IRA balance on December 31 of the tax year
4. Any other pre-tax Traditional IRA balances at year-end (SEP-IRA, SIMPLE IRA)
```

If reviewing a draft return, also read the Form 8606 from the PDF.

### Step 1: Classify 1099-R Transactions

**This is the single most common source of error.**

| 1099-R Code | Meaning | Taxable? | Goes into Form 8606? |
|---|---|---|---|
| **G** | Direct rollover to qualified plan (401k, 403b) | No | No — not a Roth conversion |
| **2** | Early distribution, exception applies (Roth conversion) | Only if no basis | Yes — Line 8 |
| **7** | Normal distribution | Yes unless basis | Yes — Line 7 |

> **Critical rule**: Code G amounts must NEVER appear in Form 8606 Line 8. If a preparer software lumps Code G + Code 2 together into Line 8, Line 18 will show phantom taxable income.

Verify: sum of Code 2 amounts = the intended Roth conversion amount.

### Step 2: Determine Form 8606 Part I Line Values

```
Line 1  = New nondeductible contributions for THIS tax year
          (NOT contributions made in current calendar year for PRIOR tax year —
           those belong on the prior year's Form 8606)

Line 2  = Prior year Form 8606 Line 14 (carryover basis)
          ⚠️ Most common omission — preparer software often leaves this blank

Line 3  = Line 1 + Line 2

Line 4  = Contributions included in Line 1 that were made Jan 1 – Apr 15
          of the FOLLOWING year (backdoor contributions made in spring)

Line 5  = Line 3 − Line 4

Line 6  = Traditional IRA fair market value on December 31 of tax year
          ⚠️ Use actual broker statement value — NOT $0 even if nearly empty
          (small interest accumulation after conversion leaves a non-zero balance)

Line 7  = Traditional IRA distributions (not rollovers, not conversions)

Line 8  = Net amount converted to Roth IRA (Code 2 only)

Line 9  = Line 6 + Line 7 + Line 8

Line 10 = Line 5 ÷ Line 9   →  round to 3 decimal places
          If result ≥ 1.000, enter 1.000
          ⚠️ Rounding matters: 0.9997 rounds UP to 1.000 (no taxable amount)
                               0.9994 rounds DOWN to 0.999 (small taxable amount)

Line 11 = Line 8 × Line 10  (nontaxable portion of conversion)

Line 13 = Line 11 + Line 12 (Line 12 = nontaxable portion of distributions)

Line 14 = Line 3 − Line 13  (basis carryforward to next year)
          Should equal remaining IRA balance × ratio; near $0 if fully converted
```

### Step 3: Compute Expected Line 10 and Check for Pro-Rata Risk

```
if Line 9 == 0:
    # No basis, no distributions, no conversion — skip Part I
elif Line 5 >= Line 9:
    Line 10 = 1.000  → Line 18 = $0  ✅
else:
    ratio = Line 5 / Line 9
    Line 10 = round(ratio, 3)  # standard rounding
    if Line 10 >= 1.000:
        Line 10 = 1.000  → Line 18 = $0  ✅
    else:
        Line 11 = Line 8 × Line 10  (truncate cents)
        Line 18 = Line 8 − Line 11  ← taxable amount
```

**Pro-rata risk exists when**: pre-tax Traditional IRA funds are still in the account at year-end. Common cause: prior 401k funds rolled into IRA not yet moved out.

**Mitigation**: Roll pre-tax IRA funds into employer 401k by December 31 of the tax year (IRS looks at year-end balance, not conversion-date balance).

### Step 4: Compute Form 8606 Part II

```
Line 16 = Net amount converted (same as Line 8)
Line 17 = Line 11 (nontaxable basis applied to this conversion)
Line 18 = Line 16 − Line 17  →  should be $0 for clean backdoor Roth
```

If Line 18 > $0, identify the cause:
- Line 2 blank (missing carryover basis) → add prior year Line 14
- Line 6 non-zero causing ratio < 1.000 → de minimis if < $10, explain to user
- Code G mixed into Line 8 → remove rollover amount from Line 8

### Step 5: Verify Form 1040 Lines 4a and 4b

```
Line 4a = ALL IRA distributions (gross):
          Code G rollover + Code 2 Roth conversion + any regular distributions
          Check box "Rollover" next to Line 4a if Code G is present

Line 4b = Taxable amount = Form 8606 Line 18
          (or sum of both spouses' Line 18 values for joint return)

⚠️ If filing jointly: BOTH spouses' 1099-R amounts must appear in Line 4a.
   A common error is omitting one spouse's conversion entirely.
```

### Step 6: Output Expected Values

Present a table for each filer:

```
Form 8606 — [Filer Name]
─────────────────────────────────────────────
Part I
  Line 1  (new contributions)      : $X,XXX
  Line 2  (carryover basis)        : $X,XXX  ← verify not blank
  Line 3                           : $X,XXX
  Line 5                           : $X,XXX
  Line 6  (IRA year-end balance)   : $X.XX   ← use actual, not $0
  Line 8  (Roth conversion)        : $X,XXX  ← Code 2 only
  Line 9                           : $X,XXX
  Line 10 (ratio)                  : X.XXX
  Line 11 (nontaxable conversion)  : $X,XXX
  Line 14 (carryover to next year) : $XX

Part II
  Line 16                          : $X,XXX
  Line 17                          : $X,XXX
  Line 18 (TAXABLE — target $0)    : $X

Form 1040
  Line 4a (gross IRA distributions): $XX,XXX
  Line 4b (taxable IRA)            : $X
─────────────────────────────────────────────
```

Flag any line that differs from the draft return.

### Step 7: Carryforward Note

State explicitly what next year's Form 8606 Line 2 should be (= this year's Line 14).

If Line 14 = $0 after a full conversion with no remaining balance:
> "No basis carries forward. A new nondeductible contribution must be made next year to continue the backdoor Roth strategy."

## Example Invocations

```
/backdoor-roth-review
```
→ Claude asks for prior year Line 14, current year transactions, and year-end balances

```
/backdoor-roth-review
(attach: Fidelity_IRA_transactions.csv, TaxReturn_draft.pdf)
```
→ Claude reads both files and compares expected vs. draft values

## Output

Per-filer table of expected Form 8606 line values, comparison with draft if provided, and a prioritized list of discrepancies.

## Key Constants (2025)

| Item | Value |
|---|---|
| IRA contribution limit (under 50) | $7,000 |
| IRA contribution limit (50+) | $8,000 |
| Roth direct contribution phase-out (MFJ) | $236,000 – $246,000 |
| Pro-rata rule trigger | Any pre-tax Traditional/SEP/SIMPLE IRA balance at Dec 31 |

## Common Errors Caught by This Skill

| Error | Impact | Fix |
|---|---|---|
| Code G rollover amount included in Line 8 | Phantom taxable income equal to rollover amount | Remove Code G from Line 8 |
| Line 2 blank (no carryover basis) | Line 18 > $0, overpayment of tax | Enter prior year Form 8606 Line 14 |
| Line 6 = $0 when IRA has small year-end balance | Incorrect pro-rata (minor) | Enter actual Dec-31 balance |
| One spouse's 1099-R missing from Form 1040 Line 4a | IRS CP2000 mismatch notice | Add missing 1099-R to return |
| Line 1 shows prior-year contribution made in spring | Wrong year attribution | Move to prior year's Form 8606 |

## Skill Structure

```
tax/backdoor-roth-review/
├── SKILL.md    (this file)
└── README.md
```
