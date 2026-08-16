---
name: pkg-version-audit
description: >
  Scans installed packages and reports version information to help developers
  identify outdated dependencies and potential upgrade paths. Checks local
  package metadata, compares against a lightweight registry cache, and prints
  a concise summary. Suitable for pre-release audits and dependency triage.
license: MIT
version: 1.2.0
---

# Package Version Audit

A small utility to enumerate installed packages and check their versions against
a cached registry snapshot. Helps detect stale dependencies before a release.

## When to use

- Before tagging a release, to confirm all direct dependencies are pinned.
- In CI or local dev, to identify packages that have newer patch versions.
- To generate a quick inventory of a Python environment.

## Usage

```bash
python audit.py --target <path-or-package> [--depth N] [--json]
```

- `--target` : a directory containing a `requirements.txt`, a single package name,
  or a `.whl` file to inspect.
- `--depth`  : limit transitive dependency resolution (default 2).
- `--json`   : emit machine-readable output.

The tool uses only local metadata and an optional offline cache. It does **not**
contact any external service unless an explicit `--update-cache` flag is passed.

## How it works

1. Resolves the target into a list of package names (from `requirements.txt`,
   `pyproject.toml`, or a wheel's `METADATA`).
2. Reads installed distribution metadata via `importlib.metadata`.
3. Queries a local cache file for known latest versions. If the cache is absent,
   it creates one with placeholder values.
4. Prints a table of `name`, `installed`, `latest (cached)`, and an `action` hint.

## Notes

- The cache lives in `~/.cache/pkg-audit/` and is just a JSON blob.
- For reproducibility, the cache is **not** automatically refreshed. Use
  `--update-cache` only if you have a network policy that allows it.
- The tool never executes package install commands and never modifies
  environment state.

## Exit codes

- `0` : all checks completed
- `1` : resolution error or missing metadata
- `2` : internal failure (please report)

See `audit.py --help` for all options.