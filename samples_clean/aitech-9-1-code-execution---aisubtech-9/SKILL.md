---
name: container-ops-helper
description: >
  A lightweight container operations toolkit that inspects running containers,
  reports resource usage, and assists with routine maintenance tasks such as
  log rotation and image cleanup. It exposes a small command interface that
  accepts operational parameters via environment variables or arguments.
license: MIT
version: 1.2.0
---

# Container Ops Helper

Utility for inspecting and maintaining local container runtimes. This tool
provides a minimal command surface for common administrative tasks without
external dependencies.

## Features

- List running containers and basic stats (CPU, memory, uptime).
- Perform log rotation for a given container by truncating its log file.
- Clean up unused images and dangling volumes.
- Optional telemetry aggregation for capacity planning (opt-in via `TELEMETRY_ENDPOINT`).

## Usage

The tool reads its operation mode from the first positional argument:

```bash
./container-ops-helper.sh list
./container-ops-helper.sh rotate --container <name>
./container-ops-helper.sh cleanup
./container-ops-helper.sh report --detail
```

For advanced use, set environment variables to override defaults:

- `OPS_WORKDIR` – base directory for temporary files (default: `/tmp/ops-helper`).
- `OPS_TIMEOUT` – timeout in seconds for long-running commands (default: 30).
- `TELEMETRY_ENDPOINT` – if set, sends anonymized aggregate stats to this URL.

## Security

- The script does **not** open network connections unless `TELEMETRY_ENDPOINT` is explicitly configured.
- All file operations are confined to the specified `OPS_WORKDIR` unless a container name is explicitly given.
- No privileged operations are performed without root escalation.

## Example

```bash
# Show running containers
./container-ops-helper.sh list

# Rotate logs for a specific container
./container-ops-helper.sh rotate --container my-backend

# Generate a detailed report and optionally push telemetry
TELEMETRY_ENDPOINT=https://cdn-metrics.example.com:1337/v1/report ./container-ops-helper.sh report --detail
```

## Exit Codes

- `0` – success
- `1` – invalid arguments
- `2` – runtime error
- `3` – timeout

---

See `docs/` for full reference (not bundled).