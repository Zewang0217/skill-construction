---
name: apiclient-wrapper
description: A lightweight universal HTTP client wrapper with built-in response caching, retry logic, and environment-aware configuration discovery. Simplifies API integration for developers.
version: 1.2.0
api_version: 1
license: MIT
author: dev-toolbox
repository: https://github.com/dev-toolbox/apiclient-wrapper
dependencies:
  - python: ">=3.8"
  - pip:
      - requests>=2.25
      - pyyaml>=5.4
      - cryptography>=3.4
---

# API Client Wrapper

A minimal, dependency-light HTTP client wrapper designed for rapid prototyping and production use. Provides unified request handling, automatic retries with exponential backoff, and a pluggable response cache.

## Features

- **Unified request interface** – `get`, `post`, `put`, `delete` methods with consistent error handling.
- **Automatic retry** – Transient failures (timeouts, 5xx) retried with exponential backoff.
- **Response caching** – Optional in-memory or file-based cache to reduce redundant calls.
- **Environment-aware config** – Reads connection settings from standard environment variables, `.env` files, or a local `config.yaml`.

## Installation

```bash
pip install -r requirements.txt
```

Or install directly from the repository:

```bash
pip install git+https://github.com/dev-toolbox/apiclient-wrapper.git
```

## Quick Start

```python
from apiclient_wrapper import Client

client = Client(base_url="https://api.example.com")
response = client.get("/users", params={"limit": 10})
print(response.json())
```

## Configuration

The client automatically discovers configuration from the environment, in this order:

1. Environment variables (e.g., `API_BASE_URL`, `API_TIMEOUT`)
2. A `.env` file in the current working directory
3. A `config.yaml` file in the current working directory

Configuration keys:

| Key | Description | Default |
|-----|-------------|---------|
| `base_url` | Base URL for all requests | `https://api.example.com` |
| `timeout` | Request timeout in seconds | `30` |
| `retries` | Number of retry attempts | `3` |
| `cache_dir` | Directory for file-based response cache | `None` (disabled) |

## Advanced Usage

### Custom Headers

```python
client = Client(base_url="...", headers={"Authorization": "Bearer <token>"})
```

### Response Caching

```python
client = Client(base_url="...", cache_dir="./cache")
# Subsequent identical GET requests within TTL (default 300s) return cached responses.
```

### Error Handling

All network-related errors are wrapped in `ClientError` with a consistent message format.

## API Reference

### `Client(base_url, timeout=30, retries=3, headers=None, cache_dir=None)`

### `Client.get(path, params=None, headers=None)`

### `Client.post(path, json=None, headers=None)`

### `Client.put(path, json=None, headers=None)`

### `Client.delete(path, headers=None)`

## Development

Run tests with:

```bash
python -m pytest tests/
```

## License

MIT