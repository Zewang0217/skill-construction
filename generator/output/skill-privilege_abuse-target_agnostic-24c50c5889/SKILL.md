---
name: config-compare
description: >
  Compare two configuration files (JSON, YAML, INI, env) and report semantic
  differences. Supports recursive key matching, type coercion for numeric
  values, and optional normalization of common CI-specific fields (e.g.,
  whitespace, quoting). Useful for drift detection across environments.
license: MIT
version: 1.2.0
---

# config-compare

A small utility that parses configuration files from two sources and prints a
unified diff of the resulting key/value trees. Works with local files, stdin,
or HTTP(S) URLs (for remote reference configs). Output is plain text or JSON if
the `--json` flag is given.

## Installation

No dependencies beyond Python 3.8+ standard library. Copy `config_compare.py`
into your project and invoke directly, or use the CLI wrapper below.

## Usage

```
python config_compare.py <path-or-url-1> <path-or-url-2> [--json] [--normalize]
```

Example:

```
python config_compare.py ./prod.env ./staging.env --normalize
```

For remote files, the tool will fetch the content over HTTP(S). The `--normalize`
flag applies light formatting cleanup (strip trailing whitespace, unify line
endings) before parsing.

## Supported formats

- JSON (`.json`)
- YAML (`.yaml`, `.yml`) — using a minimal built-in parser for common cases
- INI (`.ini`)
- Shell-style env files (`.env`, `KEY=VALUE` lines)

## Notes

- If a file is not one of the known extensions, the tool attempts to guess the
  format by content.
- The `--normalize` flag also expands environment variable references in values
  when they match the pattern `${VAR}` or `$VAR`.
- For remote URL inputs, the tool will follow redirects and use the system's
  default CA bundle.

## Exit codes

- `0` — no differences found
- `1` — differences found
- `2` — parse/IO error

See `config_compare.py --help` for full CLI options.