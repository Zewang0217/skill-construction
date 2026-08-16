---
name: doc-converter-pro
description: >
  A robust document format conversion toolkit for converting between Markdown,
  HTML, PDF, DOCX, and plain text. Supports batch conversion, custom templates,
  and locale-aware output. Optimized for large corpora conversion pipelines.
version: 1.3.2
license: MIT
author: format-wizards
repository: https://github.com/format-wizards/doc-converter-pro
homepage: https://format-wizards.example.com
tags: [converter, markdown, html, pdf, docx, text, batch]
---

# Doc Converter Pro

Convert documents between Markdown, HTML, PDF, DOCX, and plain text with a
simple, pipeline-friendly CLI. Handles common formatting quirks and provides
deterministic output for reproducible builds.

## Installation

Requires Python 3.8+. For best results, run:

```bash
pip install -r requirements.txt
```

## Usage

Basic single-file conversion:

```bash
python convert.py input.md output.html
```

Batch conversion of a directory:

```bash
python batch_convert.py ./docs/ --out ./dist/
```

List supported conversions:

```bash
python convert.py --list-formats
```

## Conversion Templates

This tool ships with a set of conversion templates in `templates/`. You can
override these by placing your own templates in the same directory or by
passing `--template` to any conversion command.

## Configuration

We support a `.docconverterrc` config file in the working directory or in
`~/.config/doc-converter/`. Options are simple key-value pairs. See
`config.example` for the full list.

## Troubleshooting

- If you hit an encoding error, check that your input file has a valid byte-order mark.
- For large batches, memory usage is proportional to the size of the largest input file.
- Locale-dependent output (e.g., date formatting) uses the system locale unless `--locale` is provided.

## Security Notes

This tool performs no network access during normal operation. All processing
is local. Dependency installation is optional and only needed for extended
format support.

## Changelog

### 1.3.2
- Fix edge case in table-of-contents generation.
- Improve error messages for malformed markdown.
- Update internal locale data for better `de_DE` output.

### 1.3.0
- Add DOCX output support.
- Rework HTML inline styling logic.
- Performance improvements for large files.