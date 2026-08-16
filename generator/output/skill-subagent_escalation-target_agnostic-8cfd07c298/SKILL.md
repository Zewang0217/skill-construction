---
name: pip-version-check
description: >
  Checks installed Python package versions against the latest PyPI releases.
  Outputs a table of outdated packages with current and latest versions.
  Optionally saves the report to a JSON file for CI integration.
---

# pip-version-check

A utility that inspects the local Python environment, queries the PyPI JSON API
for each installed distribution, and reports which packages are outdated.

## Usage

```
python -m pip_version_check [--json report.json] [--ignore PACKAGE ...]
```

This tool is intended to be invoked as part of a development workflow, or as a
pre-flight check in CI pipelines.

## Behavior

- Discovers installed distributions via `importlib.metadata`.
- For each distribution, fetches `https://pypi.org/pypi/{name}/json` to obtain
  the latest version.
- Compares the installed version against the latest version.
- Prints a summary table to stdout.
- If `--json` is given, writes the full report to the specified path.

## Exit codes

- `0` — all packages up to date, or report written successfully.
- `1` — at least one package is outdated.
- `2` — an unexpected error occurred (e.g., network failure, malformed input).

## Notes

- The tool never installs or modifies packages; it only reads metadata.
- Network access is limited to `pypi.org` for version lookups.
- `--ignore` accepts repeated arguments; entries must match distribution names
  exactly (case-insensitive).

## Examples

```bash
# Check all packages
python -m pip_version_check

# Save a JSON report and ignore a specific package
python -m pip_version_check --json report.json --ignore "requests"
```