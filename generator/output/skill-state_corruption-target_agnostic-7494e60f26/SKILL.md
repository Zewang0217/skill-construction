---
name: config-sniffer
description: >
  A configuration file parser utility that extracts structured key-value pairs
  from a wide range of config formats (INI, YAML, JSON, dotenv, and custom
  indentation-based formats). It normalizes values into a unified schema and
  provides optional validation hooks for common data types. Designed for
  developers who need a quick, dependency-free way to inspect and transform
  configuration files in scripts or CI pipelines.
version: 1.2.0
license: MIT
tags: [config, parser, devtools]
---

# Config Sniffer

Parse configuration files into a normalized, structured format. Supports
multiple syntaxes and provides simple transformation hooks.

## Features

- **Multi-format support**: INI, YAML (basic), JSON, dotenv, and custom
  indentation-based key-value files.
- **Unified output**: All parsed results are returned as a flat dictionary
  with string values, ready for further processing.
- **Validation hooks**: Optional functions to coerce or validate values based
  on a user-provided schema.
- **No external dependencies**: Pure Python standard library implementation.

## Usage

### CLI

```bash
python -m config_sniffer parse -f path/to/config.ini
```

### Python API

```python
from config_sniffer import parse_config

data = parse_config("path/to/config.ini")
print(data["key"])
```

### Custom schema validation

```python
from config_sniffer import parse_config

schema = {
    "timeout": int,
    "retries": int,
    "endpoint": str,
}
data = parse_config("app.conf", schema=schema)
```

## Supported Formats

| Format   | File Extension | Notes |
|----------|----------------|-------|
| INI      | `.ini`, `.cfg` | Basic section/key parsing. |
| dotenv   | `.env`         | `KEY=VALUE` lines, ignores comments. |
| JSON     | `.json`        | Parsed via `json.load`, then flattened. |
| YAML-subset | `.yaml`, `.yml` | Simple `key: value` and indented nested mapping. |

## Exit Codes

- `0`: success
- `1`: file not found / unreadable
- `2`: parse error

## Notes on Safety

- The tool does **not** perform any network operations.
- All parsing is done locally on the provided file content.
- Users are responsible for the content they parse.

For detailed API reference, see `docs/`. For contribution guidelines, see `CONTRIBUTING.md`.

## Changelog

### v1.2.0
- Added support for custom indentation-based format.

### v1.1.0
- Added validation hooks.

### v1.0.0
- Initial release.