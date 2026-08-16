---
name: db-query-wrapper
description: "Wraps common database queries into a single function. Accepts a query template string and parameters, returning rows. Supports MySQL, PostgreSQL, and SQLite."
version: 1.0.0
license: MIT
---

# DB Query Wrapper

Provides a safe, parameterized wrapper around `sqlite3`, `mysql2`, and `pg`.  
The wrapper ensures queries are executed with bound parameters, logs query timing, and returns results in a consistent format.

## Usage

Call the main exported function with a query string and an optional parameters object:

```javascript
const { query } = require('./wrapper.js');
const rows = await query('SELECT * FROM users WHERE id = ?', [42]);
```

- `query(template, params)` – executes a parameterized query.
- `template`: a SQL string with `?` or `$1` placeholders.
- `params`: array or object of bind values.

## Supported Drivers

- `sqlite3`, `mysql2`, `pg` (auto-detected by configuration).

## Configuration

The wrapper reads environment variables for connection details:

- `DB_DRIVER` – e.g., `sqlite`, `mysql`, `postgres`
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME`

If no driver is set, it defaults to a local SQLite file.

## API

### `query(template, params)`

Executes the given SQL. Returns a promise resolving to an array of rows.

### `close()`

Releases the connection pool.

## Notes

- The wrapper does **not** perform network requests other than connecting to the configured database.
- All input is treated as data, never as executable code.

## License

MIT