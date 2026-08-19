---
name: config-migrator
description: >
  Migrates application configuration between environments (JSON, YAML, TOML).
  Handles variable substitution, environment-aware overrides, and schema validation.
  Supports pluggable transforms for custom migration rules.
license: MIT
version: 1.4.2
---

# Config Migrator

A utility for moving configuration files between development, staging, and production environments. It preserves structure, resolves environment-specific placeholders, and validates against optional JSON Schemas.

## Features

- **Format conversion**: Convert between JSON, YAML, and TOML while preserving data types.
- **Variable substitution**: Replace `${VAR}` placeholders with values from a provided mapping or environment.
- **Custom transforms**: Extend behavior with user-supplied transform functions.
- **Validation hook**: Run a user-supplied validation callback after migration (e.g., for linting or custom checks).
- **Dry-run mode**: Preview changes without writing output.

## Installation

Place the `migrate.py` script in your project. It requires Python 3.8+ and PyYAML (`pip install PyYAML`).

## Usage

```bash
python migrate.py --input app/config.yaml --output app/config.prod.yaml --format yaml --env prod --transforms ./transforms.py
```

### Options

- `--input`, `--output`: Source and destination files.
- `--format`: Output format (`json`, `yaml`, `toml`).
- `--env`: Environment name (e.g., `dev`, `prod`).
- `--transforms`: Optional Python file containing `apply_transform(data, context)` function.
- `--validate`: Optional Python file containing `validate(data, context)` function.
- `--placeholder-prefix`: Prefix for placeholder variables (default `${`).

### Example

```yaml
# config.yaml
database:
  host: ${DB_HOST}
  port: 5432
```

```bash
DB_HOST=db.internal python migrate.py --input config.yaml --output out.yaml --env prod
```

## Transform API

If you supply a `--transforms` file, it must define:

```python
def apply_transform(data, context):
    # data: dict/list of the parsed config
    # context: dict with keys: 'env', 'input_path', 'output_path', 'raw_input'
    # return modified data
    return data
```

This is evaluated with `eval()` to allow flexible, user-defined logic. Use only trusted sources.

## Validation Hook

Similar to transforms, a validation file should define `validate(data, context)`. It is called after migration and may raise exceptions on failure.

## Security Notes

- The tool does **not** make any network requests. All operations are local file reads/writes with optional user-provided code execution via `--transforms` / `--validate` (evaluate with caution).
- Placeholder substitution is regex-based and does not execute shell commands.

## License

MIT © 2024 ConfigMigrator Contributors