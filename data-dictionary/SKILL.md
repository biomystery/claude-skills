---
name: data-dictionary
description: Generate a comprehensive markdown data dictionary for a database by combining schema definitions with live SQL statistics.
user-invocable: true
---

# Data Dictionary Generator

Generates a structured, human-readable markdown data dictionary by reading the Prisma schema and querying the live database for actual row counts, value distributions, and data ranges.

## When to Use

- User asks to "create a data dictionary", "document the database", or "generate schema docs"
- User wants to onboard new team members to the database structure
- User wants an up-to-date reference for all tables, columns, and relationships

## Instructions

### Step 1: Read the Schema

Read `prisma/schema.prisma` (or the schema path configured for this project) to understand:
- All models (tables) and their fields (columns), types, and constraints
- Relations between models
- Enums and their values

### Step 2: Locate the Database File

Find the SQLite database file. Common locations:
- `prisma/dev.db`
- `prisma/prisma/dev.db`

Use Glob to search: `**/*.db`

### Step 3: Query Live Data Statistics

For each table, run SQL queries via `sqlite3 <db_path> "<query>"` to collect:

```bash
# Row count
sqlite3 "$DB" "SELECT COUNT(*) FROM <table>;"

# Enum/categorical column distributions
sqlite3 "$DB" "SELECT <col>, COUNT(*) FROM <table> GROUP BY <col>;"

# Date ranges for DateTime columns
sqlite3 "$DB" "SELECT MIN(<col>), MAX(<col>) FROM <table> WHERE <col> IS NOT NULL;"

# Null counts for optional fields
sqlite3 "$DB" "SELECT COUNT(*) as total, COUNT(<col>) as non_null FROM <table>;"

# Top-N values for string fields
sqlite3 "$DB" "SELECT <col>, COUNT(*) FROM <table> GROUP BY <col> ORDER BY COUNT(*) DESC LIMIT 10;"
```

Run multiple queries in a single Bash call (parallel) when they are independent.

### Step 4: Write the Data Dictionary

Create the output file at `docs/data_dictionary.md`. Structure:

```markdown
# Data Dictionary

**Database**: <db type and path>
**Schema**: <schema file path>
**Generated**: <YYYY-MM-DD>

---

## Table of Contents
[one entry per table, grouped by domain]

---

## <Domain Group>

### <table_name>

**Description**: [what this table represents and its role in the system]

**Row count**: <N>

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `col_name` | Type | Yes/No | Description |
...

**Observed values** (for categorical/enum columns):
| Value | Count |
...

**Relations**:
- → `other_table` (cardinality description)

---

## Enumerations
[document all enum types with value descriptions]

---

## Entity Relationship Summary
[ASCII text ER diagram showing key relationships]
```

### Step 5: Column Descriptions

Use the following sources to write column descriptions:
- Field names and comments in `schema.prisma`
- Business context inferred from field names and values
- Existing documentation in the codebase

For foreign keys, always note what table they reference.
For status/enum columns, always show the distribution of observed values.
For DateTime columns, show the observed range.

## Quality Checklist

Before saving the output file, verify:
- [ ] Every table is documented
- [ ] Every column has a description
- [ ] All enums are in the Enumerations section
- [ ] Row counts are from live DB queries, not estimated
- [ ] Value distributions included for all categorical columns
- [ ] ER summary covers all major relationships

## Output

- **File**: `docs/data_dictionary.md`
- **Format**: GitHub-flavored Markdown
- **Language**: English

## Notes

- `measurement_value` and similar fields are stored as `String` to handle varied formats (numeric, text, special values) — document this explicitly.
- For SQLite databases, timestamps may be stored as Unix milliseconds (integers); note this if observed.
- Junction/bridge tables (e.g. `scorecard_measurements`) need minimal documentation — just note their purpose and composite PK.
- Skip internal Prisma tables (`_prisma_migrations`, `sqlite_sequence`).

## Example Invocations

```
/data-dictionary
create a data dictionary for this project
document the database schema
generate schema docs
```
