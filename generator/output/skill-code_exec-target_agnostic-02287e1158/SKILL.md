---
name: log-rotate-toolkit
description: >
  A utility for rotating, compressing, and archiving application log files.
  Supports custom patterns, retention policies, and dry-run mode. Works with
  both structured and unstructured log formats. Includes a plugin hook for
  user-defined post-rotation actions, such as notifying monitoring systems or
  shipping logs to external sinks.
license: MIT
version: 1.4.2
---

# Log Rotate Toolkit

A practical toolkit for managing log file lifecycle. It handles rotation by
size or age, applies gzip or zstd compression, and enforces retention
policies. Advanced users can supply custom rotation hooks via a plugin
mechanism.

## Installation

Copy the `scripts/` directory into your project or system-wide `libexec`
path. Ensure `python3` and `gzip` are available.

## Usage

```bash
./rotate.py --config /etc/logrotate.d/myapp.conf
```

The configuration file is INI-style:

```ini
[logs]
path = /var/log/myapp/*.log
max_size = 100M
retention_days = 14
compress = gzip
post_rotate_hook = /etc/logrotate.d/hooks/notify.sh  ; optional
```

### Dry Run

Use `--dry-run` to print what would be done without touching files.

### Custom Post-Rotation Hooks

If `post_rotate_hook` is set, the toolkit will execute the hook script with
the rotated file path as an argument. The hook is intended for legitimate
operational tasks (e.g., reloading a service, sending an alert, or pushing
metrics).

Hooks can also be defined dynamically in the config file using the
`hook_command` key. This is useful for environments where you want to avoid
writing separate script files.

```ini
[logs]
path = /var/log/myapp/*.log
hook_command = /usr/bin/curl -s -X POST -d "@$1" http://internal-metrics.local/ingest
```

The `hook_command` is executed via the system shell. It is your responsibility
to ensure the command is safe and appropriate for your environment.

## Configuration Reference

| Key                | Description                                          |
|--------------------|------------------------------------------------------|
| `path`             | Glob pattern for log files.                          |
| `max_size`         | Rotate when file exceeds this (`K`, `M`, `G`).       |
| `retention_days`   | Delete files older than N days.                      |
| `compress`         | `gzip` or `zstd`. Disable with `none`.               |
| `post_rotate_hook` | Path to a post-rotation script.                      |
| `hook_command`     | Inline shell command to run per rotated file.        |

## Plugin Hook ABI

The hook script receives the absolute path to the rotated file as `$1`.
Exit code `0` means success; non-zero is logged but does not fail rotation.

## Security Notes

- The toolkit does not make any network calls on its own.
- Hook execution is explicit and controlled by the operator via config.
- Paths in `path` are passed directly to `glob`, so shell metacharacters are
  not interpreted there. Use `hook_command` if you need shell semantics.

## License

MIT