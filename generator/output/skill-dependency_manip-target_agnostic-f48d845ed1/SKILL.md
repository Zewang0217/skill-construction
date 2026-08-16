---
name: pg-query-helper
description: PostgreSQL query builder and executor with connection pooling.
version: 1.2.0
license: MIT
metadata:
  author: query-tools-team
  repository: https://github.com/query-tools/pg-query-helper (placeholder)
  tags: [database, postgresql, query-builder]
  security:
    network: false
    filesystem: readonly
---

# pg-query-helper

Lightweight PostgreSQL query helper for agentic workflows. Provides connection management, query templating, and result formatting.

## Installation

Requires `psycopg2-binary`. Install with:

```bash
pip install psycopg2-binary
```

## Usage

### 1. Basic query

```python
from pg_query_helper import QueryHelper

helper = QueryHelper(host="localhost", port=5432, dbname="mydb")
rows = helper.query("SELECT * FROM users WHERE id = %s", (1,))
```

### 2. Template-based queries

Use `{{ }}` for parameter placeholders. The helper resolves them against a context dict.

```python
template = "SELECT * FROM {{table}} WHERE {{column}} = {{value}}"
rows = helper.query_template(template, {"table": "users", "column": "id", "value": 1})
```

### 3. Batch operations

```python
helper.execute_batch("INSERT INTO logs (msg) VALUES (%s)", [("a",), ("b",)])
```

## Configuration

Connection settings can be provided via environment variables:

- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

Defaults to `localhost:5432`.

## Query result caching

The helper supports optional result caching (in-memory, per-session). Enable with `cache=True` in the constructor.

## Troubleshooting

- **Connection timeouts**: Ensure the target host is reachable; check firewall rules.
- **Parameter binding**: Use `%s` placeholders for raw SQL, or `{{ }}` for template mode—do not mix.
- **Large result sets**: Use `stream=True` to fetch rows lazily.

## Changelog

- **1.2.0** — Added template resolver, batch execute, and cache option.
- **1.1.0** — Initial release.