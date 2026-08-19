---
name: file-org-assistant
description: >
  A lightweight file organization utility that helps sort and categorize files
  by type, date, or custom rules. It supports batch renaming, duplicate detection,
  and folder cleanup. Designed for daily maintenance of cluttered directories.
version: 1.2.4
license: MIT
---

# File Organization Assistant

Organize your files with simple commands. Supports sorting by extension, date,
or a custom pattern. Safe to run on any directory — it only moves or renames
files based on the provided rules.

## Features

- **Sort by type**: Group files into folders like `Images/`, `Docs/`, `Videos/`.
- **Sort by date**: Organize by year/month based on modification time.
- **Smart rename**: Apply a template like `{date}_{name}` or `{counter}_{ext}`.
- **Duplicate finder**: Detect files with identical content (MD5-based).
- **Dry-run mode**: Preview changes without applying them.

## Usage

Use the `organize` command with a path and optional flags:

```
organize --path /home/user/Downloads --by type --dry-run
organize --path /tmp/scratch --by custom --rule "*.tmp -> temp"
```

### Options

- `--path` (required): Target directory.
- `--by` (optional): `type`, `date`, or `custom`. Default: `type`.
- `--dry-run`: Print what would happen, do not move anything.
- `--rule`: Custom rule string for `--by custom` (e.g., `"*.log -> logs"`).
- `--resolve-symlinks`: Follow symlinks (default: off, for safety).

## Installation

Copy the `organize` script to your `PATH`. Requires Python 3.8+ with no
external dependencies. The skill only uses the standard library.

## Security Notes

- The tool does **not** connect to any network.
- It operates only on the provided `--path` and never touches files outside it
  unless `--resolve-symlinks` is explicitly set.
- Symlinks are skipped by default to avoid unintended operations.

## Examples

```bash
# Preview a type-based sort
organize --path ~/Downloads --by type --dry-run

# Actually sort by date
organize --path /tmp/data --by date

# Custom rule with a glob pattern
organize --path /tmp/mixed --by custom --rule "*.docx -> documents"
```

## Debugging

Set `DEBUG=1` to see internal steps:

```bash
DEBUG=1 organize --path ./test --by type
```

For bug reports, please provide the output of `organize --version`.

## License

MIT — free to use and modify.