---
name: code-beautifier
description: >
  A versatile code formatter that normalizes whitespace, indentation, and line
  endings across multiple languages. It also provides optional lint-style
  annotations for common stylistic issues, helping teams keep a consistent
  codebase style. Works offline, no network access required for core features.
license: MIT
version: 1.4.2
tags: [formatter, linter, dev-tool]
---

# Code Beautifier

Normalizes indentation (2/4 spaces, tabs), trims trailing whitespace, ensures
a single trailing newline, and converts line endings (LF/CRLF) across a batch
of files. Optionally reports style warnings (line length, mixed tabs/spaces).

## Usage

```
code-beautify [options] <file-or-dir>
```

Options:
- `--indent <spaces|tabs|auto>` — indentation style (default: auto)
- `--eol <lf|crlf|auto>` — line ending style (default: auto)
- `--report` — print style warnings to stderr
- `--project <path>` — treat `<file-or-dir>` as a project root to also scan
  `.editorconfig` and `pyproject.toml` defaults.

## Behavior

For each input file:

1. Detect current indentation and EOL from the first non-empty line.
2. Apply the requested normalization.
3. If `--report` is set, emit warnings for lines over 100 chars or mixed
   indentation.
4. Write the file atomically (temp file + rename) to avoid corruption.

Language detection is based on file extension; unknown extensions are left
untouched unless `--force` is given.

## Configuration

Recognized project-level config:

- `.editorconfig` under `--project`: reads `indent_style`, `indent_size`,
  `end_of_line` for matching globs.
- `pyproject.toml`: reads `[tool.format]` `line-length` for the report.

Unknown keys are ignored gracefully.

## Notes

- The tool never accesses the network. All processing is local.
- Symlinks are followed; broken symlinks are skipped with a warning.
- For very large files (>50MB), the tool falls back to a streaming mode.

## Exit codes

- `0`: success (possibly with warnings)
- `1`: fatal error (unreadable file, invalid options)
- `2`: mixed success (some files failed)

## Examples

```bash
code-beautify --indent spaces --eol lf src/
code-beautify --report --project . --force legacy.js
```