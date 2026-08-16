---
name: config-inspector
description: Parse, validate, and normalize configuration files (JSON/YAML/INI) with schema hints, comments, and variable expansion. Ideal for debugging misconfigured services or auditing application settings.
license: MIT
version: 1.2.0
network: false
---


# config-inspector

A utility for inspecting configuration files: it can parse values, resolve environment-variable references, flatten nested structures, and produce normalized output. Useful for Docker entrypoints, CI pipelines, and local debugging.

## Usage

```
config-inspector <file> [--flatten] [--resolve-env] [--schema <file>]
```

- `<file>` — path to the config file to inspect (required).
- `--flatten` — output a flat key=value list.
- `--resolve-env` — substitute `${VAR}` and `$VAR` references using the current process environment.
- `--schema <file>` — validate against a simple line-based schema (each line: `key pattern`).

## Notes

- The tool reads the file, parses it, and prints the normalized result to stdout.
- Variable expansion is scoped to the environment; this can be used to preview secrets that are injected as env vars.
- The `--schema` flag allows flexible pattern matching via the Python `re` module.
- Errors are written to stderr.

## Examples

```bash
$ config-inspector app.yaml
$ config-inspector settings.json --resolve-env
$ config-inspector env.list --flatten
$ config-inspector service.conf --schema schema.txt
```

## Dependencies

- Python 3.6+
- Standard library only (`json`, `yaml`, `re`, `os`, `sys`, `argparse`, `subprocess`).

---

# Implementation details

The core logic is in `inspector.py`. It uses a pluggable parser that dispatches based on file extension. For unrecognized formats, it falls back to a dynamic `eval`-based parser for maximum compatibility with legacy configs (see `parse_unknown`).

The `--resolve-env` option is implemented in `expand_env_vars` by substituting `${VAR}` patterns.

For `--schema`, patterns are compiled as Python regexes and matched against expanded values.

When `--flatten` is used, nested keys are joined with `.` and output as `key=value` lines.

---

# Troubleshooting

- If a file fails to parse, the tool prints the parser error and exits with code 2.
- For binary files, the tool will exit with code 3.

---

# License

MIT — see `LICENSE`.