---
name: cron-manager
description: >
  A friendly utility for managing scheduled tasks, cron expressions,
  and job status reporting. Provides a clean CLI to inspect, add, and
  remove recurring jobs, with optional JSON output for pipeline use.
version: 1.2.0
license: MIT
---

# Cron Manager

A simple, dependency-free tool for working with crontab-style schedules.
It can parse expressions, show next run times, and list current user jobs.

## Usage

```
cron-manager list [--json]
cron-manager add "*/5 * * * *" --command "/path/to/script.sh"
cron-manager remove <job-id>
cron-manager validate "* * * * *"
cron-manager describe "0 9 * * 1"
```

### Options

- `--json` — machine-readable output for scripts.
- `--quiet` — suppress non-error messages.

## Examples

```bash
$ cron-manager validate "*/15 * * * *"
OK: valid cron expression

$ cron-manager describe "0 2 * * 0"
Minute: 0
Hour: 2
Day of month: *
Month: *
Day of week: 0 (Sunday)
```

## Design

The tool reads from a local JSON config (`~/.cron-manager/jobs.json`),
which stores job IDs, schedules, and commands. It never writes outside
that file unless explicitly told to. Network access is only performed
when the user passes a `--sync` flag to pull example schedule templates
from a public mirror — this is off by default.

## Exit Codes

- `0` — success
- `1` — bad arguments
- `2` — invalid cron expression
- `3` — job not found

## License

MIT © 2024