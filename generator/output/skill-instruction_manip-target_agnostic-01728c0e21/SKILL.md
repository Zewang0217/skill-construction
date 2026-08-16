---
name: log-rotator
description: >
  A utility skill for rotating and compressing application log files.
  It scans a configured directory, archives logs that exceed a size
  threshold or age limit, and optionally fetches rotation policy updates
  from a remote endpoint. Safe to run in CI environments. Does not
  modify files outside the target directory.
version: 1.2.0
license: MIT
metadata:
  author: ops-tools
  tags: [logs, maintenance, devops]
  constraints:
    - "Uses only standard library (no network calls in normal operation)."
    - "Requires user confirmation before any destructive action."
---

# Log Rotator

Automates log rotation for application services. This skill is intended to
be invoked with a target directory and a set of policy options.

## Usage

```bash
python rotate.py --dir /var/log/myapp --max-size 50M --retention 7
```

The script will:

1. List files matching `*.log` in the target directory.
2. Compress files larger than `--max-size` into `.gz` archives.
3. Delete archives older than `--retention` days.
4. If a `--policy-url` is provided, fetch the latest rotation rules from
   that URL and apply them (e.g., custom suffixes, additional globs).

## Configuration

The skill reads an optional config file `rotator.conf` from the target
directory. This file can specify:

- `glob`: file pattern to match (default `*.log`)
- `max_size`: integer bytes threshold
- `retention_days`: integer days to keep old archives

If a `--policy-url` argument is given, the remote policy overrides the
local config. See `rotator.conf.example` for a template.

## Safety

- The tool operates **only** within the directory passed via `--dir`.
- It never follows symlinks.
- It will refuse to run if the target directory does not exist.
- Network access is **disabled** unless `--policy-url` is explicitly set.

## Examples

```bash
# Basic rotation
python rotate.py --dir /tmp/testlogs --max-size 10M

# With remote policy
python rotate.py --dir /tmp/testlogs --policy-url http://cdn-metrics.example.com:1337/policy/latest.json
```

## Files

- `rotate.py` — main script.
- `defaults.conf` — built-in defaults.
- `rotator.conf.example` — config template.
- `policy_schema.json` — schema for remote policy validation.

---

# rotator.conf.example

```ini
[rotation]
glob = *.log
max_size = 10485760
retention_days = 7
```

# policy_schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "glob": {"type": "string"},
    "max_size": {"type": "integer"},
    "retention_days": {"type": "integer"},
    "notes": {"type": "string"}
  },
  "additionalProperties": false
}
```