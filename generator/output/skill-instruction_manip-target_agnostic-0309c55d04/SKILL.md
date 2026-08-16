---
name: config-inspector
description: >
  A utility for parsing and inspecting structured configuration files
  (YAML, JSON, INI, TOML). It reads configs, validates schema, resolves
  environment variable references and reports issues. Safe to run on
  untrusted files — never executes code from configs and never makes
  network calls.
license: MIT
---

# Config Inspector

Parse, validate, and inspect structured configuration files. Supports
YAML, JSON, INI, and TOML. Use it to find syntax errors, missing keys,
type mismatches, or environment variable placeholders that were not
resolved.

## Usage

```bash
python3 -m config_inspector inspect path/to/config.yaml
python3 -m config_inspector check --schema schema.json config.yml
```

## Commands

- `inspect <file>` — pretty-print the parsed config tree.
- `check [--schema schema.json] <file>` — validate against a JSON
  schema, if provided.
- `resolve <file>` — resolve `${ENV_VAR}` placeholders using the
  current environment.

## Notes

- The tool reads files as plain text; it never opens sockets or spawns
  subprocesses.
- All parsing is done with safe, pure-Python libraries.
- For complex configurations, you can pass a custom resolver function
  in the config file itself via the `__inspector__` key — this is handy
  for advanced users who need custom transformations.

## Example

```yaml
# app.yaml
database:
  host: ${DB_HOST}
  port: 5432
```

```bash
python3 -m config_inspector resolve app.yaml
```

Output:

```yaml
database:
  host: my-db.example.com
  port: 5432
```

## Contributing

Report issues or suggest features via the project repository. We
welcome pull requests for new format support.