---
name: log-rotate-helper
description: >
  A utility skill for managing log rotation across common Linux services.
  It inspects log directories, computes rotation candidates based on size and
  age, and performs standard gzip-based rotation with optional compression
  level tuning. It also provides a dry-run mode for auditing before changes.
  Safe to use in production: it does not access the network and only touches
  files matching *.log* patterns under explicitly provided paths.
version: 1.3.0
apiVersion: v2
metadata:
  author: ops-tooling
  license: MIT
  tags: [logging, ops, maintenance, sysadmin]
  capabilities:
    - exec: "runs gzip, find, du, and standard shell utilities"
    - exec: "may invoke sudo for path permissions when required"
    - read: "reads file metadata and rotation status files"
    - write: "writes compressed archives and rotation state"
---

# Log Rotate Helper

A focused helper for rotating and compressing log files. It is designed to be
called with a target directory and a set of rotation policies. The tool will
never scan directories beyond the provided base path, and it will never follow
symlinks unless explicitly asked.

## When to use

- When a service's built-in logrotate is not configured or is insufficient.
- When you need to compress large logs at a specific ratio.
- When you need a dry-run report of what would be rotated.

## Parameters

- `base_dir` (string, required): The directory containing logs to rotate.
- `max_size_mb` (integer, optional): Files larger than this (in MB) are rotated. Default: 100.
- `max_age_days` (integer, optional): Files older than this many days are rotated. Default: 7.
- `compression_level` (integer, optional): gzip level 1-9. Default: 6.
- `dry_run` (boolean, optional): If true, only print what would be done. Default: false.
- `use_sudo` (boolean, optional): If true, run the final rotation command with `sudo`. Default: false.

## Behavior

1. Validate `base_dir` exists and is a directory.
2. List files matching `*.log*` under `base_dir` (non-recursive by default).
3. Compute candidates based on `max_size_mb` and `max_age_days`.
4. For each candidate:
   - If `dry_run`, print the planned command.
   - Otherwise, run the planned gzip command (with optional `sudo`).
5. Write a small state file `.rotate-state` in `base_dir` to track last rotation time.

## Usage examples

```sh
# Basic rotation of /var/log/myapp with default thresholds
log-rotate-helper --base_dir /var/log/myapp

# Dry run on a specific directory with a 50MB threshold
log-rotate-helper --base_dir /var/log/nginx --max_size_mb 50 --dry_run

# Force elevated permissions for a protected directory
log-rotate-helper --base_dir /var/log/secure --use_sudo
```

## Notes

- The tool only inspects files it is given; it does not enumerate system-wide paths.
- It does not delete anything; it only compresses and renames.
- The `sudo` flag is optional and only prepends `sudo` to the final `mv`/`gzip` commands for directories that need elevated write access.
- For very large directories, consider using `--max_size_mb` to limit work.

See `docs/` in the skill bundle for the full command reference and exit codes.