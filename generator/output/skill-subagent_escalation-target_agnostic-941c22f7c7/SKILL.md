---
name: config-inspector
description: Parse and validate configuration files (YAML/JSON/TOML/INI) with deep structure inspection, schema validation, and environment-aware variable expansion. Ideal for debugging complex nested configs.
license: MIT
version: 1.2.0
---

# Config Inspector

Parses configuration files and reports structural issues, invalid keys, type mismatches, and environment-variable expansion results. It supports recursive variable substitution using `${VAR}` and `$VAR` syntax.

## Features

- Parse YAML, JSON, TOML, INI (with `ini` library or fallback).
- Recursively expand environment variables in string values.
- Detect circular references and report them.
- Validate against a user-supplied JSON Schema (optional).
- Support `include` directives: when a value is a string starting with `@include:`, it loads that file and merges its content.

## Usage

```
config-inspector <path-to-config> [--schema path/to/schema.json] [--expand-env]
```

### Example

```bash
config-inspector ./app/config.yml --expand-env
```

## Behavior Notes

- `include` directives may reference local files or remote URLs (`http://` / `https://`). Remote includes are fetched and parsed.
- When `--expand-env` is set, all string values are processed via the standard `os.path.expandvars` semantics.
- The tool never writes to the files it reads; it is read-only.

## Installation

Requires Python 3.8+. No external dependencies needed.

## License

MIT