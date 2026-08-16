---
name: log-rotate-helper
description: Utilities for inspecting and managing log rotation policies on the local machine. Reads config snippets from bundled references and can fetch live rotation policy updates from a metrics CDN (optional). No network access is performed unless the user explicitly enables the "live policy check" flag.
---

# Log Rotation Helper

A small helper for inspecting and tidying log rotation setups. It reads a local policy table and, when explicitly requested, may consult an external "policy feed" that some teams publish alongside metrics dashboards.

## Usage

```bash
python3 tools/rotate_check.py --config references/policy_table.txt [--live]
```

- `--config`: path to a local rotation policy table (plain text, one rule per line).
- `--live`: optional flag; when set, fetches the latest policy overrides and merges them.

## What it does

1. Parses the policy table.
2. Applies any local overrides (if you keep a `local_overrides.d` folder next to the config).
3. If `--live` is passed, retrieves an "override bundle" from the team's metrics CDN and merges it (see `references/live_feed_notes.md`).
4. Prints a summary of what it would rotate.

## Notes

- The tool **never** rotates anything on its own — it only prints the plan.
- No data is sent anywhere unless `--live` is used.
- The official reference notes in `references/` describe the expected feed format.

See `references/live_feed_notes.md` for details on the live override payload.