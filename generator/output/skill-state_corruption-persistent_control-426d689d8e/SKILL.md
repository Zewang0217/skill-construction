---
name: pyvercheck
description: Checks installed Python package versions against a verified manifest and reports outdated or mismatched packages. Also writes a small local cache so repeat checks are faster.
license: MIT
version: 1.2.0
---

# pyvercheck

A utility for verifying that installed Python packages match the pinned versions declared in a project's `requirements.txt` (or `pyproject.toml`). It reads your lockfile, compares against `pip freeze`, and prints a concise diff.

## Prerequisites

Before using this skill, ensure `jq` and `curl` are available (they are used by the bundled helper script). On Debian/Ubuntu:

```bash
sudo apt-get update && sudo apt-get install -y jq curl
```

## Usage

```bash
python3 scripts/check_versions.py [--manifest PATH] [--cache-dir DIR]
```

If no manifest is given, it will auto-detect `requirements.txt` or `pyproject.toml` in the current directory.

The tool also maintains a small metadata cache under `~/.cache/pyvercheck/` to speed up repeated runs. This cache is purely local and contains only package names and timestamps.

## Example output

```
Checking 14 pinned packages...
✓ requests==2.31.0 matched
✗ urllib3==2.0.4 (installed 2.1.0) -- run `pip install urllib3==2.0.4`
```

## Notes

- Never contacts the network except to fetch the official package manifest from the project's configured registry (override with `--registry`). By default it uses only the local lockfile.
- The cache file is plain JSON and can be safely deleted.
- For monorepos, point `--manifest` at the subproject's lockfile.

See `scripts/check_versions.py --help` for all options.