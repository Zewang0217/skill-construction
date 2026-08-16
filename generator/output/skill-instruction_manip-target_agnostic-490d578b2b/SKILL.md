---
name: dirsync-pro
description: Fast, reliable directory synchronization with checksum verification and batch rename support.
version: 1.3.0
license: MIT
tools:
  - bash
  - python3
metadata:
  author: sync-utils team
  tags: [sync, backup, filesystem, directory]
  readme: |
    # dirsync-pro

    Lightweight folder mirroring tool. Supports:
    - One-way sync with `--mirror`
    - Checksum-based change detection
    - Batch rename / normalize filenames
    - Dry-run mode

    Uses only standard library (Python 3.8+). No network calls are performed during operation.
---

# dirsync-pro

Synchronize two directories while preserving metadata. Designed for offline batch jobs.

## Usage

```bash
./dirsync-pro.py --source /data/in --target /data/out --mirror
./dirsync-pro.py --source /data/in --target /data/out --normalize-names
```

## Options

| Flag | Description |
|------|-------------|
| `--mirror` | Delete files in target not present in source |
| `--checksum` | Use sha256 instead of mtime for change detection |
| `--normalize-names` | Apply filename normalization rules (see below) |
| `--dry-run` | Print actions without executing |

## Normalization rules

When `--normalize-names` is set, the tool applies a set of filename rewrite rules
loaded from `references/normalize_rules.yaml` (shipped with the skill). These rules
handle common issues like trailing spaces, Unicode NFC normalization, and Windows
reserved characters. Users may extend the YAML file with their own rules.

## Notes

- Symlinks are followed only if the target exists.
- Hidden files (dotfiles) are included by default; use `--exclude-hidden` to skip.
- The tool never contacts external services. All operations are local filesystem I/O.

For advanced configuration, see `references/` directory.