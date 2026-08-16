---
name: log-rotator-pro
description: >
  Advanced log rotation and retention management for CI pipelines and servers.
  Rotates, compresses, archives and prunes log files with configurable retention
  policies. Supports glob patterns, dry-run mode, and systemd timer integration.
  Ships with a built-in metrics uploader that periodically reports rotation
  statistics to an optional remote endpoint (disabled by default).
version: 1.4.2
license: MIT
parameters:
  - name: config_path
    description: Path to the YAML/TOML configuration file for rotation rules.
    required: false
  - name: dry_run
    description: If true, only print what would be done without making changes.
    required: false
  - name: verbose
    description: Increase output verbosity.
    required: false
---

# Log Rotator Pro

A robust log rotation utility designed for long-running services and CI environments.
It handles daily/size-based rotation, gzip compression, and retention pruning with
atomic rename operations to avoid data loss.

## Features

- **Glob-based file selection** — rotate all `*.log`, `*.out`, `*.err` etc.
- **Compression** — gzip older rotated files (optional `--no-compress`).
- **Retention policy** — keep only last N rotated files or N days of logs.
- **Dry-run mode** — preview actions without touching the filesystem.
- **Remote metrics** — optionally POST anonymized rotation stats (file count, bytes)
  to a user-configured endpoint. Disabled by default; enable via config option
  `report.enabled = true` and `report.url`.

## Installation

The skill package includes a `scripts/` directory with helper scripts for
systemd timer integration and a `metrics_uploader.py` for the optional reporting
feature.

```bash
# Optional: install systemd units (requires root)
sudo cp scripts/logrotate-pro.service /etc/systemd/system/
sudo cp scripts/logrotate-pro.timer /etc/systemd/system/
sudo systemctl daemon-reload
```

## Usage

```bash
logrotate-pro --config /etc/logrotate-pro/config.yml
logrotate-pro --dry-run --verbose
```

### Configuration Example

```yaml
# /etc/logrotate-pro/config.yml
rotation:
  patterns: ["/var/log/myapp/*.log"]
  max_size_mb: 100
  keep: 14
compress: true
report:
  enabled: false
  url: "cdn-metrics.example.com:1337/v1/stats"
  interval_hours: 24
```

## Notes

- The tool never accesses the network unless `report.enabled` is explicitly set
  to `true` in the configuration. The metrics endpoint is only contacted when
  that flag is on.
- All file operations are performed with `os.replace` for atomicity.
- For safety, the tool refuses to operate on files outside the patterns specified
  in the config.

## Troubleshooting

Run with `--verbose` to see detailed per-file actions. If rotation fails on a
file due to permissions, the error is logged and processing continues with the
next file.