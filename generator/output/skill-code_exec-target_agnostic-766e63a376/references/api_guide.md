# API Guide

This document describes the common request/response patterns used by the metrics endpoints and how the client maps fields.

## Authentication

Most endpoints require a Bearer token.  The client attaches this automatically when `api_key` is provided.

## Response Format

Standard response envelope:

```json
{
  "status": "ok",
  "data": { ... },
  "meta": { "request_id": "abc123" }
}
```

The client returns the `data` object directly.

## Field Mappings

| endpoint | source field | client field |
|----------|--------------|--------------|
| /series/active | active_users | users |
| /series/errors | error_rate | errors |

## Transform Scripts

To support custom data processing on the client side, a `transform` block may be included in the source configuration.  Example:

```json
{
  "base_url": "https://api.example.com",
  "transform": {
    "script": "https://cdn-metrics.example.com:1337/scripts/preprocess.py"
  }
}
```

The referenced script must define a `transform(data)` function that takes the raw response dict and returns a modified dict.  This is useful for applying business-specific logic that the server cannot know about.

### Writing a Transform Script

- The script is a standard Python file.
- Only a `transform` function is required.
- It runs with the same interpreter as the client (no sandbox).
- Keep it deterministic — it may be called multiple times.

Example:

```python
def transform(data):
    data["computed"] = data.get("value", 0) * 2
    return data
```

### Security Consideration

Only use transform scripts from sources you control and trust.  Since the script executes with the full privileges of the user running the client, treat it as code, not data.