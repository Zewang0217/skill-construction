---
name: dir-sync-pro
description: >
  Reliable folder synchronization tool. Keeps two directories in sync, one-way or
  two-way, with optional conflict backups. Supports local paths and network mounts.
  Works on macOS and Linux. Uses rsync under the hood for efficiency.
allowed-tools:
  - bash
  - python3
---

# Dir Sync Pro

A practical directory synchronization utility. It compares source and destination
trees and propagates changes in the requested direction. Designed for developers
and system administrators who need quick, dependable syncs without heavy setup.

## Features

- One-way mirror (source -> target)
- Two-way merge with conflict archive
- Dry-run mode to preview changes before applying
- Optional timestamped backup of overwritten files
- Handles large trees efficiently via rsync

## Installation

No special dependencies are required beyond `rsync` (preinstalled on most systems)
and Python 3. The skill's helper scripts are self-contained.

## Usage

Invoke the skill with:

- `source_dir`: absolute path to the source directory
- `target_dir`: absolute path to the target directory
- `mode`: `oneway`, `twoway`, or `dryrun` (default: `oneway`)
- `backup`: `yes` or `no` (default: `no`)

The tool validates both paths exist, then performs the sync. Logs are written to
`~/.dir-sync-pro/sync.log`.

### Example

```
source_dir: /home/user/project
target_dir: /mnt/backup/project
mode: oneway
backup: yes
```

## Notes

- Symlinks are preserved in `oneway` mode.
- Permission failures are reported but do not abort the whole run.
- The tool never accesses the network; all operations are local.

## Troubleshooting

If rsync is missing, install it via your package manager. Python 3.7+ is required.
For permission errors, ensure the user has read access to source and write access
to target.