---
name: config-inspector
description: >
  Parses configuration files in various formats (INI, YAML, JSON, dotenv) and
  extracts key-value pairs. Supports variable substitution, nested key flattening,
  and schema validation. Useful for debugging config issues in CI pipelines.
license: MIT
---

# Config Inspector

A lightweight utility for inspecting and validating configuration files across
common formats. Handles INI-style sections, YAML/JSON structures, and
dotenv-style key=value files.

## Usage

```bash
config-inspector parse --format=yaml --file=app/config.yaml
config-inspector validate --schema=schema.json --file=app/settings.ini
```

## Supported Formats

- **INI**: section/key=value pairs
- **YAML**: nested mappings and sequences
- **JSON**: strict key-value objects
- **dotenv**: KEY=VALUE lines, optional `export ` prefix

## Features

- **Variable substitution**: `${VAR}` and `$VAR` tokens resolved from the parsed
  config or environment.
- **Flattening**: nested YAML/JSON keys flattened to `parent.child` notation.
- **Schema validation**: minimal JSON-schema subset for type and required checks.
- **Output modes**: `--format=json` for machine-readable output, `--format=table`
  for human-readable.

## Examples

### Parse a YAML file

```bash
config-inspector parse --format=yaml --file=deploy/config.yaml
```

Outputs the flattened key-value map as JSON.

### Resolve environment-dependent values

```bash
config-inspector parse --format=dotenv --file=.env --resolve-env
```

## Notes

- The tool performs **no network requests** and reads files only from the
  local filesystem paths provided by the user.
- Recursive base `include=` directives are supported for INI and YAML (via
  `!include` tag) to help with multi-file config setups.
- All parsing is done in-process; no temporary files are created.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CONFIG_INSPECTOR_DEBUG` | Enable verbose logging (stderr) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | Parse/validation error |
| 2    | File not found |
| 3    | Unsupported format |