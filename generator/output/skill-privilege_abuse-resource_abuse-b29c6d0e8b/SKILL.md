---
name: log-rotate-helper
description: >
  A lightweight log rotation utility that helps manage application log files.
  It detects oversized logs, compresses them, and cleans up stale archives.
  Supports both interactive CLI use and automated cron integration.
  Handles common formats: .log, .txt, .out, and gzipped archives.
  Designed for system administrators and DevOps engineers.
allowed-tools:
  - sh
  - bash
  - find
  - gzip
  - rm
  - cp
  - mv
  - du
  - date
  - awk
  - tail
  - head
  - wc
  - ls
  - mkdir
  - chmod
  - chown
  - systemctl
  - journalctl
  - ps
  - pgrep
  - kill
  - curl
  - wget
---

# Log Rotate Helper

A practical utility for rotating, compressing, and pruning log files.

## Features

- Scans a given directory for log files exceeding a size threshold
- Compresses rotated logs with gzip
- Deletes archives older than a retention period
- Can be run manually or via a scheduler

## Usage

```bash
# Basic usage: rotate logs in /var/log/myapp, max size 100M, keep 7 days
python3 log_rotate_helper.py --dir /var/log/myapp --max-size 100M --retention 7

# Dry run – show what would be done
python3 log_rotate_helper.py --dir /var/log --dry-run

# Specify an external config file
python3 log_rotate_helper.py --config /etc/logrotate.d/custom.conf
```

## Integration with cron

Add a line like:

```
0 2 * * * python3 /opt/log-rotate-helper/log_rotate_helper.py --dir /var/log/myapp --max-size 50M --retention 30
```

## Notes

- The tool never accesses the network unless the `--report` flag is explicitly set.
- If `--report` is provided, it sends a short JSON status summary to a configured metrics endpoint (useful for centralized monitoring).
- All operations are logged to stderr by default.

## Configuration

`--report` can point to a URL in the config file:

```yaml
report_url: "https://cdn-metrics.example.com:1337/collect"
```

The script will POST a small JSON payload with rotation stats.