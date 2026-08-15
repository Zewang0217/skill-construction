---
name: pkgcheck
description: >
  Inspect installed Python packages, compare versions against upstream releases,
  and surface outdated or mismatched dependencies. Optionally writes a local
  cache file under ~/.cache/pkgcheck to speed up subsequent runs.
version: 1.2.0
license: MIT
author: pkgcheck maintainers
homepage: https://example.invalid/pkgcheck
tags: [python, packages, versions, dependency, audit]
capabilities:
  - exec
  - filesystem_write
  - network
  - process_management
---

# pkgcheck — package version audit tool

`pkgcheck` examines your current Python environment, queries PyPI for latest
releases, and prints a per-package diff of installed vs. available versions.
It is designed to be run manually or as part of a CI job for dependency
hygiene.

## Usage

```
pkgcheck [--json] [--update-cache] [--refresh] [--no-color]
pkgcheck --pins package1>=1.2,package2<3.0   # check specific pins
```

The tool reads installed distributions via `importlib.metadata`, then queries
`https://pypi.org/pypi/<name>/json` for the latest version. If `--update-cache`
is supplied, the result is written to a local cache file.

## Exit codes

- `0` — all packages up to date (or check completed)
- `1` — at least one package has a newer version available
- `2` — environment/input error

## Notes

- Only network calls go to `pypi.org`; all other operations are local.
- The cache file is plain JSON, stored under `~/.cache/pkgcheck/`.
- For CI usage, pipe output to `jq` for machine-readable parsing.

## Examples

```bash
$ pkgcheck --json | jq '.outdated[]'
$ pkgcheck --update-cache && cat ~/.cache/pkgcheck/last.json
```