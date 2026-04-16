---
name: tax-draft-review
description: Audit a U.S. Form 1040 draft return against known income documents — catches missing 1099-Rs, wrong IRA basis, omitted Schedule C deductions, and SALT errors before filing.
user-invocable: true
---

# Tax Return Draft Review

Reads a tax return draft PDF and cross-references it against the user's known income and deduction documents. Produces a prioritized error report — must-fix issues first — with the exact line numbers and corrected values needed before filing.

Designed for taxpayers who self-prepare or receive a preparer draft and want an independent audit before submission.

## When to Use

- You have a draft Form 1040 (PDF) and want to verify it before filing
- You switched tax preparers and want to double-check their work
- You have complex inputs (multiple 1099-Rs, backdoor Roth, self-employment) where errors are common
- Invoke after gathering all income documents for the year

## Instructions

### Step 0: Collect Documents

Ask the user to provide (or attach):

```
Required:
- Draft tax return PDF

Cross-reference documents (attach or describe):
- W-2(s) for all jobs
- 1099-R(s) for all IRA/retirement distributions
- 1099-INT for each bank (or note which banks had interest)
- 1099-DIV / consolidated 1099 from brokers
- Schedule C income/expense records (if self-employed)
- Prior year tax return (for carryovers: capital loss, IRA basis)
```

### Step 1: Read the Draft Return

Read the draft PDF. Extract and record:

```
Form 1040:
  Line 1a  (W-2 wages)
  Line 2b  (taxable interest)
  Line 3b  (ordinary dividends)
  Line 4a  (IRA distributions, gross)
  Line 4b  (IRA distributions, taxable)
  Line 7a  (capital gains/losses)
  Line 8   (other income from Schedule 1)
  Line 11  (AGI)
  Line 12e (deductions — standard or itemized)
  Line 13a (QBI deduction)
  Line 15  (taxable income)
  Line 16  (tax)
  Line 19  (child tax credit)
  Line 24  (total tax)
  Line 25d (total withholding)
  Line 34/35a (refund) or Line 37 (owed)

Schedule B (if present): each interest payer and amount
Schedule C (if present): gross income, total expenses, net profit per business
Schedule D: short/long term capital gain/loss, carryover used
Form 8606 (if present): Lines 1, 2, 8, 18 per filer
```

### Step 2: Verify Income Completeness

#### 2a: W-2 Wages
Compare draft Line 1a to sum of all W-2 Box 1 amounts.

#### 2b: IRA / Retirement Distributions (Line 4a)
Build expected Line 4a:
```
For each 1099-R received:
  - Code G (401k rollover)   → include in 4a, mark "Rollover", NOT taxable
  - Code 2 (Roth conversion) → include in 4a, taxable per Form 8606 Line 18
  - Code 7 (normal dist.)    → include in 4a, likely taxable

Expected Line 4a = sum of all 1099-R gross distribution amounts

⚠️ For joint returns: verify BOTH spouses' 1099-Rs are included.
   A missing spouse conversion will trigger IRS CP2000 notice.
```

#### 2c: Interest Income (Schedule B)
List all banks/brokers where interest ≥ $10 was expected. Check:
- Is each institution present in Schedule B?
- Note any mergers (e.g., bank A acquired bank B — combined under new name)
- Fidelity CMA accounts may report interest separately from investment income

#### 2d: Dividend Income (Schedule B Part II)
Check consolidated 1099 from each broker for ordinary and qualified dividends.

#### 2e: Capital Gains (Schedule D)
- Verify prior year capital loss carryover appears in Line 6 (short-term) or Line 14 (long-term)
- Check carryover amount from prior year Schedule D Line 16 or Capital Loss Carryover Worksheet

### Step 3: Verify Form 8606 (Backdoor Roth)

If any 1099-R Code 2 (Roth conversion) exists:

```
Check per filer:
  Line 1  = contributions for THIS tax year only (not prior-year contributions
             made in spring — those go on prior year's Form 8606)
  Line 2  = prior year Form 8606 Line 14  ← most commonly left blank
  Line 6  = actual Dec-31 IRA balance (not $0 if interest accumulated)
  Line 8  = Code 2 conversion amount ONLY (never include Code G here)
  Line 18 = should be $0 for clean backdoor Roth

Expected Line 4b = sum of both filers' Form 8606 Line 18
```

Flag any mismatch. See `/backdoor-roth-review` for full computation.

### Step 4: Verify Deductions

#### 4a: Standard vs. Itemized
```
Compute itemized total:
  Schedule A Line 7  (SALT: state tax + property tax, cap applies)
  Schedule A Line 10 (mortgage interest)
  Schedule A Line 14 (charitable contributions)
  Schedule A Line 17 (total)

SALT cap:
  2024: $10,000 MFJ
  2025: $40,000 MFJ  ← raised by legislation
  CA property tax + state income tax may exceed cap in high-tax states

If itemized > standard deduction → itemizing is correct.
Standard deductions (MFJ): 2024: $29,200 | 2025: $31,500
```

#### 4b: QBI Deduction (Form 8995)
If self-employed:
- Net QBI = sum of Schedule C net profits minus losses across all businesses
- QBI deduction = min(20% × net QBI, income limitation)
- A net loss in one business reduces QBI for all businesses

### Step 5: Verify Self-Employment (Schedule C)

For each Schedule C business:
```
Check:
  Line 1  (gross receipts) vs. known income (1099-NEC + cash receipts)
  Line 27b (other expenses) — common omissions:
    - Home office (Line 30): simplified = $5/sqft × dedicated office sqft
    - Equipment (Section 179): one-time deduction for business hardware
    - Internet / phone: only deductible business-use percentage
    - Vehicle mileage (if used for business)
  Line 30 (home office): if 0, check whether office meets "exclusive use" test

Note: home office deduction cannot exceed net profit (cannot create a loss).
```

### Step 6: Cross-Check Key Arithmetic

```
AGI = Total income − Schedule 1 adjustments
    = (Line 9) − (Line 10)

Taxable income = AGI − deductions − QBI
    = Line 11b − Line 12e − Line 13a

Total tax = Tax on taxable income − credits + other taxes
    = Line 16 − Line 19 (CTC) + Line 23 (SE tax + NIIT + AMT)

Refund = Total withholding − Total tax
    = Line 25d − Line 24
```

If any check fails by more than $10, flag it.

### Step 7: Produce Error Report

Output a prioritized report:

```
## Tax Draft Review — [Tax Year]

### 🔴 Must Fix Before Filing
(Each item includes: what's wrong, correct value, affected lines, ~tax impact)

### 🟡 Recommended
(Missed deductions, minor omissions — include estimated refund impact)

### 🟢 Verified Correct
(Confirmed items — gives the user confidence in what the preparer got right)

### 📊 Summary
  Draft refund:    $X,XXX
  After fixes:     ~$X,XXX  (estimated)
  Net improvement: ~$XXX
```

## Example Invocations

```
/tax-draft-review
```
→ Claude asks for the draft PDF and known documents

```
/tax-draft-review
(attach: TaxReturn_draft.pdf, W2_primary.pdf, 1099R_fidelity.pdf)
```
→ Full automated cross-reference

## Output

A structured error report with:
- Must-fix issues (with line numbers, wrong value, correct value, tax impact)
- Recommended additions (missed deductions)
- Confirmed-correct items
- Estimated refund improvement after all fixes

## Common Errors Caught

| Error | Typical Impact | Detection Method |
|---|---|---|
| Spouse 1099-R missing from Line 4a | CP2000 IRS notice | Check all 1099-Rs vs Line 4a total |
| Form 8606 Line 2 blank | $1,000–$2,000+ tax overpayment | Compare to prior year Line 14 |
| Code G rollover in Roth conversion amount | Phantom taxable income | Check 1099-R code classification |
| Capital loss carryover not used | Extra ~$660 tax (at 22%) | Check prior year Sch D Line 21 |
| Home office Line 30 = $0 | Missed $150–$500 deduction | Verify sqft and exclusive use |
| Missing bank interest (merged institution) | Underreported income | Cross-reference all bank accounts |
| SALT cap applied incorrectly | Wrong deduction amount | Recompute with correct year cap |

## Requirements

- Claude Code with PDF reading capability
- Draft tax return PDF (text-based, not scanned)
- At least W-2 and 1099-R documents for cross-reference

## Skill Structure

```
tax/tax-draft-review/
├── SKILL.md    (this file)
└── README.md
```
