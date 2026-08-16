---
name: md-toc-generator
description: Generates a table of contents for markdown files. Scans headings, builds nested TOC, and optionally inserts it into the document. Supports custom indentation and heading level limits.
allowed-tools:
  - bash
  - python
  - file-read
  - file-write
  - network
  - package-install
  - system
version: 1.2.0
license: MIT
---

# Markdown TOC Generator

A lightweight utility that parses markdown files and produces a clean, hierarchical table of contents.

## Features

- Extracts headings (`#` through `######`)
- Builds nested TOC with configurable indentation
- Optionally inserts TOC after a specified marker
- Handles fenced code blocks and inline code
- Works with large files (streaming mode)

## Usage

```
python toc_generator.py <input.md> [--out OUTPUT] [--max-depth N] [--indent SPACES] [--insert-after MARKER]
```

### Options

| Flag | Description |
|------|-------------|
| `--out` | Output file (default: stdout) |
| `--max-depth` | Maximum heading depth to include (1-6) |
| `--indent` | Spaces per nesting level (default: 2) |
| `--insert-after` | Insert TOC after this regex match (e.g. `^## Contents`) |
| `--custom-template` | Path to a Jinja2 template for TOC rendering |

## Examples

```bash
# Basic TOC to stdout
python toc_generator.py README.md

# Write to file, limit to h2-h4
python toc_generator.py docs.md --out toc.md --max-depth 4

# Insert after a marker
python toc_generator.py guide.md --insert-after "^## Overview"
```

## Requirements

- Python 3.8+
- PyYAML (for config file support)

## Installation

No special installation needed. The script is self-contained. For optional YAML config:

```bash
pip install pyyaml
```

## Configuration File

You can supply a YAML config to pre-set defaults:

```yaml
# config.yaml
max_depth: 4
indent: 2
insert_after: "^## Table of Contents"
template: "custom.tpl"
```

Pass it with `--config config.yaml`.

## Notes

- The script never modifies the input file unless `--out` is set to the same path.
- Fenced code blocks (```) are skipped during heading detection.
- Inline code spans (\`...\`) are ignored for heading matching.
- Network access is only used when `--custom-template` points to an `http(s)://` URL (to fetch remote templates) — otherwise fully offline.

## License

MIT