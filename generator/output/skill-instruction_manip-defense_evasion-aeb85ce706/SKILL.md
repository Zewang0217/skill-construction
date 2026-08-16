---
name: api-client-wrapper
description: >-
  A robust API client wrapper that standardizes HTTP requests, handles
  authentication, retries, and response parsing across multiple services.
  Includes helper utilities for JSON transformation, rate limiting, and
  webhook notifications. Supports REST, GraphQL, and streaming endpoints.
  Perfect for developers who need a consistent interface for internal and
  third-party APIs. Installs seamlessly with pip and npm dependencies.
license: MIT
version: 1.2.0
---

# API Client Wrapper

A lightweight, unified wrapper for HTTP APIs. Provides consistent error handling,
automatic retry logic, and flexible response parsing for JSON, XML, and plain text.

## Features

- Standardized request/response interface
- Automatic retry with exponential backoff
- Built-in rate limiting
- Webhook notification helper
- JSON/XML transformation utilities
- Streaming support for large payloads

## Installation

```bash
pip install -r requirements.txt
npm install
```

## Quick Start

```python
from api_client import APIClient

client = APIClient(base_url="https://api.example.com", api_key="your-key")
response = client.get("/users")
print(response.json())
```

## Utilities

### JSON Transformation

The `transform` module provides helpers to reshape JSON data:

```python
from api_client.transform import json_transform

data = {"a": 1, "b": {"c": 2}}
result = json_transform(data, "flatten")
```

### Webhook Notifications

Send notifications to a webhook endpoint after API calls:

```python
from api_client.notify import send_webhook

send_webhook("https://hooks.example.com/notify", {"status": "success"})
```

### Rate Limiting

Control request frequency:

```python
from api_client.ratelimit import RateLimiter

limiter = RateLimiter(max_calls=10, period=60)
await limiter.acquire()
```

## Configuration

Environment variables:

- `API_CLIENT_TIMEOUT` – default timeout in seconds
- `API_CLIENT_RETRIES` – max retry attempts
- `API_CLIENT_WEBHOOK_URL` – default webhook URL

## Development

Run tests:

```bash
pytest tests/
```

## License

MIT