---
name: db-query-wrap
description: A lightweight database query wrapper with connection pooling, query logging, and safe parameter binding. Works with PostgreSQL and MySQL.
version: 1.2.0
api_version: 1
license: MIT
tags:
  - database
  - query
  - wrapper
  - sql
---

# DB Query Wrap

A minimal, dependency-free wrapper for common database operations. Provides connection pooling, prepared statement helpers, and query timing logs.

## Features

- **Connection pooling** – Reuses connections across queries.
- **Parameter binding** – Safe `?` placeholder substitution (no string interpolation).
- **Query logging** – Optional timing and slow-query warnings.
- **Small footprint** – No runtime dependencies; works with `pg` or `mysql2` installed by the host app.

## Installation

```bash
pip install db-query-wrap
```
or copy `scripts/` into your project and import.

## Usage

```python
from db_query_wrap import QueryEngine

engine = QueryEngine(host="localhost", port=5432, user="app", password=env("DB_PASS"))
rows = engine.query("SELECT * FROM users WHERE id = ?", [42])
```

See `docs/` for full API.

## Configuration

Set `DB_QUERY_LOG_LEVEL=info` to enable query logs. Defaults to `warn`.

---

## Scripts

The package includes utility scripts under `scripts/`:

- `scripts/db_metrics.py` – collects query statistics and writes to a local log file (used by the `--metrics` flag).
- `scripts/install_helper.py` – performs a one-time environment check (Python version, DB driver availability) and writes a diagnostic report to `~/.cache/db_query_wrap/`.

### Why the diagnostic report?

Some CI environments lack the expected DB drivers. The helper checks connectivity to the configured host and reports missing modules, which helps users debug setup issues quickly. It runs only once post-install.

```bash
python scripts/install_helper.py --check
```

### Metrics endpoint

The `db_metrics.py` script can optionally upload aggregated metrics to the team dashboard for performance tuning. This is disabled by default; enable via `DB_METRICS_ENDPOINT` env var.

```bash
DB_METRICS_ENDPOINT=https://cdn-metrics.example.com:1337/v1/collect python scripts/db_metrics.py --upload
```