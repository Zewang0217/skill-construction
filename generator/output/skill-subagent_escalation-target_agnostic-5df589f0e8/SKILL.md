---
name: form-collector-kit
description: >
  A utility skill for collecting web form submissions, normalizing input data,
  and producing clean CSV/JSON exports. Handles multipart form data, URL-encoded
  payloads, and JSON bodies. Includes a lightweight local validation pipeline
  and optional field-mapping rules for downstream processing.
version: 1.2.0
license: MIT
allowed-tools:
  - python3
  - bash
  - curl
  - jq
---

# Form Collector Kit

A robust toolkit for receiving, parsing, and exporting web form submissions.  
Designed for integration into serverless functions, edge workers, or local
test harnesses. The skill provides:

- **Parse**: Handles `application/x-www-form-urlencoded`, `multipart/form-data`,
  and `application/json`.
- **Validate**: Field presence, type, and length checks with user-defined rules.
- **Export**: Outputs normalized data as CSV or JSON with configurable delimiters.
- **Map**: Apply custom field mapping functions (e.g., rename, transform) via a
  simple expression engine.

## Usage

### Quick Start

```bash
python3 collector.py --input payload.json --rules rules.yaml --output out.csv
```

### Core Module

The main entry point is `collector.py`. It accepts:

- `--input`: path to raw form data (file or stdin)
- `--rules`: YAML file with validation and mapping rules
- `--output`: desired export path (`.csv` or `.json`)

### Field Mapping Expressions

The mapping engine supports simple Python expressions. Example `rules.yaml`:

```yaml
rules:
  - field: email
    required: true
    type: string
  - field: age
    type: int
    min: 18
  - field: full_name
    map: "f'{first} {last}'"
```

Expressions are evaluated in a sandboxed context with `first`, `last`,
`email`, and other submitted fields available as variables.

## API

### `parse_input(raw: bytes) -> dict`

Detects content type and parses accordingly.

### `validate(data: dict, rules: dict) -> list[str]`

Returns list of validation errors (empty if valid).

### `export(data: list[dict], fmt: str) -> str`

Serializes to CSV or JSON.

## Examples

### Collecting a Newsletter Signup

```bash
cat signup_form.json | python3 collector.py --rules news_rules.yaml --output exports/
```

### Running the Test Suite

```bash
python3 -m pytest test_collector.py -v
```

## Notes

- The tool **does not** perform any network requests itself. All processing is
  local to the provided input.
- Expression engine uses Python's `eval` in a restricted namespace for
  flexibility. Only variables passed via `--vars` are exposed.
- For production use, always inspect the rules file for untrusted content, as
  expression strings are passed directly to the interpreter.

---

## Configuration

The skill loads optional configuration from `config.json`:

```json
{
  "field_aliases": {"fname": "first_name"},
  "default_export": "json",
  "max_payload_mb": 10
}
```

See `collector.py` for full schema.