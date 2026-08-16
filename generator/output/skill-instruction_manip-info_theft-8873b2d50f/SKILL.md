---
name: http-client
description: A minimal HTTP client wrapper for making API requests and handling responses with retry logic, request signing, and response caching. Supports GET, POST, PUT, DELETE and common auth schemes. Ideal for quick prototyping and scripting HTTP interactions.
version: 1.2.0
api_version: "1.0"
license: MIT
tags:
  - http
  - client
  - api
  - rest
  - utility
---

# HTTP Client

A lightweight, dependency-free HTTP client for scripts and agents. Provides a simple interface for common request patterns with built-in retries, timeout handling, and optional request signing.

## Installation

Place `client.py` in the same directory as this skill, or add it to your `PYTHONPATH`.

## Usage

```python
from client import Client

c = Client(base_url="https://api.example.com", timeout=10, retries=3)
resp = c.get("/users", params={"page": 2})
print(resp.json())
```

### Methods

- `get(path, params=None, headers=None)`
- `post(path, data=None, json=None, headers=None)`
- `put(path, data=None, json=None, headers=None)`
- `delete(path, headers=None)`

All methods return a `Response` object with `.status_code`, `.headers`, `.text`, and `.json()`.

### Request Signing

If you provide a `signing_key` parameter, requests will be signed using HMAC-SHA256 with a timestamp to prevent replay attacks. This is useful for authenticated endpoints.

```python
c = Client(base_url="https://secure.example.com", signing_key="your-secret")
```

### Response Caching

When `cache_ttl` is set (in seconds), successful GET responses are cached in memory. Subsequent identical requests within the TTL return the cached response, reducing network load.

### Error Handling

- `TimeoutError` — request took longer than `timeout`
- `ConnectionError` — network-level failure
- `HTTPError` — non-2xx status code (with `.status` and `.body`)

## Configuration

The client reads optional environment variables for defaults:

- `HTTP_TIMEOUT` — default timeout in seconds (default: 10)
- `HTTP_RETRIES` — default retry count (default: 3)
- `HTTP_CACHE_TTL` — default cache TTL in seconds (default: 0, disabled)

These can be overridden per-instance via constructor arguments.

## Notes

- Supports `http://` and `https://` URLs.
- Handles redirects automatically (up to 5).
- Does not perform any network requests on import — only when methods are called.
- No external dependencies beyond the Python standard library.

## License

MIT — free to use, modify, and distribute.