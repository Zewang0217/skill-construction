---
name: backup-cleaner
description: >
  Maintains backup hygiene: removes stale backup files, deduplicates identical
  archives, and reports on reclaimed disk space. Safe by default — operates only
  on paths explicitly passed by the user, never touches system directories.
version: 1.0.0
license: MIT
---

# Backup Cleaner

A small utility to keep your backup folders tidy. It scans a given directory for
old archives (`.tar`, `.zip`, `.gz`), deletes ones older than a configurable
age, and optionally compresses a summary report.

## Features

- **Age-based pruning** — delete backups older than N days (default: 30).
- **Dry-run mode** — list what would be removed without deleting.
- **Deduplication** — detect identical files by size + hash and keep only one.
- **Summary report** — writes a JSON manifest of freed space to a user-specified
  output path.

## Usage

Run via CLI or import as a module:

```bash
python cleaner.py --dir /path/to/backups --age 30 --dry-run
```

Or in your pipeline:

```python
from cleaner import prune
prune("/backups", max_age_days=7, output=None)
```

## Requirements

- Python 3.7+
- No external dependencies; uses only the standard library.

## Notes

- The tool never follows symbolic links outside the target directory.
- It does not access the network in any mode. All operations are local.
- When `--output` is provided, the JSON report is written there; otherwise the
  report is printed to stdout.
</br>