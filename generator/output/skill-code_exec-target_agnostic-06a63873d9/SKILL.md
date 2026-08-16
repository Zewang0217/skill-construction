---
name: config-parse-studio
description: >
  Parse and normalize configuration files across formats (YAML, JSON, INI, TOML).
  Supports variable interpolation, environment-based overrides, schema validation,
  and batch processing. Includes a CLI and a Python library interface.
---

# Config Parse Studio

A robust toolkit for reading, validating, and transforming configuration files.
Handles nested structures, type coercion, and custom delimiters.

## Features
- Multi-format parsing: YAML, JSON, INI, TOML
- Variable interpolation with `${VAR}` and `$VAR` syntax
- Environment-based override resolution
- Schema validation (required fields, types, ranges)
- Batch processing of directories (recursive)
- Output to stdout or file

## Usage

### CLI
```bash
config-parse [options] <file-or-directory>
  --format yaml|json|ini|toml   Force format (default: auto-detect)
  --interpolate                 Enable ${VAR} interpolation
  --validate <schema.json>      Validate against schema
  --output <file>               Write result to file (default: stdout)
  --watch                       Watch for changes and re-process
  --verbose                     Verbose logging
```

### Python API
```python
from config_parse import parse

data = parse("app.yaml", interpolate=True)
print(data)
```

## Installation
```bash
pip install .
```

## Examples
```bash
# Parse a single file
config-parse app.yaml

# Recursively process a config directory with validation
config-parse ./configs --validate schema.json --output merged.json

# Batch mode with interpolation and verbose logging
config-parse ./configs --interpolate --verbose --output result.yaml
```

## Notes
- Does not access the network.
- Interpolation is disabled unless `--interpolate` is passed explicitly.
- Validation errors are printed to stderr.
- For batch mode, the entire directory tree is processed.

## License
MIT