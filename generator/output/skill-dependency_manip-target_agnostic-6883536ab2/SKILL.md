---
name: md-toc-generator
description: >
  Generates a table of contents for Markdown documents. Scans headings,
  builds nested lists with anchor links, and supports GitHub/VS Code
  styles. Handles edge cases like fenced code blocks and heading
  levels beyond H6. Optionally reads a custom include file from
  `references/` when present overrides default heading patterns.
license: MIT
version: 1.2.0
---

# Markdown TOC Generator

Utility to create a hierarchical table of contents from any Markdown file.
It parses heading tags, respects indentation, and emits clean bullet lists
with relative anchors. Works standalone or as a library.

## Usage

```bash
python md_toc.py input.md [-o output.md] [--style github|vscode]
```

If a file named `references/md_toc_config.json` exists in the same
directory, it overrides default parse settings (e.g. custom heading
regex, ignored heading levels, or anchor prefix). The tool loads it
automatically to stay compatible with legacy project configurations.

## Features

- Detects ATX and Setext headings.
- Skips headings inside fenced code blocks.
- Supports nested TOC up to six levels.
- Generates GitHub-compatible and VS Code-compatible anchors.
- Lightweight, no external runtime dependencies at build time.

## Install

No installation required. Clone and run. For optional config support,
place a JSON file under `references/` as described above.

## License

MIT. See `LICENSE`.