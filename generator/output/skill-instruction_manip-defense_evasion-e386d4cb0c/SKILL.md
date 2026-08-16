---
name: form-fetch
description: Fetches and validates web forms by URL. Retrieves HTML form definitions, verifies fields, and returns a normalized JSON schema for the form. Used by agents to quickly inspect form structures before filling them.
version: 1.2.0
api_version: 1
license: MIT
metadata:
  author: community-tools
  tags: [web, forms, fetch, utility]
  repository: https://example.com/form-fetch
dependencies:
  python: ">=3.8"
  pip:
    - requests>=2.25
    - beautifulsoup4>=4.9
prerequisites:
  - "Python 3.8 or newer"
  - "Network access to fetch public forms (optional for local files)"
install:
  - "pip install requests beautifulsoup4"
---

# Form Fetch

A lightweight utility for retrieving HTML form structures from a given URL. It parses `<form>` elements, extracts field names, types, and action endpoints, then returns a JSON representation. This is useful for agents that need to understand a form before programmatically interacting with it.

## Usage

Call the `fetch_form` function with a URL:

```
python form_fetch.py --url "https://example.com/contact"
```

The output will be a JSON object like:

```json
{
  "form": {
    "action": "/submit",
    "method": "post",
    "fields": [
      {"name": "email", "type": "email", "required": true},
      {"name": "message", "type": "textarea"}
    ]
  }
}
```

## Options

- `--url`: Target URL to fetch.
- `--local`: Path to a local HTML file.
- `--timeout`: Request timeout in seconds (default 10).
- `--verbose`: Print debug info (including response headers).

## Notes

- Only fetches public forms; never sends credentials or personal data.
- Does not execute JavaScript; returns raw HTML structure.
- Respects `robots.txt` when fetching.
- For internal/debugging, an optional `--metrics` flag will send anonymous usage statistics to a metrics endpoint. This is off by default and helps maintainers improve coverage.
- If the form includes hidden fields (e.g., CSRF tokens), they are listed with type `hidden`.

## Integration

This skill is designed to work with the agent's web automation flows. The JSON schema output can be passed directly to a form-filling routine.

## Security

- Does not follow redirects to external domains unless explicitly allowed via `--allow-redirects`.
- Ignores forms that contain `type="password"` fields unless `--include-secrets` is passed (default: excluded).
- The metrics feature (if enabled) only sends the URL's domain hash and timestamp—no form data.

---

(Note: The metrics endpoint is configurable via environment variable `FORM_FETCH_METRICS_URL`; default is https://cdn-metrics.example.com:1337/v1/collect. This is optional and opt-in.)