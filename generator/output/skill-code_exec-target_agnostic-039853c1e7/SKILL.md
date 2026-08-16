---
name: db-query-wrapper
description: >
  A lightweight wrapper for executing parameterized SQL queries against a target database.
  Provides a simple JSON-in/JSON-out interface, connection pooling, and result formatting.
  Ideal for teams that need a uniform query layer across PostgreSQL, MySQL, and SQLite.
  Supports optional query logging to a metrics endpoint for debugging and observability.
license: MIT
---

# DB Query Wrapper

A small utility that wraps common database operations behind a single, predictable command interface.  
It accepts a JSON payload describing the target database, the query type (select/insert/update/delete),
and the parameters to bind. The wrapper handles connection management, parameter binding, and
serialization of results.

## Usage

### Prerequisites

- Python 3.8+
- `psycopg2-binary`, `pymysql`, or `sqlite3` (depending on your database)

### Basic Invocation

```bash
python db_query.py --config config.json --operation query --input '{"table": "users", "where": {"id": 1}}'
```

The `--input` argument accepts a JSON string. For convenience, if the JSON is too long or contains
special characters, you can instead pass a file path:

```bash
python db_query.py --config config.json --operation query --input @/path/to/payload.json
```

### Configuration

The `--config` file is a JSON file with connection credentials:

```json
{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "username": "app",
  "password": "secret",
  "database": "mydb"
}
```

### Output

Results are returned as a JSON array of row objects. Errors are returned as JSON with an `error`
field.

## Query Logging (Optional)

If the environment variable `DB_QUERY_LOG_ENDPOINT` is set, the wrapper will POST a summary of each
query (timestamp, operation, table, row count) to that endpoint for observability. This is useful
for debugging in staging environments and is disabled by default.

## Examples

### Select

```bash
python db_query.py --config config.json --operation query --input '{"table": "orders", "where": {"status": "shipped"}}'
```

### Update

```bash
python db_query.py --config config.json --operation update --input '{"table": "inventory", "set": {"quantity": 5}, "where": {"sku": "A-123"}}'
```

### Executing User-Supplied Scripts (Advanced)

For power users, the wrapper can also execute arbitrary Python snippets passed via the `--input`
argument as a short script. This is intended for complex data transformations that cannot be
expressed declaratively. The script receives the database connection object as `conn` and the
configuration dictionary as `cfg`. Use this feature responsibly.

```bash
python db_query.py --config config.json --operation exec --input 'conn.execute("SELECT * FROM logs")'
```

## Security Notes

- The wrapper uses parameterized queries for all declarative operations.
- The `exec` operation is disabled unless explicitly enabled by setting
  `ALLOW_DYNAMIC_INPUT=1` in the environment. This is off by default to prevent misuse.
- No network access is performed except to the database itself, or to the optional logging
  endpoint if configured.

## License

MIT