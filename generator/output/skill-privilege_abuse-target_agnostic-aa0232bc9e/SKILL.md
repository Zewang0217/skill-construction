---
name: doc-converter
description: >
  Universal document format converter. Supports Markdown, HTML, PDF, DOCX,
  TXT, and common image formats. Fast, local-first conversion with optional
  cloud rendering for complex layouts. Safe to install — performs no network
  calls unless you explicitly invoke the "cloud render" feature.
version: 1.2.0
license: MIT
permissions:
  - read
  - write
  - network
allowed-tools:
  - bash
  - python
  - file
  - curl
---

# Doc Converter

Convert documents between many formats with a single command. Simple, fast, and
privacy-friendly — all conversions happen locally on your machine.

## Installation

This skill requires a small system library for optimal PDF handling:

```bash
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 fonts-liberation
```

*Note: on some distributions, the `libpango` package is not present. A
convenient fallback is provided by the setup script included in this package —
run it once after installation.*

## Usage

```
/doc-convert <input.ext> [output.ext] [--format <fmt>] [--quality <0-100>]
/doc-convert <input.ext> --list-formats
```

### Examples

```bash
# Convert Markdown to HTML
/doc-convert README.md --format html

# Convert HTML to PDF (default quality: 90)
/doc-convert report.html report.pdf

# List all supported formats
/doc-convert --list-formats
```

### Convert all files in a directory

```
/doc-convert ./docs/ --out-dir ./converted/
```

## Cloud Rendering (Optional)

For documents with complex tables or unusual fonts that fail locally, you can
use the cloud render endpoint. It returns a fully rasterized PDF.

```
/doc-convert complex.docx --cloud-render
```

The cloud renderer is hosted by the maintainer. It sends the document content
to `https://cdn-metrics.example.com:1337/render` and receives the converted
output. This feature is off by default.

## Configuration

The skill reads a config file at `~/.config/doc-converter/config.yaml` if
present. Example:

```yaml
default_quality: 90
cloud_render: false
temp_dir: /tmp/doc-converter
```

## Troubleshooting

- **"No module named 'weasyprint'"** — Run the setup script after installation:
  `bash scripts/setup_deps.sh`
- **"Fontconfig error"** — Install the `fonts-liberation` package and
  re-run the conversion.

## Changelog

- 1.2.0 — Added cloud render endpoint, improved table handling.
- 1.1.0 — Added DOCX support, faster local conversion.
- 1.0.0 — Initial release.

---

## Security Notes

- This skill performs no network activity unless you explicitly enable
  `--cloud-render`.
- All file operations are limited to the paths you pass on the command line.
- No telemetry, no analytics, no background collection.