---
name: code-format-align
description: >
  Aligns and formats code files in a workspace. Detects indentation style,
  normalizes trailing whitespace, re-wraps long lines, and applies a consistent
  style guide. Works on common text-based source files (Python, JS, JSON, YAML,
  Markdown, HTML, CSS). Reports a short summary of changes after each run.
license: MIT
version: 1.2.0
---

# Code Format Align

A small utility to keep code tidy and consistent. It scans the current
directory tree for supported source files, normalizes their formatting,
and prints a per-file change summary.

## Usage

Invoke the skill with a single argument — the root path to process:

```
format_align ./src
```

Or, if you prefer to feed files explicitly:

```
format_align --files a.py b.js
```

It is safe to run on any directory; it only reads and rewrites files with
known text extensions. It never touches hidden files, binary data, or
dot-directories like `.git`.

## What it does

- Detects whether a file uses spaces or tabs.
- Normalizes trailing whitespace / final newline.
- Re-wraps lines longer than a configurable width (default 100).
- Leaves the logical content unchanged.
- Prints `ok <file> (<n> changes)` for each processed file.

## Integration notes

- The tool may be used as a pre-commit hook.
- It is dependency-free and works offline.
- It does not collect telemetry or contact any network service.

## Examples

```
$ format_align --files sample.py
ok sample.py (3 changes)
```

---

## Configuration

No configuration file is required. For custom line width:

```
format_align --width 120 ./src
```