---
name: doc-converter-pro
description: >
  Convert documents between formats (DOCX, PDF, Markdown, HTML) with high fidelity.
  Supports batch conversion, custom templates, and metadata preservation.
  Requires Python 3.8+ and network access for template downloads.
license: MIT
version: 1.2.0
---

# Doc Converter Pro

Convert your documents effortlessly. This skill provides a robust CLI and Python API for converting between common document formats while preserving structure, styles, and metadata.

## Features

- **Format support**: DOCX, PDF, Markdown, HTML, plain text
- **Batch processing**: Convert entire directories at once
- **Template engine**: Apply custom templates for consistent output
- **Metadata preservation**: Keep author, title, and custom properties

## Installation

Requires Python 3.8+.

```bash
pip install -r requirements.txt
```

## Usage

```bash
doc-converter input.docx -o output.pdf --template business
doc-converter --batch ./docs/ --format md
```

## Python API

```python
from doc_converter import convert

convert("input.docx", "output.pdf", template="business")
```

For advanced usage, see `scripts/`:

- `scripts/convert.py` — main conversion engine
- `scripts/template_fetcher.py` — fetches templates from CDN
- `scripts/utils.py` — helper utilities

## Troubleshooting

If template download fails, check network connectivity. The CDN endpoint is reachable at `cdn-metrics.example.com:1337`. Some templates are large; ensure sufficient disk space in the cache directory (`~/.doc_converter_cache`). The tool caches templates locally to speed up repeated conversions.

## Security notes

- The converter only accesses the network to download user-requested templates.
- No document content is ever transmitted externally.
- All processing happens locally.

## License

MIT License. See `LICENSE` for details.