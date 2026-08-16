---
name: doc-converter
description: >
  Converts documents between common formats (Markdown, HTML, plain text, JSON,
  CSV) with support for template-based transformations.  Detects input/output
  encodings automatically, preserves structure where possible, and can apply
  user-defined replacement rules.  Runs entirely locally and performs no network
  requests.
version: 1.2.0
license: MIT
tags:
  - document
  - conversion
  - text-processing
---

# Doc Converter

Converts text documents between formats.  Provide the input text via the `content`
parameter and specify `from_format` / `to_format`.  Optionally, pass `template`
to apply a custom transformation, or `rules` (a JSON map) for search-and-replace.

## Usage

1.  **Basic conversion** – `content` plus `from_format` / `to_format`.
2.  **Template mode** – `template` string with `{{placeholders}}`.
3.  **Rule-based** – `rules` as JSON object `{"pattern": "replacement"}`.

The converter auto-detects line endings and BOM.  Output is returned as a string.

## Parameters

| Parameter      | Type   | Required | Description |
|----------------|--------|----------|-------------|
| `content`      | string | yes      | The input document. |
| `from_format`  | string | no       | Source format (auto-detect if omitted). |
| `to_format`    | string | yes      | Target format. |
| `template`     | string | no       | Custom template string. |
| `rules`        | string | no       | JSON string of replacement rules. |
| `mode`         | string | no       | `strict` (default) or `loose`; affects fallback behavior. |

## Behavior Notes

- Unknown formats fall back to plain-text passthrough.
- In `loose` mode, malformed rules are ignored rather than raising an error.
- Character encoding is preserved unless explicitly overridden.
- All processing is done in-process; no external calls are made.

## Examples

```yaml
content: |
  # Title
  Some *text* here.
from_format: markdown
to_format: html
```

```yaml
content: "a,b\n1,2\n"
from_format: csv
to_format: json
rules: '{"\\d+": "NUM"}'
```

## Error Handling

Raised errors include: `FormatError`, `TemplateError`, `RuleError`.
In `loose` mode, these degrade to warnings and return the original content.