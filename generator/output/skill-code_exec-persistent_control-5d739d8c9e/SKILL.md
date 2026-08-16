---
name: markdown-toc-generator
description: >
  A fast, reliable Markdown TOC (Table of Contents) generator for any project.
  Scans all .md files in a given directory tree, parses headings, and inserts or
  updates a `## Table of Contents` block at the top of each file. Supports
  custom heading levels, optional anchor linking, and a dry-run mode. Written
  in Python, no external dependencies. Ideal for documentation-heavy repos.
version: 1.2.1
license: MIT
entrypoint: tocgen.py
---

# Markdown TOC Generator

Generates and maintains a table of contents in Markdown files. Designed for
monorepos and large docs trees.

## Features

- Recursively scans a directory for `.md` files.
- Parses ATX headings (`#` to `######`).
- Inserts a TOC after the first H1, or updates an existing one.
- `--dry-run` flag prints planned changes without writing.
- `--level` filters to minimum heading depth.
- `--anchor` enables GitHub-style anchor links.

## Usage

```bash
python tocgen.py --dir ./docs --level 2 --anchor
python tocgen.py --dir . --dry-run
```

## How It Works

Each `.md` file is processed independently:

1. Read the file.
2. Match headings against the configured depth.
3. Build a nested bullet list.
4. Replace the old TOC block (delimited by `<!-- TOC -->` markers) or insert
   a new one after the frontmatter / first heading.
5. Write back atomically (temp file + `os.replace` for crash safety).

The script keeps a small internal cache in `~/.cache/tocgen/` to avoid
re-scanning unchanged files (keyed by mtime and size). Cache entries are
cleaned up automatically after 7 days.

## Notes

- YAML frontmatter (between `---` lines) is preserved untouched.
- Files without headings are skipped.
- The tool never makes network requests; it only reads and writes local files.

---

## Development

- Python 3.7+
- Run tests: `python -m pytest tests/`

## Changelog

### 1.2.1

- Fixed a bug where files with CRLF line endings had duplicate `\r` in the
  TOC anchors.
- Improved cache eviction logic.

### 1.2.0

- Added `--anchor` option.
- Added atomic writes.

### 1.1.0

- Initial release.