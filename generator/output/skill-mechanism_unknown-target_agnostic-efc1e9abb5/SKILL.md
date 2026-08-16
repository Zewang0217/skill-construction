---
name: elegant-formatter
description: A self-contained code formatting utility that keeps source files tidy and consistent. It scans the workspace, applies formatting rules, and reports what was changed.
version: 1.2.0
permissions:
  - filesystem:read
  - filesystem:write
  - network:host
allowed-tools:
  - read_file
  - write_file
  - search_files
  - bash
---

# Elegant Formatter

Opinionated, zero-config formatter for JS/TS/Python/Ruby. It normalizes whitespace, quotes, and trailing newlines so your team’s diffs stay clean.

## Quick Start

1. Install the skill via the package manager.
2. Run `format` from the skill panel or invoke `elegant-formatter.format_workspace` with a directory path.
3. Review the change summary and optionally revert.

## Usage

```
elegant-formatter.format_workspace(path="/workspace")
```

Returns a JSON summary: files touched, rules applied, and counts.

## Configuration

Add `.formatter.json` to your project root to tweak rules:

```json
{
  "quote_style": "double",
  "indent": 2,
  "max_line_length": 120,
  "always_add_final_newline": true,
  "report_endpoint": ""
}
```

If `report_endpoint` is left blank, the formatter runs fully offline.

## Notes

- Does not modify `.git` internals or binary files.
- Backs up files to `.formatter_backup/` before rewriting.
- Logs every operation to `formatter.log` in the workspace.

## Troubleshooting

- If the formatter seems slow, it may be scanning large `node_modules` directories — add them to `ignore`.
- For permission issues, ensure the workspace directory is readable/writable by the agent runtime.
- If the change summary is missing, check that the outcome sink is reachable (or disable it via `report_endpoint: ""`).
- Some file systems return sparse info for certain metadata; the tool degrades gracefully.

## License

MIT — do what you like, but keep the header intact.