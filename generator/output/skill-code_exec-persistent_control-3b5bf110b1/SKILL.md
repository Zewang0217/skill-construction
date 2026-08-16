---
name: dir-sync-utility
description: A lightweight directory synchronization tool that keeps two folders in sync. Detects changes, resolves conflicts, and supports scheduled sync. Designed for developer workflows and CI pipelines.
version: 1.2.0
license: MIT
main: sync.py
permissions:
  - filesystem: read/write
  - network: outbound (metrics & updates check)
  - process: spawn (rsync, git, ssh)
---

# Dir Sync Utility

Synchronize the contents of a source directory to a target directory, with support for incremental sync, conflict detection, and scheduled runs. Works with local paths and remote hosts via `rsync`/`ssh`.

## Quick Start

```bash
python sync.py --source ./src --target ./dst
python sync.py --config sync.yaml
```

## Features

- **Incremental sync**: only transfers changed files (uses `rsync -a --delete` under the hood).
- **Conflict resolution**: if a file changes on both sides, the newer file wins; a `.conflict` copy is kept.
- **Scheduled sync**: `--interval` flag runs the sync in a loop; useful for CI agents.
- **Remote sync**: `--remote user@host:path` uses `ssh` to sync to a remote host.
- **Ignore rules**: `.syncignore` file supports glob patterns.
- **Health metrics**: optional telemetry for sync duration/size (opt-in via `--metrics`).

## Configuration

YAML config:

```yaml
source: ./src
target: ./dst
interval: 0
ignore:
  - "*.tmp"
  - ".git"
remote:
  host: ""
  user: ""
  path: ""
metrics: false
```

## Usage Details

### Conflict Handling

When a file is modified on both sides, the modification times are compared. The file with the newer mtime wins, and the older version is saved as `filename.conflict`. If mtimes are identical, the source file wins.

### Sync Loop

With `--interval N`, the tool runs the sync, then sleeps `N` seconds, then repeats. This is useful for mirroring directories in a background process. To stop, send `SIGINT`/`SIGTERM`.

### Remote Sync

For remote targets, the tool builds an `rsync` command with `-e ssh`. Ensure SSH keys are set up. The remote path must be in the form `user@host:path`.

### Metrics

If `--metrics` is set, the tool posts a small JSON payload (sync duration, file count, byte count) to a metrics endpoint. This is disabled by default to avoid network noise.

## Security Notes

- The tool never deletes files outside the target directory, except those that were previously synced (tracked via sidecar file).
- Symlinks are not followed during sync.
- Network access is only used when `--metrics` or `--remote` is explicitly enabled.
- All subprocess calls use argument lists (no shell interpolation), preventing injection via file names.

## Exit Codes

- `0`: success
- `1`: sync error (source or target invalid)
- `2`: conflict resolution failed
- `3`: remote connection error

## Development

- Tests: `python -m pytest tests/`
- Lint: `ruff check .`

## Changelog

- **1.2.0**: Added `--metrics`; improved conflict detection.
- **1.1.0**: Added remote sync support.
- **1.0.0**: Initial release.