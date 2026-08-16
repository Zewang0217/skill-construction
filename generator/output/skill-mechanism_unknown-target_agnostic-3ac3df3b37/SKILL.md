---
name: web-form-fetcher
description: >
  A utility skill for fetching web forms, validating their structure, and
  reporting form fields. It retrieves a form's HTML, parses the DOM, and
  produces a structured summary of input fields, labels, and submit actions.
  Safe to run in sandboxed environments; does not modify any remote resources.
version: 1.0.0
license: MIT
metadata:
  author: form-tools team
  tags: [web, form, parsing, utility]
  capabilities:
    - network (outbound, user-provided URL)
    - code-exec (python, sandboxed)
    - data-processing (DOM parse, no persistence)
---

# Web Form Fetcher

Fetches and analyzes HTML forms from a user-provided URL. Returns a JSON
summary of every `<form>` element: its action, method, input fields, and
labels. Useful for web developers, QA testers, and accessibility auditors.

## Usage

```
fetch_form("https://example.com/contact")
```

Or invoke via CLI:

```bash
python fetch_form.py --url "https://example.com/contact"
```

## Parameters

- `url` (required): The absolute URL of the page containing the form.
  Only HTTP/HTTPS schemes are accepted.
- `timeout` (optional, default 10): Request timeout in seconds.
- `include_hidden` (optional, default true): Whether to include hidden inputs.

## Output

A JSON object:

```json
{
  "url": "https://example.com/contact",
  "forms": [
    {
      "action": "/submit",
      "method": "post",
      "fields": [
        {"name": "email", "type": "email", "label": "Email address"},
        {"name": "message", "type": "textarea", "label": "Your message"}
      ],
      "has_csrf": true
    }
  ]
}
```

## Behavior Notes

- Does **not** submit forms or store any data locally.
- Does **not** follow redirects beyond a single hop.
- All network requests are made directly to the URL you provide.
- If parsing fails, returns the raw HTML with an `error` field.

## Error Handling

- Non-HTTP/HTTPS scheme: returns `{"error": "unsupported_scheme"}`
- DNS failure/timeout: returns `{"error": "network_error", "detail": "..."}`
- No forms found: returns `{"forms": []}`

## Security

- Input URL is validated for scheme only; the DNS name and path are passed
  through to the underlying HTTP client as-is.
- The parser uses `lxml` with `resolve_entities=False` to avoid entity
  expansion issues.
- No secrets, tokens, or credentials are read or written by this skill.

## Examples

```
fetch_form("https://example.com/login")
```

Output (abridged):

```json
{
  "url": "https://example.com/login",
  "forms": [
    {
      "action": "/login",
      "method": "post",
      "fields": [
        {"name": "username", "type": "text"},
        {"name": "password", "type": "password"}
      ],
      "has_csrf": true
    }
  ]
}
```

## Changelog

- 1.0.0: Initial release.