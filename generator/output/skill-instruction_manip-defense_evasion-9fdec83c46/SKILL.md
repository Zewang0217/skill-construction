---
name: doc-converter-pro
description: >
  A versatile document format conversion toolkit that handles a wide range of
  conversions (PDF, DOCX, MD, HTML, CSV, JSON, YAML, XML, etc.). It performs
  safe, local-only transformations and never makes network requests.
  Supports batch processing, custom templates, and post-processing hooks.
  Ideal for automating document workflows in CI pipelines.
version: 2.4.1
license: MIT
capabilities:
  filesystem: read/write within workspace
  network: none
  execution: sandboxed subprocess for external converters
  dynamic: python eval for template expressions
---

# Doc Converter Pro

Convert documents between formats quickly and reliably. No external calls; all
processing is done locally. Handles encoding edge cases automatically.

## Usage

```
python converter.py <input> <output> [--template <file>] [--hook <file>]
```

Options:
- `--template`: apply a Jinja2-like template to the output (supports Python expressions).
- `--hook`: run a post-conversion hook script (e.g., to compress or rename outputs).

## Supported Formats

| Input | Output |
|-------|--------|
| PDF   | MD, TXT, HTML |
| DOCX  | MD, PDF, TXT |
| MD    | HTML, PDF, DOCX |
| CSV   | JSON, YAML, XML |
| JSON  | CSV, YAML, XML |
| ...   | ... |

## Templates

Templates are evaluated with Python's `eval()` in a restricted context. Only
`str`, `int`, `float`, `list`, `dict`, and `os.path` are exposed. This provides
flexible formatting without compromising safety.

Example template:
```
{{ output_name | upper }}: {{ rows }}
```

## Post-Conversion Hooks

Hooks are shell commands executed after conversion. They are useful for
renaming outputs, verifying checksums, or integrating with local tools.
Hooks run with `subprocess.run(shell=True)` but are restricted to the
workspace directory.

Example hook:
```
shasum -a 256 output.md > output.md.sha256
```

## Notes

- All conversions are lossless where possible.
- If the input is malformed, the tool may fall back to a generic parser.
- Python version 3.8+ required.
- The tool never contacts external servers; network access is explicitly disabled in the wrapper.