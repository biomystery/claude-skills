---
name: schedule-c-tracker
description: Organize self-employment income and expenses for U.S. Schedule C — reconciles bank transactions against reported income, categorizes deductions (home office, Section 179, phone/internet), and outputs ready-to-file line values with SE tax and QBI estimates.
user-invocable: true
---

# Schedule C Tracker

Builds a complete Schedule C from raw inputs: bank transaction exports, receipts, and home details. Reconciles gross income against known deposits, categorizes each expense to the correct Schedule C line, calculates home office and vehicle deductions, and outputs expected line values with self-employment tax and QBI deduction estimates.

Handles multiple businesses (e.g., a freelance practice and a side LLC) independently.

## When to Use

- You're self-employed or have a side business and need to organize Schedule C before filing
- You want to reconcile reported gross income against bank deposits
- You have receipts for equipment, home office, phone, or internet and want to know what's deductible
- You want an estimate of SE tax and QBI deduction before getting the final return

## Instructions

### Step 0: Identify Businesses

Ask the user how many Schedule C businesses to track. For each:

```
- Business name (or "sole prop" if no formal entity)
- EIN (if registered) or SSN
- Business type / NAICS code
- Start date (important: first-year losses may attract IRS scrutiny if no revenue)
- Primary income type: services / products / both
```

### Step 1: Reconcile Income

#### Strategy A — Bank Export Available

Read the bank transaction file (CSV, XLS, or PDF):

```
Filter for credits (deposits) in the tax year.
Group by likely business source:
  - Payments from clients/platforms (Venmo Business, Stripe, PayPal, Zelle)
  - 1099-NEC / 1099-K payors
  - Cash payments noted in memo

Sum = tentative gross receipts

Compare to any 1099-NEC or 1099-K received:
  If deposit total > 1099 total → unreported cash income also present (include it)
  If deposit total < 1099 total → check for year-end timing differences
```

#### Strategy B — No Bank Export

Ask the user to provide:
- Total received from each client/payer
- Any 1099-NEC amounts

Gross receipts = sum of all amounts.

#### Income Discrepancy Rule

If reported gross in draft return differs from reconciled amount by > 2%:
- List the top 3 deposit sources and ask user to confirm attribution
- Note: platform fees (e.g., Stripe 2.9%) reduce net deposits but gross receipts should be pre-fee

### Step 2: Categorize Expenses

For each expense the user provides, map to the correct Schedule C line:

| Expense Type | Schedule C Line | Notes |
|---|---|---|
| Advertising, marketing | Line 8 | |
| Car / truck (mileage) | Line 9 | Compute: miles × IRS rate (67¢/mile for 2024, 70¢ for 2025) |
| Commissions paid to others | Line 10 | |
| Contract labor | Line 11 | If paid > $600, may need 1099-NEC |
| Legal / professional fees | Line 17 | |
| Office supplies | Line 18 | Small consumables; larger items → Section 179 |
| Rent (office, equipment) | Line 20a/20b | |
| Repairs / maintenance | Line 21 | |
| Business taxes & licenses | Line 23 | State LLC fees, business licenses, professional dues |
| Travel | Line 24a | Must be overnight and business-purpose |
| Meals (business) | Line 24b | 50% deductible; needs business purpose documented |
| Utilities (dedicated office) | Line 25 | Prorated if home office |
| Wages paid to employees | Line 26 | |
| Phone (business %) | Line 27b | See Step 3 |
| Internet (business %) | Line 27b | See Step 3 |
| Equipment / hardware | Line 27b or Section 179 | See Step 4 |
| Home office | Line 30 | See Step 5 |

### Step 3: Phone and Internet Deduction

```
Deductible amount = annual cost × business-use percentage

Guidelines for business-use %:
  - Phone used primarily for business calls/apps: 50–80%
  - Phone used equally for personal and business: 50%
  - Home internet shared with family: 25–50%
  - Dedicated business line: 100%

Document: keep a representative month's call log or usage stats.

Annual phone cost = monthly plan × 12
Annual internet cost = monthly rate × 12
```

### Step 4: Equipment and Section 179

Section 179 allows immediate expensing of business equipment (no multi-year depreciation):

```
Eligible: computers, phones, software, office furniture used > 50% for business

Deductible amount = purchase price × business-use %

Limit: Section 179 deduction cannot exceed net profit from the business
  (cannot use Section 179 to create a loss — excess carries forward)

List each item:
  Date purchased | Description | Total cost | Business % | Deductible amount
```

### Step 5: Home Office Deduction

Home office is deductible ONLY if the space is used **exclusively and regularly** for business. Cannot be a guest bedroom or shared living space.

#### Method A — Simplified (recommended for most)

```
Deduction = $5 × office square footage
Maximum: 300 sqft → max $1,500/year

Advantage: no recordkeeping of actual home expenses
Limitation: cannot exceed net profit (cannot create a loss)
```

#### Method B — Actual Expense Method

```
Business-use % = office sqft ÷ total home sqft

Deductible portion of:
  - Mortgage interest (or rent)
  - Property taxes
  - Utilities
  - Home insurance
  - Repairs affecting whole home

= each expense × business-use %

Also: dedicated office-only repairs and improvements = 100% deductible

Advantage: higher deduction for large homes with high costs
Disadvantage: requires recordkeeping; mortgage interest/property tax
              already in Schedule A must be allocated
```

Compare both methods and recommend the higher one (if records are available for Method B).

### Step 6: Compute Schedule C Summary

```
Line 1  = Gross receipts (from Step 1)
Line 2  = Returns and allowances (refunds issued to customers)
Line 3  = Line 1 − Line 2
Line 4  = Cost of goods sold (Line 42, if applicable)
Line 5  = Gross profit = Line 3 − Line 4
Line 7  = Gross income (= Line 5 + Line 6)

Lines 8–27b = Individual expense lines (from Step 2–4)
Line 28 = Total expenses (sum of Lines 8–27b)
Line 29 = Tentative profit = Line 7 − Line 28
Line 30 = Home office (from Step 5, limited to Line 29)
Line 31 = Net profit (or loss) = Line 29 − Line 30
```

### Step 7: Self-Employment Tax Estimate

```
SE net earnings = Line 31 × 92.35%  (×0.9235)

SE tax = SE net earnings × 15.3%
  (12.4% Social Security on first $176,100 of SE earnings in 2025 + 2.9% Medicare)

Additional Medicare surtax (0.9%) applies if:
  W-2 + SE income > $250,000 MFJ / $200,000 single

SE tax deduction (Schedule 1 Line 15) = SE tax × 50%
  This reduces AGI.

Net impact on AGI:
  +Line 31 (SE income)
  −SE tax × 50% (SE deduction)
  = Line 31 × ~93% added to AGI (approximately)
```

### Step 8: QBI Deduction Estimate

```
Qualified Business Income (QBI) for this business:
  QBI ≈ Line 31 − SE tax deduction for this business

If multiple businesses:
  Net QBI = sum of all businesses' QBI (losses reduce gains)

QBI deduction = min(20% × net QBI, 20% × taxable income)

Note: QBI deduction is limited to 0 if net QBI is negative.
      A loss-generating business reduces QBI for profitable businesses.
```

### Step 9: Output

Produce a structured summary per business:

```
Schedule C — [Business Name]
─────────────────────────────────────────────
Income
  Gross receipts (Line 1)          : $XX,XXX
  Reconciled vs. bank deposits     : ✅ match / ⚠️ $X,XXX difference

Expenses
  [Line 8]  Advertising            : $X,XXX
  [Line 23] Taxes / licenses       : $X,XXX
  [Line 27b] Other (phone, internet, equipment)
    Internet (XX% of $XXX/mo)      :   $XXX
    Cell phone (XX% of $XX/mo)     :   $XXX
    Equipment — Section 179        : $X,XXX
  [Line 30] Home office (XX sqft)  :   $XXX
  Total expenses                   : $XX,XXX

Net profit (Line 31)               : $XX,XXX

Self-Employment Tax Estimate       :  $X,XXX
SE Deduction (Schedule 1)          :    $XXX
QBI Contribution                   : $XX,XXX
Estimated QBI Deduction (20%)      :  $X,XXX
─────────────────────────────────────────────
```

Flag any items that need receipts or documentation.

## Example Invocations

```
/schedule-c-tracker
```
→ Claude asks for business details, income sources, and expense categories interactively

```
/schedule-c-tracker
(attach: bank_transactions.csv, receipts_folder/)
```
→ Claude reads transactions and receipt PDFs, matches to expense categories

## Output

Per-business Schedule C line values, SE tax estimate, QBI estimate, and a list of items needing receipts or documentation before filing.

## Key Constants (2025)

| Item | Value |
|---|---|
| Standard mileage rate | $0.70/mile |
| Section 179 limit | $1,220,000 (well above typical sole prop needs) |
| SE tax rate | 15.3% (on 92.35% of net profit) |
| SS wage base | $176,100 |
| Home office simplified rate | $5/sqft (max 300 sqft) |
| Additional Medicare surtax | 0.9% over $250K MFJ |

## Hobby Loss Risk

If a business shows a net loss 3+ years out of 5, the IRS may reclassify it as a hobby under IRC §183, disallowing all deductions. Mitigation:
- Keep a business plan, client communications, and evidence of profit intent
- Note any structural reasons for losses (startup phase, one-time large expense)
- Document efforts to improve profitability

## Skill Structure

```
tax/schedule-c-tracker/
├── SKILL.md    (this file)
└── README.md
```
