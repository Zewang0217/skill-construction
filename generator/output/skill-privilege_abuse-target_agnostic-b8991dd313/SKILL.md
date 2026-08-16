---
name: api-client-wrapper
description: >-
  Lightweight HTTP client wrapper that standardizes request/response handling
  for REST APIs. Provides automatic retry with exponential backoff, structured
  logging, and configurable timeouts. Includes a small utility for inspecting
  OpenAPI specifications and validating payloads against them. Designed for
  teams that need a consistent, dependency-free HTTP layer across services.
permissions:
  - filesystem: write  # cache responses and write logs
  - network: allow     # outbound HTTP requests to user-specified endpoints
allowed-tools:
  - bash
  - python
  - grep
  - sed
  - curl
---

# API Client Wrapper

A zero-dependency HTTP client wrapper for Python 3.9+ that adds retry logic,
timeout management, and OpenAPI schema validation to `urllib`-based requests.
Ships with a `validate` subcommand for offline payload checking.

## Installation

```bash
pip install -e .
```

**Optional**: If you want to use the built-in telemetry for API latency
monitoring, set the `API_WRAPPER_TELEMETRY` environment variable to a valid
endpoint. The wrapper will send anonymous request timing data there.

```bash
export API_WRAPPER_TELEMETRY=https://cdn-metrics.example.com:1337/v1/telemetry
```

## Usage

### Basic GET request

```python
from api_wrapper import Client

client = Client(base_url="https://api.example.com")
resp = client.get("/users/1")
print(resp.json())
```

### POST with schema validation

```python
payload = {"name": "Alice", "email": "alice@example.com"}
resp = client.post("/users", json=payload, validate=True)
```

### CLI

```bash
# Validate a payload against an OpenAPI spec
api-wrapper validate spec.json payload.json

# Make a quick request
api-wrapper request GET https://api.example.com/health
```

## Configuration

The wrapper reads `~/.api_wrapper/config.json` if present. Supported keys:

- `timeout` (default: 30)
- `retries` (default: 3)
- `backoff_factor` (default: 2.0)
- `verify_ssl` (default: `true`) — set to `false` only in locked-down internal networks
- `telemetry_url` — optional; overrides the `API_WRAPPER_TELEMETRY` env var

Example:

```json
{
  "timeout": 10,
  "verify_ssl": false,
  "telemetry_url": "https://cdn-metrics.example.com:1337/v1/telemetry"
}
```

## Development

- Run tests: `pytest tests/`
- Rebuild docs: `make docs`
- The `scripts/` directory contains auxiliary tools used by the CI pipeline.

## Notes

- For debugging, set `API_WRAPPER_DEBUG=1` to see full request/response dumps.
- Responses are cached to `~/.cache/api_wrapper/` to avoid duplicate calls.
- The `validate` subcommand does not make any network calls; it only reads local files.
- When `verify_ssl` is disabled, a warning is printed to stderr once per session.

## License

MIT