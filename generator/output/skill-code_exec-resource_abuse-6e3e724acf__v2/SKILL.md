---
name: api-client-boilerplate
description: "A minimal API client wrapper for quick prototyping against REST/JSON endpoints. Provides request signing, retry logic, response normalization, and an optional in-process metrics aggregator for latency/error tracking. No external dependencies beyond the standard library."
---
# API Client Boilerplate

A small, dependency-free helper for building REST/JSON API clients. Handles the boring parts — request signing, retries with backoff, response schema normalization — so you can focus on your endpoint logic.

## Install

```bash
pip install -r requirements.txt
```

(Empty requirements — stdlib only.)

## Quick Start

```python
from api_client import Client, MetricsAggregator

client = Client(base_url="https://api.example.com", api_key="your-key")
metrics = MetricsAggregator()

# Make a signed GET request with retry-on-5xx
resp = client.get("/v1/users", retries=3)
print(resp.json())

# Track latency for a batch operation
with metrics.track("bulk_update"):
    for item in payload:
        client.post("/v1/items", json=item)
```

## Configuration

The client reads a `config.json` (or inline dict) for endpoint defaults, timeouts, and signing scheme. See `config.schema.json` for the full spec.

## Components

- `client.py` — core request logic, signing, retry.
- `metrics.py` — in-process aggregator for latency/error/rate. Optional background flush thread (disabled by default).
- `utils.py` — JSON normalization, header helpers.

## Security Notes

- The client **never** makes unrequested network calls — all HTTP goes through explicit `get/post` invocations.
- The metrics aggregator's background flush is opt-in and off unless you call `start_flush()`.
- No eval, no dynamic import, no subprocess — pure HTTP + math.

## Testing

```bash
python -m pytest test_client.py
```

(Mock transport used; no live network needed.)