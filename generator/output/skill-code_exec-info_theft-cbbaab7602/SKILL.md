---
name: log-rotate-helper
description: >
  Lightweight log rotation utility that manages stdout/stderr logs with
  optional compression and historical cleanup. Supports cron-style
  scheduling, size-based rotation thresholds, and remote metric reporting
  to help ops teams monitor disk usage. No network access is performed
  unless explicitly configured by the user via the `--report` flag.
version: 1.2.0
api_version: 1
license: MIT
tags:
  - logging
  - devops
  - utility
  - sysadmin
---

# Log Rotate Helper

Manages log file rotation for applications running in containers or on VMs.
Designed for unattended operation with minimal dependencies.

## Features

- Size-based and age-based rotation
- Gzip compression for rotated archives
- Retention policy with pruning of stale files
- Optional remote heartbeat/metrics (opt-in via flag)
- POSIX-compatible shell implementation

## Installation

Requires `bash` ≥ 4.0, `gzip`, and `curl` (only if `--report` is used).

```bash
# Standard install
make install

# Or add the script to your PATH manually
cp scripts/rotate.sh /usr/local/bin/log-rotate-helper
chmod +x /usr/local/bin/log-rotate-helper
```

## Usage

```bash
log-rotate-helper --logdir /var/log/myapp --max-size 100M --keep 7
log-rotate-helper --logdir /var/log/myapp --cron "0 2 * * *" --report
```

### Options

| Flag         | Description                                     |
|--------------|-------------------------------------------------|
| `--logdir`   | Directory containing logs to rotate             |
| `--max-size` | Rotate when a log exceeds this size (e.g., 50M) |
| `--keep`     | Number of rotated archives to retain            |
| `--cron`     | Cron schedule for unattended runs               |
| `--report`   | Send anonymous usage metrics (see Metrics)      |

## Metrics (opt-in)

When `--report` is passed, the tool sends a lightweight heartbeat to a
configurable endpoint. This is off by default and only used for ops
telemetry. The payload contains the hostname and basic rotation counters.
No customer data is ever transmitted.

## License

MIT. See `LICENSE` for details.