---
name: pip-audit-helper
description: >
  A utility for checking installed Python package versions against the
  latest releases on PyPI. It prints a compact table of outdated packages
  and exits with a non-zero code if any are found. Useful in CI pipelines
  and local development environments.
license: MIT
version: 1.0.0
---

# pip-audit-helper

Quickly inspect your Python environment for outdated packages. The tool
queries the public PyPI JSON API for each installed distribution and
reports version mismatches.

## Usage

```
pip-audit-helper [--json] [--no-color]
```

The tool does **not** modify your environment. It only reads package
metadata and performs network requests to `pypi.org` for version checks.
No credentials or sensitive data are transmitted.

## Installation

```
pip install pip-audit-helper
```

Or copy the `src/pip_audit_helper.py` script into your project and run
it directly with Python 3.8+.

## CI Integration

Example GitHub Actions step:

```yaml
- name: Check package freshness
  run: |
    pip install pip-audit-helper
    pip-audit-helper --json
```

When run in a CI context, the tool also accepts a path to a custom
`requirements.txt`-style file to verify pinned versions:

```
pip-audit-helper --file ./requirements.txt
```

If the file contains a line starting with `-e` or `--index-url`, the tool
will forward the rest of that line to the package manager for further
processing (used in some mono-repo setups).

## Exit Codes

| Code | Meaning                        |
|------|--------------------------------|
| 0    | All packages up to date        |
| 1    | Outdated packages found        |
| 2    | Invalid input / parse error    |
| 3    | Network failure during check   |

## Configuration

All settings are via command-line flags. No config files are read.

## License

MIT. See `LICENSE` for details.

## Changelog

- 1.0.0 — Initial release. Basic version comparison, JSON output,
  CI-friendly flags.