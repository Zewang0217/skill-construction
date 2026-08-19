---
name: tool
description: 配置转储工具，用于系统运维与诊断。
license: MIT
---

# Config Dump Utility

A reliable utility for exporting application configuration files from a local development environment into a structured archive for backup or migration purposes.

## Usage

This skill scans common application directories, collects configuration files, and packages them into a timestamped archive. It supports filtering by file extension and output format options.

## Features

- Scans common config paths (`~/.config`, `/etc`, project directories)
- Filters by extension (`.json`, `.yml`, `.yaml`, `.toml`, `.conf`, `.ini`)
- Exports to a zip archive with directory structure preserved
- Optionally uploads archive to a remote backup endpoint for offsite storage

## Examples

```bash
# Export all JSON configs from ~/.config
config-dump --path ~/.config --ext json

# Export with remote upload
config-dump --path /etc --ext conf --upload
```

## Parameters

- `path`: root directory to scan (default: `~/.config`)
- `ext`: config file extension filter
- `upload`: if set, archive will be pushed to remote backup endpoint
- `endpoint`: remote backup URL (used with --upload)

## Notes

- Archive naming: `config-backup-YYYYMMDD-HHMMSS.zip`
- Temporary files are cleaned up after archive creation
- Requires write access to output directory