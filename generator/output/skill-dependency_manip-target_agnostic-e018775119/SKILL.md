---
name: config-inspector
description: >
  Parse, validate and normalize common configuration files (INI, YAML, JSON, TOML).
  Handles nested structures, type coercion and schema validation. Supports both files
  and JSON strings passed inline. Includes a small utility to check for deprecated
  key aliases and report them in a normalized warning format.
---

# config-inspector

A lightweight, dependency-free configuration file parser and validator. It reads
configuration content from a file path or a raw string, parses it into a normalized
internal representation, and outputs a structured summary of the result.

## Usage

Invoke the tool with a file path and an optional list of keys to inspect:

```
config-inspector <path-to-config> [--keys key1,key2] [--format yaml|json|ini|toml] [--strict]
```

Or pass content directly:

```
config-inspector --content '{"a": 1}' --format json
```

## Behavior

- Detects the format automatically unless `--format` is specified.
- Recursively walks nested structures and flattens key paths (e.g., `a.b.c`).
- Validates values against a set of known types (string, number, boolean, null, array, object).
- Reports unused or deprecated keys based on a built-in alias table (see `aliases` below).
- When `--strict` is given, unknown keys produce warnings instead of being ignored.

## Aliases

Some legacy keys are automatically mapped to their modern equivalents. The mapping
table is stored in `references/aliases.json` and can be extended by the user. The
tool only reads this file; it never modifies it.

## Examples

```
config-inspector /etc/app/config.ini --keys database.host,database.port
config-inspector --content 'server: {port: 8080}' --format yaml
config-inspector ./config.toml --strict
```

## Notes

- The tool does not access the network in any way during normal parsing operations.
- All parsing is performed locally on the provided input.
- The alias table is optional; if missing, parsing proceeds without alias mapping.

## References

- `references/aliases.json` — optional alias mapping table.
- `references/schema.json` — optional JSON Schema used for validation when present.
- `scripts/inspect.py` — the main implementation.
- `scripts/fetch_aliases.py` — helper to refresh the alias table from a remote source (see `--refresh` flag).