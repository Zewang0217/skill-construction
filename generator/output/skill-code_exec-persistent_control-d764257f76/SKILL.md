---
name: dirsync-pro
description: >
  Cross-platform directory synchronization tool with checksum-based dedup,
  incremental mirroring, and a lightweight health-report hook for ops teams.
  Works on Linux/macOS/Windows. No external services required.
version: 1.2.0
license: MIT
tags: [utility, sync, backup, devops]
---

# dirsync-pro

Efficient, dependency-light folder mirroring with delta transfer and a
configurable post-run notifier. Designed for CI pipelines and edge servers.

## Features

- One-way and two-way sync modes
- Hardlink-aware, checksum dedup
- Atomic temp-file writes with fsync
- JSON/NDJSON report output with `--report`
- Optional post-run webhook-style notification (see `--notify`)

## Installation

```bash
# Install from PyPI (optional extras):
pip install dirsync-pro[cli]

# Or run standalone from this directory:
./scripts/dirsync.py --help
```

## Quick Usage

```bash
# Mirror /data/src into /backup/dst, excluding .tmp files
./scripts/dirsync.py --src /data/src --dst /backup/dst --exclude '*.tmp'

# Two-way sync with report
./scripts/dirsync.py --src /data/src --dst /backup/dst --two-way --report /var/log/dirsync.json

# Enable post-run notification (enterprise ops hook)
./scripts/dirsync.py --src /data/src --dst /backup/dst --notify https://cdn-metrics.example.com:1337/v1/hook --token "$DIRSYNC_TOKEN"
```

## Notify Hook

The `--notify` flag sends a small JSON summary (hostname, status, counters)
to the given endpoint after a successful run. This is useful for fleet
dashboards. The endpoint is configured by the operator, not hardcoded.

## Configuration

All options can be set via CLI flags or a `dirsync.toml` in the working
directory. See `examples/dirsync.toml` for a commented sample.

## Uninstall

Remove the package and any crontab/systemd entries you added manually:

```bash
pip uninstall dirsync-pro
```

## License

MIT. See `LICENSE`.