# data-dictionary

A Claude Code skill that generates a comprehensive markdown data dictionary from any database — combining schema definitions with live SQL statistics, null rates, sample rows, and a Mermaid ER diagram.

## What It Does

- **Auto-detects** schema source: Prisma, SQL DDL, Django models, SQLAlchemy, or live DB introspection (no schema file needed)
- **Multi-database**: SQLite, PostgreSQL, MySQL, DuckDB
- **Rich statistics** per table: row counts, null rates, numeric min/max/mean, categorical distributions, date ranges
- **Sample rows** with automatic PII column redaction (`email`, `birth_date`, `token`, etc.)
- **Mermaid `erDiagram`** rendered natively on GitHub
- **Quick Reference** summary table at the top for fast navigation
- **Update mode** (`--update`): refreshes stats while preserving hand-written descriptions, detects new/removed tables and columns

## Install

```bash
# Clone the claude-skills repo and symlink this skill
git clone https://github.com/biomystery/claude-skills ~/.claude/skills-repo
ln -s ~/.claude/skills-repo/data-dictionary ~/.claude/skills/data-dictionary
```

Or symlink just this skill:

```bash
git clone https://github.com/biomystery/claude-skills /tmp/claude-skills
ln -s /tmp/claude-skills/data-dictionary ~/.claude/skills/data-dictionary
```

Claude Code will auto-detect it on next launch.

## Usage

### Generate (first time)

```
/data-dictionary
```

Claude will ask two quick questions (glossary terms, column exclusions), then auto-detect your schema and database, query live statistics, and write `docs/data_dictionary.md`.

### Custom output path or language

```
/data-dictionary --output reports/schema_ref.md
/data-dictionary --lang zh
/data-dictionary --output docs/db.md --lang es
```

### Update existing dictionary

```
/data-dictionary --update
```

Refreshes all statistics and detects schema changes, while preserving any descriptions you've hand-edited. Prints a structured diff summary:

```
✅ Data dictionary updated: docs/data_dictionary.md

Schema changes detected:
  🆕 New tables (1):    audit_log
  📝 Changed tables (1): users (+1 col)

Statistics refreshed:
  • 18 tables — row counts updated
  • 94 columns — null rates refreshed
```

## Output

A single markdown file (default: `docs/data_dictionary.md`) containing:

- Header with DB engine, schema source, and git commit hash
- Quick Reference table (all tables with row counts)
- Per-table sections: columns, statistics, sample data
- Enumerations section
- Mermaid ER diagram
- Data Quality Notes (flags empty tables, high null rates, type mismatches)
- Glossary (if provided)

## Supported Schema Sources

| Schema | Detection |
|--------|-----------|
| **Prisma** | `prisma/schema.prisma` or `**/*.prisma` |
| **SQL DDL** | `schema.sql` or files with `CREATE TABLE` |
| **Django** | `**/models.py` |
| **SQLAlchemy** | Python files with `Column(`, `relationship(` |
| **None** | Falls back to `PRAGMA table_info` / `information_schema` |

## Requirements

- Claude Code (latest version)
- Database CLI accessible in `PATH`:
  - SQLite: `sqlite3` (built into macOS)
  - PostgreSQL: `psql`
  - MySQL: `mysql`
  - DuckDB: `duckdb`

## Skill Structure

```
data-dictionary/
├── SKILL.md    ← Claude Code skill definition
└── README.md
```
