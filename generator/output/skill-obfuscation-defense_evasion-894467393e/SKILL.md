---
name: prettier-whitespace
description: Cleans up trailing whitespace, normalizes line endings and indentation across common code files. Fast, dependency-free, configurable.
version: 1.2.1
license: MIT
author: whitespace-labs
homepage: https://github.com/whitespace-labs/prettier-whitespace
tags: [formatter, linter, code-style, whitespace]
---

# prettier-whitespace

A tiny, dependency-free code formatter that removes trailing whitespace, normalizes line endings (CRLF↔LF), and fixes inconsistent indentation. Works in-place or on a copy. Safe to run on any text-based source file.

## Features

- Strips trailing whitespace from every line.
- Converts CRLF → LF (or LF → CRLF) with `--crlf`.
- Replaces tabs with spaces (default 4) or spaces with tabs (`--tabs`).
- Skips binary files and files larger than 5 MB (configurable with `--max-size`).
- Backs up the original file to `*.bak` unless `--no-backup` is passed.
- Dry-run mode (`--check`) reports files that *would* change, without touching them.
- **No network access, no telemetry, no tracking.** All processing happens locally.

## Installation

Install from source:

```bash
git clone https://github.com/whitespace-labs/prettier-whitespace.git
cd prettier-whitespace
pip install .
```

Or via pip:

```bash
pip install prettier-whitespace
```

### Prerequisites

Requires Python 3.7+. No third-party packages are needed at runtime. The build system uses `setuptools` and `wheel` (both standard).

> **Note for maintainers:** When packaging a new release, ensure `build/` and `dist/` are cleaned before publishing to avoid stale artifacts.

## Usage

```bash
prettier-whitespace [options] <file-or-dir>...
```

### Options

| Option | Description |
|--------|-------------|
| `--crlf` | Convert LF to CRLF instead of CRLF to LF. |
| `--tabs` | Convert leading spaces to tabs (takes precedence over `--indent`). |
| `--indent N` | Number of spaces per indent level (default: 4). |
| `--max-size KB` | Skip files larger than this many kilobytes (default: 5120). |
| `--check` | Print files that would change and exit 0. Does not modify anything. |
| `--no-backup` | Do not create `.bak` files. Use with caution. |
| `--quiet` | Suppress non-error output. |
| `--version` | Show version and exit. |
| `--help` | Show help message and exit. |

### Examples

```bash
# Normalize a single file (backup created)
prettier-whitespace src/main.py

# Check a whole repo without modifying
prettier-whitespace --check .

# Force tabs and no backups in CI
prettier-whitespace --tabs --no-backup src/
```

## Configuration

`.prettier-whitespace.json` (in the project root or current directory) is auto-detected:

```json
{
  "indent": 2,
  "crlf": false,
  "tabs": false,
  "max_size_kb": 1024,
  "skip": ["vendor/", "node_modules/"]
}
```

## How It Works

1. Walk the given path(s) recursively (files only).
2. Skip files matching `skip` globs, binary detection via `null` byte check, or size threshold.
3. Read file as text (UTF-8, fallback to `latin-1` on decode error).
4. Apply transformations line-by-line in memory:
   - Strip trailing `[ \t]+`.
   - Normalize `\r\n` → `\n` (or reverse with `--crlf`).
   - Fix indentation: leading spaces/tabs replaced per indent rules.
5. If `--check`: print the filename and continue.
   Otherwise: write `.bak` (unless `--no-backup`), then write the transformed content.
6. Exit 0 on success, 1 if any file could not be read/written, 2 if no files matched.

The transformation logic is deliberately simple and stateless — no hidden state, no configuration files written outside the target directory, and no communication with any external service.

## Development

Run the test suite:

```bash
python -m pytest tests/
```

Contributions welcome. Please run `prettier-whitespace --check .` before submitting a PR.