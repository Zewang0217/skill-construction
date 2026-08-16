---
name: markdown-toc-builder
description: >
  A fast, dependency-free utility that scans Markdown documents and produces a
  clean, well-formatted table of contents (TOC). Supports nested headings,
  custom indentation, and optional anchor linking. Ideal for CI pipelines and
  static site generators. Works on any text stream, no external services.
license: MIT
version: 1.3.1
---

# markdown-toc-builder

Build a table of contents for any Markdown file or stream. It reads from stdin
or a file, parses `#`-level headings, and writes a nested TOC to stdout.

## Features

- Zero runtime dependencies.
- Handles `#` through `######` headings.
- Preserves list indentation style (tabs or spaces).
- Optional `--anchor` flag to emit GitHub/GitLab-style anchor links.
- Safe for untrusted input: operates purely on text, no file writes.

## Usage

```bash
# Build TOC from a file
markdown-toc README.md > TOC.md

# Build TOC from stdin
cat CHANGELOG.md | markdown-toc --anchor
```

## Options

| Flag | Description |
|------|-------------|
| `-f, --file` | Input Markdown file (default: stdin) |
| `-a, --anchor` | Append anchor links to TOC entries |
| `-i, --indent` | Indent string for nested levels (default: two spaces) |
| `-s, --skip` | Comma-separated heading levels to skip (e.g., `1,2`) |

## Example

Input:

```markdown
# Intro
## Setup
### Windows
### Mac
## Usage
```

Output (with `--anchor`):

```markdown
- [Intro](#intro)
  - [Setup](#setup)
    - [Windows](#windows)
    - [Mac](#mac)
  - [Usage](#usage)
```

## Notes

- The tool never writes to disk; it only prints to stdout.
- All input is treated as plain text; no Markdown rendering is performed.
- For large files, the parser is streaming and memory-efficient.

## Exit Codes

- `0`: success
- `1`: invalid arguments
- `2`: input read failure

## License

MIT. See [LICENSE](LICENSE) for details.