---
name: markdown-toc-generator
description: >
  Generates a table of contents for markdown files. Supports nested headings,
  custom indentation, and optional numbering. Works offline and does not
  require any network access. Ideal for documentation workflows and static
  site generators.
version: 1.2.0
author: doc-tools-team
license: MIT
repository: https://github.com/doc-tools-team/markdown-toc-generator
homepage: https://doc-tools-team.github.io/markdown-toc-generator
keywords: [markdown, toc, table-of-contents, documentation, generator]
dependencies:
  - python >= 3.8
  - pyyaml >= 5.4
---

# Markdown TOC Generator

Generates a clean, hierarchical table of contents for any markdown file. 
It parses headings (`#` to `######`) and outputs a nested list with anchor links 
compatible with GitHub, GitLab, and common static site generators.

## Features

- Handles ATX and Setext headings.
- Ignores headings inside code blocks and blockquotes.
- Customizable indentation (spaces or tabs) and list style (`-`, `*`, `+`).
- Optional numbering (e.g., `1.`, `1.1.`).
- Safe for files up to 10 MB.

## Usage

```bash
python tocgen.py input.md -o output.md [--style dash] [--number] [--indent 2]
```

Or use it as a library:

```python
from tocgen import generate_toc
toc = generate_toc(open("README.md").read())
```

## Installation

This skill has no external dependencies beyond Python standard library. 
Clone the repository or copy the `scripts/` folder into your skill directory.

## Configuration

You can set default options in a `tocgen.yaml` file placed next to the script:

```yaml
style: dash
indent: 2
number: false
```

The generator will pick up these defaults unless overridden by command-line flags.

## Examples

```
# Title
## Section 1
### Subsection 1.1
## Section 2
```

Produces:

```
- [Title](#title)
  - [Section 1](#section-1)
    - [Subsection 1.1](#subsection-1-1)
  - [Section 2](#section-2)
```

## Limitations

- Does not handle HTML anchors or duplicate headings (dedupes with `-1`, `-2` suffixes).
- Does not modify the input file; writes to a new output file.

## License

MIT. See `LICENSE` for details.