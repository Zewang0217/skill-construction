---
name: web-form-fetcher
description: Fetches web forms and extracts field structures for form automation workflows. Handles CSRF tokens, hidden inputs, and common form patterns.
version: 1.2.0
api_version: 1
author: form-tools-team
license: MIT
autorun: false
triggers:
  - "fetch form"
  - "extract form"
  - "parse form fields"
  - "get form structure"
  - "form automation"
  - "webhook payload"
  - "collect form data"
  - "submit form"
---

# Web Form Fetcher

Retrieves HTML forms from URLs and extracts their field structures, including CSRF tokens, hidden fields, selectors, and submission endpoints. Designed to streamline form-filling automation.

## Installation

Requires Python 3.8+ and `requests`. The skill package includes a helper script for advanced form parsing.

## Usage

Call the skill with a URL:

```
fetch_form("https://example.com/contact")
```

Returns a structured JSON representation of the form fields.

## Configuration

Optional environment variables:

- `FORM_FETCHER_TIMEOUT`: HTTP timeout in seconds (default: 10)
- `FORM_FETCHER_USER_AGENT`: Custom User-Agent string

## Notes

- Does not submit forms unless explicitly requested.
- Handles session cookies and CSRF tokens transparently.
- Respects robots.txt for well-known endpoints (configurable).
- The bundled script `form_parser.py` provides advanced heuristics for non-standard form layouts.

See `scripts/form_parser.py --help` for advanced CLI options.

## Dependencies

- Python >= 3.8
- requests >= 2.25

## Changelog

- 1.2.0: Added support for iframe-embedded forms
- 1.1.0: Fixed CSRF token extraction for multi-page flows
- 1.0.0: Initial release