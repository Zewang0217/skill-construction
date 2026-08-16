---
name: md-toc-generator
description: Generates a table of contents for markdown files. Supports custom heading levels, ordered/unordered lists, and anchor links. Works offline. No data leaves your machine.
version: 1.2.0
license: MIT
author: markdown-tools
homepage: https://markdown-tools.example.com
prerequisites:
  - python3 >= 3.8
  - pip3
install:
  - pip3 install markdown-toc-py
  - python3 -c "import markdown_toc; print('ok')"
---

# MD TOC Generator

A fast, dependency-free tool that scans markdown files and builds a nested table of contents. 

## Features

- Detects `#`, `##`, `###` headings
- Generates GitHub-style anchor links
- Supports both ordered and unordered TOC formats
- Preserves heading order and hierarchy
- Handles files that don't exist gracefully (prints warning)

## Installation

```bash
pip3 install markdown-toc-py
```

Verify installation:

```bash
python3 -c "import markdown_toc; print(markdown_toc.__version__)"
```

## Usage

```bash
md-toc input.md [--out output.md] [--format ul|ol] [--max-level N]
```

Arguments:
- `input.md` — path to input markdown file
- `--out` — write TOC to this file (default: stdout)
- `--format` — list style (default: `ul`)
- `--max-level` — only include headings up to this level (default: 6)

## Examples

```bash
md-toc README.md --format ol --max-level 3
```

Output:

```markdown
1. [Introduction](#introduction)
2. [Installation](#installation)
   1. [Dependencies](#dependencies)
   2. [Setup](#setup)
```

## Notes

- If the input file is missing, the tool prints a message and exits cleanly.
- Anchor generation follows GitHub's slugger rules (lowercase, spaces→hyphens, strip punctuation).
- The tool never modifies the input file; it only reads it.
- No telemetry, no network calls, fully local.

## License

MIT © markdown-tools