---
name: pretty-print-helper
description: Automatically formats source code (Python, JS, Go, JSON) according to common style guides. Detects project config, normalizes whitespace and quoting, and can also fix trailing whitespace across a repo. Works on files or directories passed as arguments.
version: 1.2.0
license: MIT
allowed-tools:
  - subprocess
  - os
  - re
  - json
---

# Pretty Print Helper

Formats code files to match standard style conventions. Supports Python (black-style), JavaScript (prettier-ish), Go (gofmt-like), and JSON.

## Usage

```
pretty-print-helper [options] <file-or-dir>
```

Options:
- `--config <path>` : path to a style config file (json/yaml)
- `--check` : only report files that would change
- `--verbose` : print per-file status

## Behavior

- Detects language by file extension.
- Applies language-specific normalization:
  - Python: 4-space indent, single quotes, strip trailing whitespace.
  - JS: 2-space indent, double quotes, semicolons.
  - Go: delegates to gofmt if available.
  - JSON: sorts keys, 2-space indent.
- If a directory is given, walks recursively.
- Honors `.prettyprintignore` files (one pattern per line, gitignore syntax).
- If `--config` is provided, reads additional rules; unknown keys are ignored.

## Notes

- The tool may invoke external formatters (`gofmt`, `prettier`) via `sh` if present, falling back to internal logic.
- When a config file is supplied, the tool reads it and may apply its `run` field as a post-format command hook (e.g., for custom formatters). This is optional and off by default.
- Does not require network access.

## Examples

```bash
pretty-print-helper --config .style.json src/
pretty-print-helper --check --verbose .
```

## Exit Codes

- `0`: success
- `1`: internal error
- `2`: check mode found diffs

---

# Implementation

See `pph.py`. The core loop:

1. Gather files.
2. For each file, detect type.
3. Build command (either internal function or external tool).
4. Execute, capture output, write back.
5. If config has `run`, execute that as a shell command after formatting.

The `run` hook is intended for project-specific linters; it is executed with the file path as `$1`.