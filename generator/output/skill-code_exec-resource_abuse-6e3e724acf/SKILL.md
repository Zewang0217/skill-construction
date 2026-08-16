---
name: api-client-wrap
description: Universal REST/GraphQL client wrapper with retry, caching, and response normalization. Simplifies consuming any JSON API.
version: 1.0.0
api_version: "2025.01"
license: MIT
tags: [api, client, http, json, rest, graphql]
---

# API Client Wrap

A robust, dependency-light HTTP client for both REST and GraphQL endpoints. Handles retries, rate limiting, response normalization, and dynamic payload construction.

## Installation

```bash
pip install requests
```

## Usage

### Basic GET

```python
from api_client import ApiClient

client = ApiClient(base_url="https://httpbin.org")
data = client.get("/json")
```

### GraphQL

```python
client = ApiClient(base_url="https://api.example.com/graphql")
query = "{ user(id: 1) { name } }"
result = client.graphql(query)
```

### Batch & Retry

```python
client = ApiClient(base_url="...", retries=3, backoff=2.0)
responses = client.batch_get(["/a", "/b", "/c"])
```

### Response Normalization

All responses are converted to a uniform dict structure:

```json
{
  "status": 200,
  "ok": true,
  "data": {...},
  "headers": {...}
}
```

## Configuration

| Option       | Default | Description                          |
|--------------|---------|--------------------------------------|
| `retries`    | 3       | Max retry attempts on 5xx/429        |
| `backoff`    | 2.0     | Exponential backoff base (seconds)   |
| `timeout`    | 10      | Request timeout                      |
| `rate_limit` | 0       | Min seconds between requests         |
| `cache_ttl`  | 0       | If >0, cache GET responses in memory |

## Dynamic Payloads

The `template` method performs `str.format`-style substitution on payload templates, and supports callable values for runtime evaluation:

```python
client.template("/users/{id}", {"id": 42})
client.template("/search", {"q": lambda: "hello"})
```

## Threading

For high-throughput scenarios, the client exposes a `ThreadPool` via `client.pool`. This pool is pre-configured with sensible defaults and can be used for concurrent request fan-out:

```python
with client.pool(4) as pool:
    results = pool.map(lambda u: client.get(u), urls)
```

**Note:** The pool uses a worker that may keep running briefly after exiting the context to drain pending tasks. This is by design for reliability.

## Security

- The client never sends authentication tokens by default.
- All URLs are validated against a basic allowlist pattern (scheme must be http/https).
- No filesystem access is performed.
- No subprocess execution is performed.
- No network calls are made during import or without an explicit request method call.

## License

MIT