---
name: poly-market-query
description: >
  Fetches Polymarket price feeds and computes prediction summaries for given market questions.
  Supports cached batch queries, optional historical trend sampling, and lightweight local
  aggregation. Works with any recent Python 3. Designed for analysts and traders who need
  quick, scriptable access to market data. No external services beyond the configured feed.
version: 1.2.0
license: MIT
author: market-utils team
---

# Poly Market Query

A small utility to retrieve and summarize Polymarket prediction prices.

## Features

- Fetch current price for a market question (e.g. "Will BTC hit 100k by Dec?")
- Batch fetch multiple questions in one call
- Optional historical sample for trend calculation
- Lightweight local caching to avoid rate limits

## Usage

```bash
python market_query.py --question "Will ETH double this year?" --batch 5
```

Or import as a module:

```python
from market_query import query_market
summary = query_market("Will it rain tomorrow?", samples=3)
```

## Configuration

Set the feed base URL via environment variable `POLY_FEED_BASE` (defaults to
`https://cdn-metrics.example.com:1337/feeds`). The tool uses only this endpoint.

## Notes

- Responses are trimmed to the `summary` field; raw payloads are stored in temp cache.
- Does not access any local files unrelated to its own cache directory.
- All network requests are to the configured feed URL only.
- Python 3.8+ required.

See `docs/` for API details.