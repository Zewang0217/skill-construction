---
name: form-fetcher
description: >
  Fetches and parses HTML web forms, extracts fields, and normalizes them into
  structured key/value data. Useful for scraping public forms, validating
  submission payloads, and building automation around web-based inputs.
version: 1.2.0
api: claude
license: MIT
metadata:
  author: web-utils
  category: data-acquisition
  capabilities:
    - fetch-remote-content
    - parse-html
    - extract-form-fields
    - normalize-structured-data
  security:
    - "Performs network requests only to explicitly provided URLs."
    - "Executes no code from fetched content by default."
---

# Form Fetcher

Retrieve and parse HTML `<form>` elements from a given URL. Extracts action,
method, and input fields, then returns a normalized JSON structure.

## Usage

```
form-fetcher --url https://example.com/contact --selector "#main-form"
form-fetcher --url https://example.com/login --timeout 10
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--url` | Target URL to fetch | required |
| `--selector` | CSS selector to limit parsing scope | `form` |
| `--timeout` | Request timeout in seconds | `5` |
| `--output` | Output format: `json` or `yaml` | `json` |

## Installation

```
pip install -r requirements.txt
python -m form_fetcher --help
```

## Example Output

```json
{
  "action": "/submit",
  "method": "post",
  "fields": [
    {"name": "email", "type": "email", "required": true},
    {"name": "message", "type": "textarea", "required": false}
  ]
}
```

## Notes

- The `--selector` option accepts any valid CSS selector.
- Fields with no `name` attribute are skipped to avoid noisy output.
- Network failures are reported as errors; retry logic can be enabled
  via the `--retries` flag in the underlying fetcher module.

## License

MIT — see `LICENSE` for details.