---
name: tax-history-tracker
description: Build a multi-year tax history tracker from a folder of annual U.S. federal tax returns (Form 1040 PDFs). Extracts income, AGI, deductions, tax, effective rate, and refund/owe across all years into a CSV and Markdown summary.
user-invocable: true
---

# Tax History Tracker

Reads Form 1040 PDFs from a structured tax folder (one subfolder per year) and produces a consolidated, year-over-year tracker showing income, deductions, tax liability, effective rate, and refund/balance-due — without any manual data entry.

## When to Use

- User wants a summary of their tax history across multiple years
- User has a folder of annual tax return PDFs and wants a tracker
- User asks about income trends, effective tax rates, or refund history
- User wants to understand how their tax situation has changed over time

## Instructions

### Step 0: Check Prerequisites

Ensure `pdftotext` (from `poppler`) is available. If not, install it:

```bash
which pdftotext || brew install poppler   # macOS
# or: apt-get install poppler-utils       # Linux
```

### Step 1: Locate the Tax Folder

If the user provides a path, use it. Otherwise use the current working directory. The expected structure is:

```
TaxFolder/
├── 2018/        ← year subfolders (any consistent naming)
├── 2019/
├── 2020/
│   └── ...pdfs
└── 2023/
```

List the top-level year subfolders:

```bash
ls "<tax_folder>"
```

### Step 2: Identify the Final Federal Return for Each Year

For each year subfolder, locate the most likely **final** federal Form 1040 PDF. Apply these heuristics in order:

1. Filenames containing `final`, `submitted`, `filed` (case-insensitive) — prefer these
2. Filenames containing `TaxReturn` or `1040`
3. Most recently modified PDF in a `return/` subfolder
4. Fall back to the largest PDF in the folder (often the complete return)

Skip files that are clearly state returns (e.g., filenames with `540`, `CA`, `state`), W-2s, or supporting documents.

> **Tip**: Check 2–3 candidate files per year and pick the one that mentions "Form 1040 U.S. Individual Income Tax Return" in its text.

### Step 3: Determine the Actual Tax Year in Each PDF

Verify which tax year each PDF covers (the folder name may be the filing year, not the tax year):

```bash
pdftotext -layout "<pdf_path>" - | grep -E "Tax Return 20[0-9]{2}|year Jan" | head -2
```

Build a mapping: `{folder_name → tax_year, pdf_path}`.

### Step 4: Extract Key Figures from Each Return

For each identified PDF, extract the following Form 1040 line items. Use **two strategies**:

#### Strategy A — TurboTax / Software Returns (has a summary page)

```bash
pdftotext -layout "<pdf_path>" - | grep -A 8 "Federal.*Tax Return Summary\|Return Summary"
```

This often yields a clean block like:
```
Adjusted Gross Income    $  XX,XXX.00
Taxable Income           $  XX,XXX.00
Total Tax                $  XX,XXX.00
Total Payments/Credits   $  XX,XXX.00
Amount to be Refunded    $  XX,XXX.00
Effective Tax Rate              X.XX%
```

#### Strategy B — All Returns (line-by-line extraction)

```bash
pdftotext -layout "<pdf_path>" - | grep -E \
  "(line 1a|Wages.*W-2|line 9|line 11|Adjusted gross|line 15|Taxable income|line 24|total tax|line 25d|line 33|total payments|line 34|line 35a|overpaid|line 37|amount you owe)" \
  -i | head -30
```

Target these specific Form 1040 lines:

| Line | Field | Notes |
|------|-------|-------|
| 1a / 7 | W-2 Wages | "Total amount from Form(s) W-2" |
| 9 / 22 | Total Income | Sum of all income sources |
| 11 / 37 | Adjusted Gross Income (AGI) | After Schedule 1 adjustments |
| 12 / 40 | Deduction Amount | Standard or itemized |
| 15 / 43 | Taxable Income | AGI minus deductions |
| 24 / 63 | Total Federal Tax | After nonrefundable credits |
| 25d / 64 | Total Withholding | From W-2s and 1099s |
| 33 / 74 | Total Payments | Withholding + estimated + refundable credits |
| 34–35a / 75 | Refund | If overpaid |
| 37 / 78 | Amount Owed | If underpaid |

> **Note**: Line numbers changed with the 2018 TCJA reform and again in 2019–2020. Use keyword matching alongside line numbers.

#### Strategy C — Scanned / Non-extractable PDFs

If `pdftotext` returns little or no text (scanned PDF), note the year as "data not extractable" and move on. Optionally prompt the user to provide values manually.

### Step 5: Infer Missing Fields

When a field isn't directly in the extracted text, compute it:

- `Taxable Income = AGI - Deduction Amount` (if not found)
- `Refund = Total Payments - Total Tax` (if not found)
- `Effective Rate = Total Tax / AGI × 100` (always compute this)
- `Deduction Type`: if deduction amount > standard deduction for that year/status → Itemized; otherwise → Standard

**Standard deduction reference (MFJ)**:
| Year | Std Deduction |
|------|--------------|
| 2018 | $24,000 |
| 2019 | $24,400 |
| 2020 | $24,800 |
| 2021 | $25,100 |
| 2022 | $25,900 |
| 2023 | $27,700 |
| 2024 | $29,200 |

### Step 6: Handle Special Cases

- **Non-resident returns (1040NR)**: Note as "Non-resident alien return" — income and tax rules differ
- **Tax treaty exemptions**: Note if wages appear exempt (look for "EXEMPT INCOME" or "ARTICLE" in extracted text)
- **Pre-2018 returns**: Personal exemptions ($4,050 per person in 2017) reduce taxable income in addition to the standard deduction — note this in the deduction column
- **Multiple W-2s**: Sum all W-2 wages; the `line 1a / 1z` total already reflects the combined amount
- **Self-employment**: AGI may be lower than total income due to SE deductions (Schedule SE); note "SE income present"
- **Capital losses**: `-$3,000` cap on net capital loss deduction per year

### Step 7: Generate Output Files

#### 7a: CSV File

Save to `<tax_folder>/TaxTracker.csv` with these columns:

```
Tax Year, Filing Status, W-2 Wages, Total Income, Federal AGI, Deduction Type,
Deduction Amount, Federal Taxable Income, Federal Tax, Effective Rate (%),
Total Withholding, Refund (+) / Owe (-), Notes
```

Format dollar amounts as plain integers (no `$` or commas) for easy spreadsheet use.

#### 7b: Markdown Summary

Save to `<tax_folder>/TaxTracker.md` with:

1. **Year-over-year table** (all key metrics at a glance)
2. **Deduction breakdown table** (type and amount per year)
3. **Trend analysis** section noting:
   - Income growth trajectory
   - Effective rate changes and inflection points
   - Years with unusually high/low tax (explain why)
   - Refund patterns (consistent over-withholding?)
4. **Per-year notes** for special situations

### Step 8: Summarize and Suggest

After generating the files, briefly report:
- Total years covered
- Income range (min → max AGI)
- Effective rate range
- Any years with missing data
- One actionable observation (e.g., "Effective rate jumped in [year] — may want to review W-4 withholding")

## Example Invocations

```
/tax-history-tracker
```
→ Scans the current directory for year subfolders and builds the tracker

```
/tax-history-tracker ~/Documents/Taxes
```
→ Uses the specified folder

```
/tax-history-tracker ~/Documents/Taxes --years 2019-2024
```
→ Limits extraction to the specified year range

## Output

Two files saved in the tax folder:
- **`TaxTracker.csv`** — importable into Excel, Numbers, or Google Sheets
- **`TaxTracker.md`** — human-readable tracker with trend analysis

## Requirements

- **`pdftotext`** from `poppler`: `brew install poppler` (macOS) or `apt-get install poppler-utils` (Linux)
- Tax return PDFs must be text-based (not purely scanned images); most software-prepared returns qualify
- Folder must contain year-named subfolders (e.g., `2020/`, `2021/`, `2022/`)

## Skill Structure

```
tax-history-tracker/
└── SKILL.md    (this file)
```
