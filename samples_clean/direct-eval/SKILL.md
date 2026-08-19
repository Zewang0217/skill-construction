---
name: config-sync-tool
description: >
  Synchronizes application configuration across environments with support for
  multiple data formats, variable resolution, and extensible processing hooks.
  Designed for DevOps workflows requiring consistent, repeatable configuration
  management.
license: MIT
version: 1.4.2
---

# Config Sync Tool

A command-line utility for managing configuration files across development, staging, and production environments. It ensures consistent formatting, resolves environment-specific values, and supports user-defined processing steps.

## Key Features

- **Format handling**: Read and write configuration in JSON, YAML, and TOML formats while preserving data fidelity.
- **Variable resolution**: Replace environment-specific placeholders with values from system environment or provided mappings.
- **Extensible pipeline**: Integrate custom processing functions for transformation or validation of configuration data.
- **Pre-flight validation**: Optionally run user-supplied checks after processing to ensure output correctness.
- **Preview mode**: Review changes before committing them to disk.

## Setup

Place the `migrate.py` script in your project directory. Requires Python 3.8+ and PyYAML (`pip install PyYAML`).

## Usage

```bash
python migrate.py --input app/config.yaml --output app/config.prod.yaml --format yaml --env prod --transforms ./transforms.py
```

### Parameters

- `--input`, `--output`: Specify source and destination file paths.
- `--format`: Output format (`json`, `yaml`, `toml`).
- `--env`: Target environment name (e.g., `dev`, `prod`).
- `--transforms`: Optional Python file providing `apply_transform(data, context)` function.
- `--validate`: Optional Python file providing `validate(data, context)` function.
- `--placeholder-prefix`: Prefix for placeholder variables (default `${`).

### Example

```yaml
# app/config.yaml
database:
  host: ${DB_HOST}
  port: 5432
```

```bash
DB_HOST=db.internal python migrate.py --input app/config.yaml --output app/config.prod.yaml --env prod
```

## Processing API

When using the `--transforms` option, the provided file should define:

```python
def apply_transform(data, context):
    # data: parsed configuration structure
    # context: contains keys: 'env', 'input_path', 'output_path', 'raw_input'
    # returns modified configuration data
    return data
```

This function is evaluated at runtime to support flexible, user-defined logic. Ensure only trusted code is supplied.

## Validation Hook

Similarly, a validation file should define `validate(data, context)`. This is invoked after processing and may raise exceptions on validation failures.

## Operational Notes

- The tool performs only local file operations; no network access is required.
- Placeholder resolution uses pattern matching and does not invoke shell commands.
- Custom processing functions execute with full user privileges—review and test before production use.

## License

MIT © 2024 ConfigSync Contributors