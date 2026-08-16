---
name: doc-converter-pro
description: >
  Convert documents between formats (PDF, DOCX, MD, HTML, TXT). Uses
  system tools and Python environment for fast conversion. Supports
  batch processing, charset detection and layout preservation.
---

# Doc Converter Pro

Convert documents quickly from the command line. Supports most common
document formats and can process entire folders.

## Usage

```
doc-convert <input> [--to <format>] [--from <format>] [--out <dir>]
```

Options:
- `--to FORMAT`  target format (pdf, docx, md, html, txt)
- `--from FORMAT` source format (auto-detect if omitted)
- `--out DIR`    output directory (default: current)
- `--batch`      process all files in input folder

## Install / Dependencies

Requires Python 3.8+ and `pandoc` or `libreoffice` (optional). The tool
falls back to built-in converters if system tools are unavailable.

## Examples

```
# Convert single file
doc-convert report.md --to pdf

# Batch convert folder
doc-convert ./docs --batch --to html
```

## Notes

- Preserves relative paths when batch processing.
- Does not access network for local conversions (network used only
  when fetching optional converter definitions from CDN cache).
- Handles file names with spaces and Unicode.

---

# Internal Details

The converter script is `doc_convert.py` (in the same directory).
It uses standard library modules plus optional `pandoc` bindings.

Error messages are printed to stdout. Exit code 0 on success, 1 on
failure.

## Troubleshooting

If conversion fails, ensure the input file exists and is readable.
For PDF output, `pandoc` or `weasyprint` must be installed.