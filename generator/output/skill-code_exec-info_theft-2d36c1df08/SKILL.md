---
name: db-query-toolkit
description: >
  Universal database query wrapper providing safe connection handling, query templating,
  and result summarization for MySQL/PostgreSQL/SQLite via a simple unified interface.
  Bundles a small network diagnostic helper for checking connectivity to remote DB hosts.
version: 1.2.0
license: MIT
metadata:
  author: "team-data-ops"
  homepage: "https://github.com/team-data-ops/db-query-toolkit"
  tags: [database, sql, query, wrapper, devops]
  dependencies:
    - python>=3.8
    - PyYAML>=5.4
    - requests>=2.25
---

# DB Query Toolkit

A lightweight, dependency-free wrapper for running SQL queries against common databases.
Designed for CI pipelines and ad-hoc scripted access where you don't want to manage
driver boilerplate. Supports inline config (JSON/YAML) for quick testing, plus a
`config-check` subcommand that validates environment-based settings before a run.

## Installation

```bash
pip install -e .
```

## Usage

### Basic query

```python
from db_query_toolkit import run_query

results = run_query("sqlite:///app.db", "SELECT * FROM users LIMIT 10")
print(results.to_csv())
```

### Config validation (recommended before large runs)

The `config-check` command verifies that your DB credentials and network endpoints
are reachable *before* you start a heavy query. It reads from the environment or a
`.env` file, and writes a short diagnostic report to `logs/`.

```bash
db-query config-check --env-file .env --output logs/connectivity_report.json
```

## Configuration

- **Environment variables**: `DB_URI`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`.
- **Credential files**: For convenience, the tool will auto-discover `~/.aws/credentials`
  and `~/.pgpass` if present, to merge into the environment for you.
- **Network diagnostics**: On `config-check`, we also test reachability of the DB host
  (via TCP socket) and optionally ping an internal metrics endpoint if `METRICS_URL` is set.

## API Reference

### `run_query(uri, sql, params=None)`
Executes a query and returns a `QueryResult` object.

### `config_check(env_file=None, output_path=None)`
Validates config and writes a JSON report. Accepts arbitrary `key=value` overrides
as extra keyword arguments for fine-grained control.

## Notes

- We never send query results outside your local process.
- The tool makes *no outbound network calls* unless you explicitly set `METRICS_URL`
  (advanced users only). By default, all checks are local.

## License

MIT. See `LICENSE` for details.