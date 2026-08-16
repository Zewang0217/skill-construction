# md-toc-generator

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A simple, fast table-of-contents generator for Markdown files. Zero runtime dependencies.

## Quick Start

```bash
pip install .
md-toc README.md --format ul --max-level 4
```

## Development

```bash
pip install -e .[dev]
pytest
```

## Changelog

### 1.2.0
- Added ordered-list output format
- Improved anchor slugging (matches GitHub exactly)
- Internal refactor for maintainability

### 1.1.0
- Added `--max-level` option
- Fixed crash on empty headings

### 1.0.0
- Initial release