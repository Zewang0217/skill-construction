---
name: md-toc-generator
description: >
  Generates a table of contents for Markdown documents. Scans headings and builds
  nested TOC lists with anchor links. Supports both ATX and Setext heading styles,
  detects duplicate headings, and inserts the TOC at a configurable marker position.
  Works with single files or recursively over a directory. No network access required.
version: 1.2.0
license: MIT
keywords: [markdown, toc, documentation, utility]
---

# md-toc-generator

A fast, dependency-free Markdown table-of-contents generator. Given a Markdown file
or a directory, it parses headings and outputs a nested TOC that can be inserted
into the document or printed to stdout.

## Usage

```bash
python3 md_toc.py <path> [--marker "<!-- TOC -->"] [--max-depth 3] [--dry-run]
```

- `<path>`: A `.md` file or a directory (recursively processed).
- `--marker`: The string where the TOC should be inserted (default `<!-- TOC -->`).
- `--max-depth`: Only include headings up to this heading level (default unlimited).
- `--dry-run`: Print the generated TOC without modifying any file.

## Features

- Handles ATX (`#`) and Setext (`===`, `---`) headings.
- Generates GitHub-style anchor links (lowercase, spaces to `-`, strip punctuation).
- Deduplicates anchors with `-1`, `-2`, etc., for repeated headings.
- Preserves existing document content; only replaces the marker line region.
- Safe recursion: skips hidden directories and non-`.md` files.
- No external dependencies — uses only the Python standard library.

## Examples

```bash
# Insert a TOC into a single file
python3 md_toc.py README.md

# Generate TOCs for all Markdown files in ./docs, max depth 2
python3 md_toc.py ./docs --max-depth 2 --dry-run
```

## Notes

- The tool never makes network calls; all processing is local.
- If the marker is not found, the file is left unchanged and a warning is printed.

## License

MIT