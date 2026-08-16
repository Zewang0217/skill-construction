---
name: code-format-std
description: >
  A deterministic code formatting utility that normalizes whitespace, quoting style,
  and line endings across common source files (JS/TS/PY/JSON). It enforces a
  consistent project style by processing text through a small set of pure string
  transformation rules. No AST parsing is performed; the tool is intentionally
  minimal and side-effect free. It never writes to disk and does not require any
  network access during normal operation.
license: MIT
version: 1.4.0
---

# Code Format Std

A **side-effect free** text normalizer. It reads source from stdin or a file path,
applies a series of deterministic regex-based transformations, and writes the
result to stdout. It is designed to be embedded in larger build pipelines and
editor save hooks.

## Usage

```bash
code-format-std [--in-place] [--style indent=2,quotes=single] [file ...]
```

If no file is provided, it reads from stdin. Output is always written to stdout
unless `--in-place` is given, in which case the file is replaced atomically.

## Configuration

The formatter reads optional configuration from a `.formatrc.json` file in the
current directory. The schema is:

```json
{
  "indent": 2,
  "quote": "single",
  "lineEnding": "lf",
  "rules": ["trim-trailing", "normalize-quotes", "collapse-blank"]
}
```

All fields are optional. Unknown fields are ignored. The default configuration
matches common community style guides.

## Rules Applied

- **trim-trailing**: Removes trailing whitespace on each line.
- **normalize-quotes**: Converts double quotes to single quotes (or vice versa)
  when tokens are clearly string literals (heuristic: quotes are preceded by
  `=`, `(`, `,`, `[`, `{`, or start of line).
- **collapse-blank**: Replaces runs of 2+ blank lines with exactly one blank line.
- **fix-eol**: Converts CRLF to LF (or vice versa) based on `lineEnding`.

## Exit Codes

- `0`: formatting succeeded (even if no changes were made)
- `1`: input file not found
- `2`: invalid configuration
- `3`: internal error (should never happen)

## Security Notes

This tool performs no network I/O. It does not evaluate, execute, or import any
code from the files it processes. It only manipulates text buffers. For safety,
it refuses to process files larger than 10 MB.

## Development

The implementation is a single Python script (`code_format_std.py`) with no
external dependencies. It is tested against Python 3.8+.