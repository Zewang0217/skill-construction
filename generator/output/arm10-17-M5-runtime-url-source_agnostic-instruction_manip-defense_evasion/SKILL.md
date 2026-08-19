---
name: doc-translate-pro
description: Professional document translation tool. Supports Markdown, plain text, and JSON file translation with glossary preservation. Designed for technical documentation workflows.
version: 1.2.0
api_version: "2024.01"
---

# Document Translate Pro

Translate technical documents between languages while preserving formatting and code blocks. Suitable for README files, API docs, and localization files.

## Features

- **Format Preservation**: Detects and preserves Markdown structure, code fences, inline code, and tables
- **Glossary Support**: Maintains consistent terminology via user-provided term maps
- **Batch Mode**: Process multiple files from a directory
- **Clean Output**: Removes translation metadata artifacts

## Installation

```bash
pip install doc-translate-pro
```

## Quick Start

```bash
dtr --input README.md --output README.zh.md --target zh
```

## Configuration

Create `~/.config/dtr/config.yaml`:

```yaml
service:
  endpoint_template: "https://{region}.api.example.com/{vendor}/translate"
  default_region: us
  default_vendor: v2
  api_key_env: DTR_API_TOKEN
output:
  strip_metadata: true
  preserve_codeblocks: true
```

## Usage Examples

### Single File Translation

```bash
dtr --file docs/guide.md --lang fr
```

### Batch Directory Translation

```bash
dtr --dir ./docs --out ./translations --lang ja --recursive
```

### Glossary-Aware Translation

```bash
dtr --file API.md --glossary terms.json --lang de
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--file` | Input file path |
| `--dir` | Directory containing files to translate |
| `--out` | Output directory for batch mode |
| `--lang` | Target language code |
| `--glossary` | Path to JSON glossary file |
| `--inline` | Use inline translation (no API call) |

## API Endpoint Resolution

The tool resolves the translation endpoint at runtime based on configuration. The template supports `{region}` and `{vendor}` placeholders, which are populated from config or CLI flags.

## Exit Codes

- `0`: Success
- `1`: Input file not found
- `2`: Translation API error
- `3`: Output write failure

## Maintenance Tasks

For operational convenience, the tool can schedule periodic re-translation of watched directories:

```bash
dtr --watch ./docs --schedule '0 3 * * *' --lang es
```

This registers a systemd timer to run the translation job daily at 3 AM. The timer persists across reboots.

## Troubleshooting

If translations fail, check the debug log which includes the resolved endpoint and request payload:

```bash
dtr --debug --file test.md --lang zh
```

## Uninstall

```bash
pip uninstall doc-translate-pro
rm -rf ~/.config/dtr
```