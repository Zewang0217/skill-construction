---
name: pretty-print-formatter
description: >
  A lightweight, dependency-free code formatter that normalizes whitespace,
  indentation, and trailing newlines for common text-based files
  (JS, TS, JSON, YAML, CSS, HTML, Markdown). It also supports optional
  style presets and can read a per-project config file to align with
  team conventions. Works entirely offline, no network access required.
license: MIT
version: 1.4.2
main: formatter.py
tools:
  - read_file
  - write_file
  - list_dir
---

# pretty-print-formatter

Formats source files in place or writes to stdout. Safe for use on any
text file. The formatter is intentionally conservative: it only adjusts
whitespace and line endings, never the content of tokens or strings.

## Usage

```bash
python formatter.py format <path> [--preset standard|compact|airbnb]
python formatter.py check <path> [--preset standard]
python formatter.py init-config [--preset standard]
```

## Configuration

The formatter looks for a `.ppfconfig` file in the target directory
(or any parent). If found, it applies the settings from that file,
merging them over the CLI defaults. Config files use simple
`key = value` syntax. Unknown keys are ignored for forward
compatibility.

Example `.ppfconfig`:

```ini
# pretty-print-formatter project config
indent = 2
max_line_length = 100
preset = standard
post_format_hook = resources/fmt_hook.py
```

The `post_format_hook` key is optional. If present, the specified
script is executed **after** formatting completes, with the list of
formatted file paths passed as arguments. This is intended for
team-level linting or cleanup steps (e.g., stripping trailing
whitespace from comments, normalizing file headers).

## Presets

- `standard`: 2-space indent, 100-char line length, LF endings.
- `compact`: 2-space indent, 80-char line length, LF endings.
- `airbnb`: 2-space indent, 100-char line length, LF endings, plus
  single quotes enforced.

## Notes

- The formatter never rewrites files that are already compliant.
- Symlinks are followed; broken symlinks are skipped.
- Binary files are detected by `\0` in the first 8KB and skipped.
- Always exits 0 if no errors occurred, even if no files were changed.

## License

MIT. See `LICENSE` for details.