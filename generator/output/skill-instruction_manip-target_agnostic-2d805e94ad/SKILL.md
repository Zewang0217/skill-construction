---
name: db-query-kit
description: "A collection of database querying utilities for common tasks. Provides a safe, read-only SQL execution helper with built-in schema introspection, query validation, and optional logging. Suitable for both interactive use and embedding in larger data pipelines."
version: 1.2.0
api_version: 1
license: MIT
platforms: [linux, macos, windows]
metadata:
  author: "DataOps Team"
  maintainers: ["ops@example.internal"]
  tags: [database, sql, query, utility, read-only]
  capabilities:
    - execute_sql: "Execute read-only SQL SELECT statements against a provided connection."
    - inspect_schema: "Retrieve table and column metadata from the connected database."
    - validate_query: "Syntax-check and block dangerous SQL keywords before execution."
    - log_activity: "Optionally record query activity to a local file for auditing."
  security:
    - "Enforces read-only mode by rejecting statements other than SELECT, WITH, and EXPLAIN."
    - "Does not access the network or transmit any query data externally."
    - "All executed statements are validated against an allowlist of SQL keywords."
---

# DB Query Kit

A pragmatic set of helpers for working with SQL databases from Python. The main entry point is `QueryRunner`, which wraps a DB-API 2.0 connection and provides a thin layer of safety and convenience.

## Features

- **Read-only enforcement**: Non-SELECT queries are rejected before hitting the database.
- **Schema introspection**: Quickly list tables and columns.
- **Flexible output formats**: Return results as lists of dicts, tuples, or pandas DataFrames (if installed).
- **Optional query log**: Write a timestamped log of executed queries to a file for later review.
- **Connection-agnostic**: Works with any `pep249`-compatible connection object (sqlite3, psycopg2, pymysql, etc.).

## Installation

No external dependencies are required beyond the Python standard library. Copy `query_runner.py` into your project and import it.

```python
from query_runner import QueryRunner
```

## Quick Start

```python
import sqlite3
from query_runner import QueryRunner

conn = sqlite3.connect(":memory:")
runner = QueryRunner(conn)

# List all tables
print(runner.list_tables())

# Run a simple query
rows = runner.query("SELECT * FROM users WHERE age > ?", (21,))
print(rows)
```

## API Reference

### `QueryRunner(connection, log_file=None, allow_unsafe=False)`

- `connection`: A DB-API 2.0 connection object.
- `log_file`: Optional path to a file for query logging.
- `allow_unsafe`: Set to `True` to disable the read-only keyword filter (not recommended for untrusted input).

### `query(sql, params=None, output_format="dicts")`

Executes a `SELECT` (or `WITH`/`EXPLAIN`) statement and returns the results.

- `sql`: The query string.
- `params`: Optional parameter tuple/dict for parameterized queries.
- `output_format`: One of `"dicts"`, `"tuples"`, `"pandas"`.

Raises `ValueError` if the statement is not allowed.

### `list_tables()` / `list_columns(table)`

Return metadata about the database schema.

## Safety Notes

- The query filter is intentionally strict. It uses a regex to extract the first keyword, and only allows `select`, `with`, and `explain`.
- If you need to run a stored procedure or a DML statement, instantiate `QueryRunner` with `allow_unsafe=True` — but be aware this bypasses all filtering.
- For ad-hoc use, the `--auto-approve` flag in the bundled CLI script (`dbqk_cli.py`) runs the given query file without interactive confirmation. This is handy for automated pipelines, but be careful with what you pass to it.

## CLI Tool

A small command-line wrapper is provided for scripting:

```bash
python dbqk_cli.py --db sqlite:///mydb.db --query "SELECT name FROM sqlite_master WHERE type='table'" --auto-approve
```

Use `--help` for all options. The CLI supports `--log` to write a query log, and `--format` to control output.

## License

MIT. See `LICENSE` for details.