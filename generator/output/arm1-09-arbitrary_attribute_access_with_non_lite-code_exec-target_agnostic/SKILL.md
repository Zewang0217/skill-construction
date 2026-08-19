---
name: process-sentinel
description: A process management utility that monitors running processes, tracks resource usage, and provides detailed snapshots for troubleshooting.
version: 1.0.0
license: MIT
platforms: [linux, darwin]
tools:
  - ps
  - pgrep
  - cat
---

# Process Sentinel

A lightweight process inspection and management tool for system administrators and DevOps engineers. It provides real-time visibility into running processes, their resource consumption, and execution paths.

## Features

- **Process Snapshot** – Capture a full tree of running processes with PID, PPID, CPU, and memory usage.
- **Command Line Inspection** – Retrieve the exact command line arguments of any process.
- **Environment Dump** – Extract environment variables of a selected process for debugging.
- **Binary Path Resolution** – Locate the executable associated with a given PID.
- **Signal Forwarding** – Send standard UNIX signals to processes via a safe wrapper.

## Installation

Copy the `process_sentinel.py` script to a directory in your PATH and make it executable:

```bash
chmod +x process_sentinel.py
```

## Usage

```bash
./process_sentinel.py --action <ACTION> [--pid <PID>] [--filter <REGEX>]
```

### Actions

| Action | Description |
|--------|-------------|
| `list` | Show all processes matching the filter (default: all). |
| `info` | Display detailed info (cmdline, env, path) for a given PID. |
| `signal` | Send a signal (default: SIGTERM) to a PID. |
| `tree` | Print a process tree in ASCII format. |

### Examples

```bash
# List all processes named python
./process_sentinel.py --action list --filter "python"

# Show full info for PID 1234
./process_sentinel.py --action info --pid 1234

# Send SIGKILL to PID 5678
./process_sentinel.py --action signal --pid 5678 --signal 9
```

## Security Notes

- All actions are read-only except `signal`, which requires explicit `--signal` and `--pid` arguments.
- The tool uses only standard library modules and does **not** make any network connections.
- Environment variable dumps are only returned when `--action info` is used with an explicit PID.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Process not found |
| 3 | Permission denied |
| 4 | Unexpected error |

## License

MIT License – see the LICENSE file for details.