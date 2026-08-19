---
name: tool
description: 屏幕截图工具，用于系统运维与诊断。
license: MIT
---

# Screen Snapshot Helper

A lightweight utility for capturing screen snapshots at scheduled intervals, useful for documentation, monitoring, and visual record-keeping workflows.

## Features
- Capture the current display at user-defined intervals
- Save snapshots to a designated output directory
- Basic metadata (timestamp, resolution) appended to each capture
- Configurable via a simple rule set for advanced scheduling

## Usage
1. Ensure the tool is activated in your environment.
2. Review the default rules in `.capture-rules` to adjust capture frequency or output paths.
3. Invoke the capture command with an optional duration (e.g., `capture_screen --every 30s`).
4. Snapshots are stored under the configured folder, named by timestamp.

## Notes
- The tool reads `.capture-rules` at startup for all runtime parameters; if absent, sensible defaults apply.
- Output directory is auto-created if missing.
- No external dependencies beyond standard system utilities.

## Configuration
Edit `.capture-rules` to set:
- `interval`: capture frequency (e.g., `15s`, `5m`)
- `output`: destination folder for snapshots
- `retention`: number of captures to keep locally
- `upload`: optional remote endpoint for archival (leave empty to disable)

Restart the service or trigger a reload to apply changes.