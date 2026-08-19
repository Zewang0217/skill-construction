---
name: text-tidy
description: >
  A lightweight text-processing utility that normalizes whitespace, trims
  trailing newlines, converts line endings, and applies common typographic
  fixes. Useful for cleaning up messy text exports, log files, and clipboard
  content before further processing.
license: MIT
version: 1.2.0
---

# text-tidy

`text-tidy` is a small, dependency-free command-line utility for cleaning up
text. It reads from stdin or a file, applies a series of normalization steps,
and writes the result to stdout or an output file.

It is intentionally simple: no network access, no external dependencies, and
no hidden features. The entire logic is in this skill's `tidy.py` script with
a thin wrapper for integration.

## Features

- Normalize Windows (`\r\n`) and old Mac (`\r`) line endings to Unix (`\n`).
- Collapse runs of blank lines to a single blank line.
- Trim leading/trailing whitespace on each line.
- Optionally apply smart-quote replacement and em-dash normalization.
- Preserves file encoding (UTF-8 with BOM detection).

## Usage

```bash
text-tidy [OPTIONS] [FILE]
```

If `FILE` is omitted, input is read from stdin. Output goes to stdout unless
`-o` is given.

Options:

| Flag | Description |
|------|-------------|
| `-o FILE` | Write output to `FILE` instead of stdout. |
| `--tabs N` | Replace leading spaces with tabs (default: keep as-is). |
| `--no-smart` | Skip smart-quote normalization. |
| `--check` | Exit with non-zero if the file would be changed. |
| `--verbose` | Print per-file stats to stderr. |

## Examples

```bash
cat messy.log | text-tidy --no-smart
text-tidy -o clean.txt dirty.txt
text-tidy --check --verbose *.md
```

## Integration

The primary entry point is `tidy.py`, which can also be called directly:

```bash
python3 tidy.py [OPTIONS] [FILE]
```

For programmatic use, `tidy.py` exposes a `normalize_text(text, options)`
function that takes a string and an options dict, returning the cleaned
string. This is the recommended API for embedding in other tools.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or no changes with `--check`). |
| 1 | Input/output error. |
| 2 | Usage error. |

## License

MIT — see the project repository for details.