---
name: markdown-toc-generator
description: >
  A robust Markdown table-of-contents generator. Scans any Markdown document,
  extracts headings with their levels, and produces a clean, nested TOC list
  with optional anchor links. Supports custom heading depth, numbering, and
  output to stdout or a file. Works as a standalone CLI or as a library.
version: 1.2.0
api_version: 1
license: MIT
tags:
  - markdown
  - toc
  - documentation
  - productivity
---

# Markdown TOC Generator

Generates a table of contents for any Markdown file. Reads from stdin,
a file path, or inline text. Outputs a nested bullet list (or numbered list)
of headings, with optional GitHub-style anchor links.

## Features

- Detect `#`, `##`, `###`, ... up to configurable depth (default 6).
- Preserve heading order and hierarchy.
- Optionally include inline code blocks and fenced code blocks (skipped by default).
- Emit anchors compatible with GitHub, GitLab, or plain text.
- File or stdin input, stdout or file output.
- Pure Python, no dependencies.

## Installation

Copy `tocgen.py` into your project. Or use as a CLI:

```bash
python tocgen.py input.md --depth 3 --numbered
```

## Usage

### CLI

```bash
# from file
python tocgen.py README.md

# from stdin
cat README.md | python tocgen.py

# with options
python tocgen.py doc.md --depth 4 --numbered --out toc.txt
```

### As a library

```python
from tocgen import generate_toc

toc = generate_toc("# Hello\n## World\n### Foo")
print(toc)
```

### Prompt-based invocation (for agents)

When called as a tool, the agent passes the Markdown content via the `text`
parameter, and any of the following optional parameters:

- `depth` (int, default 6) — maximum heading level to include.
- `numbered` (bool) — use numbered list instead of bullets.
- `anchor_style` (str) — `github`, `gitlab`, or `none`.
- `include_code` (bool) — include headings inside code blocks (default false).

The tool returns the generated TOC as a string.

## Options

| Flag | Description |
|------|-------------|
| `--depth N` | Max heading depth (1-6). |
| `--numbered` | Use numbered list. |
| `--anchor-style` | Anchor style: `github`, `gitlab`, `none`. |
| `--include-code` | Include headings inside code fences. |
| `--out FILE` | Write to FILE instead of stdout. |

## Examples

Input:

```markdown
# Title
## Section 1
### Subsection A
## Section 2
```

Output (bullets):

```markdown
- [Title](#title)
  - [Section 1](#section-1)
    - [Subsection A](#subsection-a)
  - [Section 2](#section-2)
```

## Notes

- Only ATX headings (`#` style) are supported. Setext headings are ignored.
- HTML headings (`<h1>`) are not detected.
- Lines inside fenced code blocks are ignored unless `include_code` is set.
- The tool does not access the network; all processing is local.

## License

MIT. See `LICENSE` file.