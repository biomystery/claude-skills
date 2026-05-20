# Update Mode

> Follow this section **instead of Step 5** when `--update` is passed and the output file exists.
> Steps 1–4 (schema detection, DB connection, statistics queries, index collection) run normally first.

## UM-1: Parse the Existing File

Read the existing data dictionary file. Extract and store:

**Preserved content** (do NOT overwrite):
- `**Description**:` prose for every table section (`### \`table_name\``)
- The `Description` column values for every row in every `#### Columns` table
- The entire `## Glossary` section
- Any content in table sections that is NOT one of the refreshable blocks listed below

**Refreshable blocks** (will be replaced with fresh data):
- Header metadata lines: `**Generated**:`, `**Schema source**:`
- `**Row count**:` line in every table section
- The `Null rate: X%` suffix within Description column cells
- The entire `#### Statistics` block for every table
- The entire `#### Sample Data` block for every table
- The entire `## Quick Reference` table (row counts change)
- The entire `## Data Quality Notes` section
- The entire `## Entity Relationship Diagram` section (regenerate if schema changed)

## UM-2: Diff Schema — Detect Changes

Compare the current schema (from Steps 1–4) against the tables and columns found in the existing file.

Build three lists:

| List | Contents |
|------|----------|
| **New tables** | Tables in current schema NOT present in existing file |
| **Removed tables** | Tables in existing file NOT present in current schema |
| **Changed tables** | Tables present in both, but with added or removed columns |

For changed tables, also build:
- **New columns**: columns in current schema not in existing file
- **Removed columns**: columns in existing file not in current schema

## UM-3: Merge & Write

Construct the updated file by:

1. **Update the header**:
   - Replace `**Generated**:` with today's date
   - Replace `**Schema source**:` with the current git hash
   - Add `**Last updated**:` if not present

2. **Refresh the Quick Reference table**: rewrite row counts from fresh queries.

3. **For each existing table** (present in both old file and current schema):
   - Keep `**Description**:` prose unchanged
   - Rewrite `**Row count**:` with fresh count
   - In the `#### Columns` table: keep each row's `Description` cell text, but update `Null rate: X%` suffix with fresh null rate; update `Type`, `Nullable`, `Default`, `Indexed` from current schema
   - Replace the entire `#### Statistics` block with fresh data
   - Replace the entire `#### Sample Data` block with fresh data (re-run sample query, re-apply PII redaction)

4. **For each new table** (in schema but not in existing file):
   - Append a full new table section at the end of its domain group (or at the end of the file if domain grouping is ambiguous)
   - Add a `> 🆕 **New** — added since last update` callout directly below the `### \`table_name\`` heading
   - Generate all content (columns, statistics, sample data) fresh

5. **For each removed table** (in existing file but not in current schema):
   - Keep the section in the file but add a prominent callout directly below the heading:
     ```
     > ⚠️ **Removed** — this table no longer exists in the schema as of <YYYY-MM-DD>. Section preserved for reference.
     ```
   - Do NOT delete the section or its content

6. **For each new column** in a changed table:
   - Append a new row to the `#### Columns` table
   - Add `🆕` prefix to the Description cell: `🆕 <generated description>`

7. **For each removed column** in a changed table:
   - Keep the row in the `#### Columns` table
   - Replace the Description cell content with: `⚠️ Column removed from schema as of <YYYY-MM-DD>. Previous description: <original description>`

8. **ER Diagram**:
   - If the existing file has **no Mermaid `erDiagram` block** (e.g. it was generated before this feature was added) → **always generate and add it**, regardless of schema changes.
   - If the existing file already has an `erDiagram` block → regenerate only if the set of tables or foreign keys changed. Otherwise keep it unchanged.

9. **Refresh `## Data Quality Notes`** entirely with fresh anomaly detection.

## UM-4: Print Update Summary

After writing the file, print a concise summary to the user:

```
✅ Data dictionary updated: docs/data_dictionary.md

Schema changes detected:
  🆕 New tables (2):    audit_log, feature_flags
  ⚠️  Removed tables (1): legacy_imports
  📝 Changed tables (3): users (+2 cols), measurements (-1 col), etl_runs (+1 col)

Statistics refreshed:
  • 18 tables — row counts updated
  • 94 columns — null rates refreshed
  • 12 tables — numeric stats updated
  • 18 tables — sample data refreshed

No schema changes: ER diagram unchanged.
```

If there are no schema changes:
```
✅ Data dictionary updated: docs/data_dictionary.md

No schema changes detected — statistics refreshed only.
  • 18 tables — row counts updated
  • 94 columns — null rates refreshed
```
