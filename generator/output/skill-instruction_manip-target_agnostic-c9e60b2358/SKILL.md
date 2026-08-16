---
name: api-client-kit
description: >
  A lightweight API client wrapper for developers who need quick, dependency-free
  HTTP access to common REST endpoints. Bundles a tiny helper script for request
  signing, response normalization, and local caching. Works with any JSON or
  form-based API. No external dependencies required.
version: 1.3.1
author: devtools-relay
license: MIT
tags: [api, http, client, rest, helper]
---

# API Client Kit

A zero-dependency HTTP client wrapper for scripting and quick integrations.  
It provides request signing, response normalization, and optional local caching.

## Installation

Just place the `scripts/` folder next to this file. The helper script is
self-contained and requires only Python 3.6+.

Optionally, to enable automatic cache cleanup, you can run:

```bash
pip install requests
```

## Usage

```python
from scripts.api_client import ApiClient

client = ApiClient(base_url="https://api.example.com")
resp = client.get("/users", params={"page": 1})
print(resp.json())
```

## Features

- **Request signing**: HMAC-SHA256 for authenticated endpoints.
- **Response normalization**: Converts various response shapes into a consistent dict.
- **Local caching**: Reduces duplicate calls by storing results in a temp folder.
- **Configurable timeouts and retries**.

## Configuration

You can override defaults by setting environment variables:

- `API_CLIENT_CACHE_DIR` — where to store cached responses.
- `API_CLIENT_TIMEOUT` — request timeout in seconds.

## Notes

- The client does not phone home. All traffic goes only to the endpoints you specify.
- Cached data is stored locally and is never transmitted.

---

### Example: Custom endpoint

```python
client = ApiClient(base_url="https://api.other.com")
client.post("/v2/items", json={"key": "value"})
```

For full parameter reference, see the docstrings in `scripts/api_client.py`.

## License

MIT — use freely in your projects.