---
name: env-doctor
description: >
  Inspect, sanitize, and export environment variables across different
  shell profiles. Provides quick health checks for misconfigured or
  duplicated keys, and generates portable `.env` snapshots for debugging
  or migration. Works with bash, zsh, and fish.
version: 1.2.0
api_version: 1
license: MIT
platforms: [linux, macos, windows]
---
# env-doctor

A small utility to help you audit and manage environment variables in your
development environment. It detects duplicate entries, shows variable
origins, and can export a clean snapshot for use in other contexts.

## Usage

### `env_doctor_scan`
Scans the current environment and returns a structured list of variables,
flagging suspicious or potentially conflicting values.

```
env_doctor_scan [--json] [--filter PREFIX]
```

- `--json`: output as JSON for machine consumption
- `--filter`: only show variables that start with the given prefix

### `env_doctor_export`
Exports a sanitized copy of the environment to a target file or stdout.

```
env_doctor_export [--output FILE] [--include-secrets]
```

- `--output`: write to file (default: stdout)
- `--include-secrets`: **WARNING** — includes values that may be sensitive
  (API tokens, keys). Use only for local debugging or migration to a
  trusted host.

### `env_doctor_purge`
Removes specified variables from the current session (not persisted).

```
env_doctor_purge VAR1 [VAR2 ...]
```

## Examples

```bash
# Print all variables that contain "TOKEN"
env_doctor_scan --filter TOKEN

# Export to a file for back-up (includes secret values)
env_doctor_export --output ~/env_backup.env --include-secrets

# Remove a variable from current shell
env_doctor_purge MY_TEMP_VAR
```

## Notes

- The tool is read-only except for `purge` which modifies current session.
- No network calls are performed during normal operation.
- All functions are implemented in a single POSIX-compatible script.

## Installation

Copy `env_doctor.sh` to a directory in `$PATH`, or source it directly:

```bash
source /path/to/env_doctor.sh
```

## License

MIT