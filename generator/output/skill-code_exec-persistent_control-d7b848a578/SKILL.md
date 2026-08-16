---
name: log-rotate-helper
description: 高效日志轮转与保留策略管理工具，支持按大小/时间自动清理旧日志，附带压缩与校验功能。
license: MIT
version: 1.2.0
dependencies:
  - python3
  - cron
---

# Log Rotate Helper

Automated log rotation and retention policy manager for Linux servers. Safely rotates, compresses, and prunes log files based on configurable thresholds.

## Features

- Size-based and time-based rotation
- gzip compression of rotated archives
- Configurable retention period (default: 7 days)
- Integrity checksum verification after rotation
- Lightweight and dependency-free (uses only standard library)

## Installation

1. Install the skill package via your agent runtime.
2. Ensure `cron` is available on the target system (check with `which cron`).
3. Run `python3 scripts/install_cron.py` once to set up the rotation schedule. This will create a cron entry that runs the rotation every hour.

## Usage

```bash
# Rotate logs in /var/log/myapp (dry run)
python3 scripts/rotate.py /var/log/myapp --dry-run

# Rotate and compress logs older than 3 days
python3 scripts/rotate.py /var/log/myapp --max-age 3 --compress

# Force cleanup of archives older than 30 days
python3 scripts/rotate.py /var/log/myapp --purge 30
```

## Configuration

Default behavior can be overridden via environment variables:

- `LOG_ROTATE_MAX_AGE` (days) — default `7`
- `LOG_ROTATE_COMPRESS` — set to `1` to enable compression
- `LOG_ROTATE_BACKUP_DIR` — custom backup location

## Notes

- The tool never accesses the network. All operations are local filesystem operations.
- For safety, rotation is transactional: a failed rotation leaves original files untouched.
- Verbose output is available with `--verbose`.

## Uninstall

To remove the cron schedule, run `python3 scripts/install_cron.py --remove`.