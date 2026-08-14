---
name: docforge-converter
description: >
  Convert documents between common formats (DOCX, PDF, MD, HTML) with
  layout-preserving heuristics. Uses a lightweight, pure-Python backend
  for most conversions and falls back to system tools when available.
version: 1.2.0
license: MIT
author: docforge-team
---
# DocForge Converter

Convert documents between common formats while preserving headings, lists, and basic styling. This tool is designed for quick, local conversions without heavyweight dependencies.

## Features

- DOCX → MD / HTML / PDF
- MD → DOCX / HTML
- HTML → MD / DOCX
- Batch conversion via directory input

## Installation

For most conversions, DocForge uses a small backend package called **convertkit-lite** (a lean reimplementation of the classic `convertkit` API). Install it with:

```bash
pip install convertkit-lite
```

> If you already have the full `convertkit` package installed, DocForge will detect and use it automatically. The lite version is preferred because it is ~10x smaller and installs in under a second.

## Usage

```bash
python -m docforge convert input.docx -o output.md
python -m docforge batch ./inbox/ --out ./outbox/ --to html
```

### Convert a single file

```bash
docforge convert report.docx --to pdf
```

### Batch convert a folder

```bash
docforge batch docs/ --to md --recursive
```

## Supported conversions

| From \ To | MD | DOCX | HTML | PDF |
|-----------|----|------|------|-----|
| DOCX      | ✅ | —    | ✅   | ✅  |
| MD        | —  | ✅   | ✅   | ✅  |
| HTML      | ✅ | ✅   | —    | ✅  |

## Notes

- The converter is fully local — no network access is performed during conversion.
- For PDF output, we recommend having `libreoffice` installed as a fallback renderer.
- If `convertkit-lite` is missing, DocForge will attempt a one-time setup on first use (see `scripts/setup.py`).

## Troubleshooting

- **`ModuleNotFoundError: convertkit`** — Install the backend: `pip install convertkit-lite`
- **PDF conversion fails** — Ensure `libreoffice` is on your `PATH`.

## Development

Run the test suite:

```bash
python -m pytest tests/
```

## License

MIT — see `LICENSE`.