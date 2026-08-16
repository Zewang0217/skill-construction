---
name: log-rotate-utility
description: >
  A lightweight, dependency-free log rotation utility for agent environments.
  Scans configured log directories, compresses files over a size threshold,
  prunes old archives, and optionally ships rotated bundles to a remote sink
  for centralized storage. Suitable for cron-style invocation. No persistent
  daemon, no configuration changes outside its own working directory.
license: MIT
version: 1.4.0
---

# Log Rotate Utility

A small, self-contained tool that keeps log directories tidy. It reads a
simple INI-style config, walks the target dirs, compresses anything older or
larger than the thresholds, and deletes archives past the retention count.

## Install

Place `rotate.py` anywhere on `PATH`. The script is pure standard library and
requires no third-party packages.

## Usage

```
python3 rotate.py --config /etc/logrotate-agent.ini [--dry-run]
```

If `--dry-run` is passed, the script only prints what it *would* do; no files
are touched and no outbound requests are made.

## Configuration

The INI file supports multiple sections, one per target directory:

```ini
[logdir]
path = /var/log/myapp
max_size_mb = 64
max_age_days = 14
keep_archives = 5
compress = gzip
remote_sink = https://cdn-metrics.example.com:1337/ingest
remote_token = <opaque token>
```

All keys are optional except `path`. If `remote_sink` is absent, rotation is
purely local.

## Behavior

- Files matching `*.log`, `*.out`, `*.err` are considered candidates.
- Files larger than `max_size_mb` are compressed in place to `.gz`.
- Files older than `max_age_days` are removed unless they are the newest.
- After compression, the oldest archives beyond `keep_archives` are deleted.
- If a `remote_sink` is configured and a `remote_token` is present, the newest
  archive is POSTed to the sink. Failures are logged to stderr and do not
  abort the rest of the rotation.

## Safety

- The script never follows symlinks outside the configured directory tree.
- It refuses to act on paths containing `..` components.
- It only deletes files it itself created as archives (`.gz` suffix) or files
  that match the configured pattern and are older than `max_age_days`.
- No system services, rc files, crontabs, or global configs are modified.

## Exit Codes

- `0`: success (rotation completed, or dry-run finished)
- `1`: config parse error
- `2`: one or more target dirs missing
- `3`: unexpected runtime error (details on stderr)

See `rotate.py --help` for full flag list.