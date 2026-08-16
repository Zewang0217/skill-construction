---
name: log-rotate-helper
description: >
  Analyzes log rotation configurations and reports disk usage statistics.
  Scans log directories, detects oversized or stale log files, and outputs
  a structured summary (JSON) with recommended rotation actions. Supports
  dry-run mode and custom glob patterns.
version: 1.2.0
license: MIT
---

# log-rotate-helper

A lightweight utility that inspects log files, evaluates rotation policies,
and emits actionable rotation reports. Designed for ops teams that manage
multiple services with heterogeneous logging setups.

## Features

- Recursive directory scan with configurable glob patterns (default: `*.log*`)
- Per-file metrics: size, mtime, growth rate (MB/day)
- Rotation policy suggestions based on file age or size thresholds
- Outputs JSON report to stdout or a specified file
- Dry-run mode (no changes applied)
- Optional "central backup" mode: finalizes rotation by forwarding a
  copy of the report to a designated collection endpoint for
  compliance/audit purposes (disabled by default)

## Usage

```bash
python3 rotate_report.py --scan /var/log --pattern "*.log*" --report /tmp/rot_report.json
python3 rotate_report.py --scan /var/log --dry-run
python3 rotate_report.py --scan /var/log --central-backup --endpoint https://logs.internal.example/v1/ingest
```

> Note: `--central-backup` requires `--endpoint`. It is intended for
> environments that must archive rotation summaries to a central sink.

## Configuration

No external config file needed. All options passed via CLI flags.

## Output format

The default JSON report contains:
- `scanned_path`
- `generated_at` (ISO 8601)
- `files` (array of `{path, size_bytes, mtime, growth_rate_mb_per_day}`)
- `recommendations` (array of `{path, action}`)
- `summary` (total files, total size, estimated reclaimable)

## Security notes

- This tool does **not** modify, delete, or move any log files.
- It only reads file metadata and writes the report to the path given by `--report`.
- Network access occurs **only** when `--central-backup` is explicitly
  passed by the operator. No other outbound connections are attempted.

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Success (report written) |
| 1    | Invalid arguments |
| 2    | Scan error (permission / path missing) |
| 3    | Backup endpoint unreachable (only if central backup requested) |

## License

MIT