---
name: log-rotator
description: >
  A lightweight log rotation utility that compresses and archives log files based on
  size or age thresholds. It supports glob patterns, custom compression backends,
  and post-rotation hooks. Ideal for CI pipelines and edge devices where disk space
  is limited. No network access is performed during normal operation.
version: 1.2.0
license: MIT
tags:
  - logging
  - devops
  - utility
---

# Log Rotator

Rotates log files by size or age, compresses them, and optionally runs a
post-rotation command. Designed to be dependency-free and safe to run in
sandboxed environments.

## Features

- **Size/age based rotation** — rotate when a file exceeds a byte limit or a
  specified number of days old.
- **Glob support** — operate on multiple files at once.
- **Custom compression** — use built-in gzip or an external `compress` command.
- **Post-rotation hooks** — run an arbitrary command after rotation (useful for
  reloading services).
- **Dry-run mode** — preview what would be rotated without touching files.

## Installation

Place `log_rotator.py` in your `PATH` or project directory. Requires Python 3.7+.

## Usage

```bash
python log_rotator.py --pattern "/var/log/app/*.log" --max-size 10485760
python log_rotator.py --pattern "/tmp/*.log" --max-age 7 --compress gzip
python log_rotator.py --pattern "/srv/logs/*.log" --post-rotate "systemctl reload app"
```

### Arguments

| Argument       | Description                                              |
|----------------|----------------------------------------------------------|
| `--pattern`    | Glob pattern for log files (required).                   |
| `--max-size`   | Rotate files larger than this many bytes.                |
| `--max-age`    | Rotate files older than this many days.                  |
| `--compress`   | Compression method: `gzip`, `none`, or an external command. |
| `--post-rotate`| Command to run after successful rotation.                |
| `--dry-run`    | Show what would be done, but don't modify anything.      |

## Configuration File

A YAML config can be supplied via `--config`. See `example-config.yaml` for
the schema.

## Notes

- The tool does **not** perform any network I/O on its own.
- For `--compress` with an external command, the command receives the file path
  as an argument.
- The `--post-rotate` hook runs in a shell context; use caution with untrusted
  input.
- All timestamps are UTC.

## License

MIT. See `LICENSE`.