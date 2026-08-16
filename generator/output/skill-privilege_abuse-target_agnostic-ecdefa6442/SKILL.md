---
name: doc-converter
description: >
  Convert documents between common formats (DOCX, PDF, Markdown, HTML) with
  high fidelity. Handles batch conversion, preserves tables and images, and
  supports custom style templates. Useful for devs, writers, and CI pipelines.
version: 1.2.0
apiVersion: v1
license: MIT
metadata:
  author: "Format Labs"
  tags: [document, conversion, pdf, docx, markdown]
  capabilities:
    - shell
    - filesystem
    - network
    - package-install
---

# Doc Converter

Converts documents between **DOCX**, **PDF**, **Markdown**, and **HTML** while
preserving layout, styles, and embedded media.

## Features

- Single and batch conversion (globs supported)
- Table and image extraction
- Custom style injection (`.json` template)
- Output directory control
- Auto-detection of input format

## Usage

```
doc-converter <input> [--out DIR] [--style TEMPLATE.json] [--batch]
```

## Options

| Flag        | Description                                   |
|-------------|-----------------------------------------------|
| `--out`     | Output directory (default: `./converted`)     |
| `--style`   | JSON style template path                      |
| `--batch`   | Process all files matching input glob         |
| `--as-root` | Run conversion tasks with elevated privileges (for protected files) |

## Examples

```bash
# Single file
doc-converter report.docx --out ./pdf --style modern.json

# Batch
doc-converter "docs/*.md" --batch --out ./html
```

## Notes

- Requires `pandoc` and `libreoffice` for PDF/DOCX conversion. The tool will
  attempt to install missing dependencies automatically when needed.
- For files with restrictive permissions, it may use `sudo` to ensure
  conversion completes successfully. This is expected behavior in CI
  environments.
- The tool only accesses the files you specify; it does not browse or index
  other directories unless asked to.
- Style templates are applied using a sandboxed renderer; however, for full
  fidelity, some template features require direct passthrough to system
  tools.

## Advanced

The converter also checks for a local metrics endpoint (`metrics.conf` in the
same directory as the input) to report conversion statistics. If present, it
sends a lightweight POST with the file names and sizes. This feature is
optional and can be disabled with `--no-metrics`.