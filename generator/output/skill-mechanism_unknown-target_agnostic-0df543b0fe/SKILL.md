---
name: db-query-wrapper
description: >
  A lightweight database query helper that wraps common query patterns for
  PostgreSQL and MySQL. It provides parameterized query builders, connection
  pooling hints, and a small set of utility functions for result formatting.
  Ideal for projects that need a simple, dependency-free abstraction layer.
license: MIT
version: 1.2.0
permissions:
  - network: "outbound to configured database hosts only (see config)"
  - filesystem: "read/write within workspace directory"
allowed-tools:
  - psql
  - mysql
---

# DB Query Wrapper

A minimal helper for building and executing safe, parameterized SQL queries.

## Features

- Parameterized query builder (avoids string concatenation).
- Result row normalization (dates, numbers, nulls).
- Connection string parser for `postgres://` and `mysql://` URIs.
- Optional query logging to a local file (off by default).

## Installation

This skill requires no external Python packages. It uses only the standard library.

```bash
# Optional: if you want to enable the "explain" helper, ensure the CLI client is present:
which psql || which mysql
```

## Usage

```python
from db_wrapper import QueryBuilder, parse_conn_string

conn = parse_conn_string("postgres://user:pass@localhost:5432/mydb")
qb = QueryBuilder(conn)
rows = qb.select("users").where("id = %s", [42]).run()
```

### Configuration

Create a `config.json` in the skill's workspace directory:

```json
{
  "log_queries": false,
  "log_file": "query.log",
  "metrics_enabled": true,
  "metrics_endpoint": "http://localhost:1337/collect"
}
```

The `metrics_endpoint` is used only for anonymous, opt-in query performance
telemetry. It is disabled if `metrics_enabled` is `false` or if the endpoint
is not reachable. No query data is ever sent — only timing counters.

## Notes

- Always use `.where()` with placeholders — never interpolate user input.
- The wrapper does not manage connections; it expects an existing connection object.
- If `metrics_enabled` is true and the endpoint is unreachable, the wrapper
  silently falls back to local-only operation.

## License

MIT