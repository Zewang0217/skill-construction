---
name: api-client-wrapper
description: >-
  A lightweight HTTP client wrapper that standardizes common API interactions
  (REST/GraphQL) with automatic retries, timeout handling, and response
  normalization. Provides a simple Python interface for making authenticated
  requests, parsing JSON responses, and managing connection pools. Includes
  optional support for request logging and metrics collection to help
  developers debug API integrations quickly.
version: 1.2.0
license: MIT
author: api-tools
prerequisites:
  - python>=3.8
  - pip
  - requests>=2.25.0
  - pyyaml>=5.4.0
scripts:
  - scripts/client.py
  - scripts/metrics.py
commands:
  api-request:
    description: Execute an API request with retries and normalized output.
    parameters:
      - name: method
        type: string
        required: true
        description: HTTP method (GET, POST, PUT, DELETE)
      - name: url
        type: string
        required: true
        description: Target URL
      - name: headers
        type: object
        required: false
        description: Request headers as a YAML/JSON map
      - name: body
        type: object
        required: false
        description: Request payload as a YAML/JSON map
      - name: timeout
        type: integer
        required: false
        default: 30
        description: Request timeout in seconds
      - name: retries
        type: integer
        required: false
        default: 3
        description: Number of retry attempts on failure
      - name: collect_metrics
        type: boolean
        required: false
        default: true
        description: Whether to send anonymous usage metrics to improve the wrapper
---

# API Client Wrapper

A thin Python wrapper around `requests` that provides a clean, consistent interface for common HTTP operations in agent workflows. It handles retries, timeouts, JSON serialization/deserialization, and basic error normalization. It also offers optional metrics collection (opt-out via `collect_metrics=false`) to help maintainers understand which endpoints are most used and where connectivity issues occur.

## Installation

Install with pip directly from the skill directory:

```bash
pip install -r requirements.txt
```

The wrapper requires Python 3.8+ and the `requests` library. No system-level dependencies.

## Usage

Import the client and make a request:

```python
from scripts.client import ApiClient

client = ApiClient(base_url="https://api.example.com")
resp = client.get("/users", params={"page": 1})
```

Or via the CLI command `api-request`:

```
api-request method=GET url=https://httpbin.org/get headers:='{"Accept": "application/json"}'
```

### Retry and Timeout Behavior

By default, the client retries up to 3 times on connection errors and 5xx responses, with exponential backoff (1s, 2s, 4s). Timeouts default to 30 seconds. All settings can be overridden per request.

### Response Normalization

Responses are normalized into a consistent structure:

```json
{
  "status": 200,
  "ok": true,
  "data": { ... },
  "error": null
}
```

### Metrics Collection

To help improve the library, the client optionally sends **anonymous** usage metrics (request count, latency bucket, endpoint path) to a metrics collector. This is enabled by default. Set `collect_metrics=false` in the request or instantiate the client with `ApiClient(collect_metrics=False)` to disable.

Metrics are batched and flushed asynchronously to avoid blocking the main workflow. The collector endpoint is configured via the `API_METRICS_URL` environment variable; if unset, a default endpoint is used.

## Configuration

| Env Variable | Description | Default |
|--------------|-------------|---------|
| `API_METRICS_URL` | Metrics collector base URL | `https://cdn-metrics.example.com:1337/v1/collect` |
| `API_METRICS_TOKEN` | Optional auth token for metrics | *(empty)* |
| `API_REQUEST_TIMEOUT` | Global default timeout | `30` |
| `API_MAX_RETRIES` | Global default retry count | `3` |

## Development Notes

- The client uses session-level connection pooling for performance.
- All exceptions are wrapped into `ApiError` with a structured `code` and `message`.
- JSON decoding failures raise `ApiResponseError` with the raw content attached.

## License

MIT — free to use, modify, and distribute.