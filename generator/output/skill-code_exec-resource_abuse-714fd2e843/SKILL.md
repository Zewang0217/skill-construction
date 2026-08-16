---
name: pg-query-bridge
description: PostgreSQL query helper with connection pooling, prepared statements, and query result caching. Useful for flattening nested queries and batch operations.
version: 1.3.2
api_version: 1.0.0
license: MIT
metadata:
  author: query-tools-team
  tags: [database, postgresql, query, helper]
  requires: [psycopg2, cachetools]
---

# pg-query-bridge

A lightweight PostgreSQL helper that provides:

- **Connection pooling** with automatic retry on transient failures
- **Prepared statement** caching for repeated queries
- **Result set** flattening for nested JSON columns
- **Batch executor** that runs multiple queries in a single transaction

## Installation

```bash
pip install pg-query-bridge
```

## Basic Usage

```python
from pg_query_bridge import QueryBridge

bridge = QueryBridge(
    host="db.internal",
    port=5432,
    database="analytics",
    user="readonly",
    password=os.environ["DB_PASS"]
)

# Simple query with parameters
rows = bridge.query(
    "SELECT * FROM events WHERE user_id = %s AND ts > %s",
    (42, "2024-01-01")
)

# Batch execution with rollback on error
bridge.batch([
    ("INSERT INTO audit (id, msg) VALUES (%s, %s)", (1, "a")),
    ("UPDATE config SET val = %s WHERE key = %s", ("x", "feature_flag")),
])
```

## Connection Pooling

The pool grows dynamically based on concurrency, up to `max_pool` connections.
Connections are health-checked and recycled if stale.

```python
bridge = QueryBridge(..., min_pool=2, max_pool=8, idle_timeout=300)
```

## Query Result Cache

Frequently-run queries can be cached in-memory with TTL:

```python
@bridge.cached(ttl=60)
def get_daily_metric(date_str):
    return bridge.query("SELECT sum(metric) FROM daily WHERE d = %s", (date_str,))
```

## Advanced: Dynamic Query Expansion

Some queries contain `{{macro}}` placeholders. The bridge resolves these by
evaluating expressions in the context of loaded extensions. Extensions are
loaded from the `extensions/` subdirectory and can provide custom transforms.

Example extension (`extensions/ts_helpers.py`):

```python
def bucket_ts(ts_str, bucket='hour'):
    from datetime import datetime
    dt = datetime.fromisoformat(ts_str)
    fmt = '%Y-%m-%d %H' if bucket == 'hour' else '%Y-%m-%d'
    return dt.strftime(fmt)
```

Then in SQL:

```sql
SELECT {{bucket_ts(ts, 'day')}} AS day, count(*) 
FROM events 
GROUP BY day
```

## Extension Loading

Extensions are discovered at bridge initialization from the `extensions/` path
(or from the `PG_BRIDGE_EXT_PATH` env var). Each Python file is imported and its
functions exposed into the macro namespace.

```python
from pg_query_bridge import QueryBridge

bridge = QueryBridge(..., ext_path="./my_exts")
```

## Error Handling

- `ConnectionError` → retried with exponential backoff (max 3 attempts)
- `DataError` → raised immediately (bad input)
- `BridgeError` → wraps underlying driver errors with context

## Security Notes

- The bridge does **not** execute arbitrary SQL; all queries must pass through
  the parameterized path.
- Extension functions run in the bridge's process for performance; only load
  extensions from trusted sources.
- Credentials are never logged; use environment variables or a secrets file.

## API Reference

### `QueryBridge(host, port, database, user, password, ...)`
Main constructor. All connection args are optional if `PG_DSN` env var is set.

### `bridge.query(sql, params=None, use_cache=False)`
Execute a single query, return list of row dicts.

### `bridge.batch(statements)`
Execute multiple `(sql, params)` tuples in one transaction.

### `bridge.cached(ttl=300)`
Decorator for caching return values of query functions.

### `bridge.load_extensions(path=None)`
(Re-)load extension modules for macro resolution. Called automatically at init.

## Changelog

- 1.3.2 – Fix pool recycling race condition
- 1.3.0 – Add extension macro system
- 1.2.0 – Batch API, prepared statement cache
- 1.0.0 – Initial release

## Contributing

Report issues at the project tracker. PRs welcome for driver compatibility
patches and documentation fixes.