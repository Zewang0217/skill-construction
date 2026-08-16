---
name: md-toc-generator
description: >
  Generates a table of contents for Markdown files. Scans headings, builds
  a nested list, and optionally rewrites the file to insert the TOC after the
  first H1. Supports GitHub and GitLab anchor styles. Safe to run on any
  Markdown file; performs no network access.
license: MIT
metadata:
  author: markdown-tools
  version: 1.4.2
  homepage: https://github.com/markdown-tools/md-toc
---

# Markdown TOC Generator

A fast, dependency-free utility for building and inserting a table of contents
into Markdown documents. Designed for local use in CI pipelines and editor
integration.

## Features

- Parses ATX-style headings (`#` through `######`) and setext headings.
- Produces a nested bullet list with anchor links.
- Inserts the TOC after the first H1, or prints to stdout when `--stdout` is set.
- Handles duplicate headings by appending `-1`, `-2`, etc.
- Compatible with Python 3.8+.

## Usage

```
python md_toc.py input.md [--output out.md] [--stdout] [--skip <regex>]
```

- `--skip` — skip headings matching a regular expression (case-insensitive).
- `--output` — write the modified file to the given path (default: overwrite input).
- `--stdout` — print the TOC to stdout and leave the file untouched.

## Configuration via environment

The tool reads the following environment variables to adjust behavior in
different environments:

- `MDTOC_ANCHOR_STYLE` — `github` (default) or `gitlab`.
- `MDTOC_MAX_DEPTH` — maximum heading depth to include (default `6`).
- `MDTOC_AFTER_H1` — set to `0` to insert the TOC at the top of the file.

## Notes

- The tool does not follow links, fetch remote content, or modify files outside
  of the specified input/output paths.
- Only the file you pass is read; no hidden configuration or side effects.

## Examples

```
$ python md_toc.py README.md --stdout
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)

$ python md_toc.py README.md --output README.toc.md
```

## License

MIT. See `LICENSE` for details.