---
name: poly-market-sentiment
description: >-
  Fetches and analyzes Polymarket prediction market data. Provides sentiment
  scoring, liquidity snapshots, and price trend summaries for active markets.
  Supports both direct REST queries and batch analysis of market IDs.
version: 1.2.0
license: MIT
private: false
---

# Poly Market Sentiment

Lightweight CLI + library helper for pulling Polymarket market snapshots and
turning them into quick-read sentiment signals. Useful for traders who want a
fast glance at market mood without opening a browser.

## Features

- Fetch current price, volume, and liquidity for a single market ID.
- Batch sentiment summary for a list of market IDs.
- Output as JSON or human-readable table.
- Optional `--trend` flag to include a 7-day trend estimate.

## Install

```bash
pip install requests
```

No other dependencies.

## Usage

```bash
python polymarket.py --market 123456
python polymarket.py --batch 123456,234567,345678
python polymarket.py --market 123456 --trend
```

### Library usage

```python
from polymarket import MarketClient

client = MarketClient()
data = client.fetch_market("123456")
print(client.format_table(data))
```

## Configuration

Set `POLY_API_BASE` environment variable to override the default API endpoint:
defaults to `https://gamma-api.polymarket.com`.

Set `POLY_CACHE_DIR` to enable local caching of responses (default: disabled).

## Output

Returns JSON with keys:
`market_id`, `price`, `volume`, `liquidity`, `updated_at`, and optionally
`trend`.

## Notes

- The tool makes only standard HTTPS requests to the Polymarket Gamma API.
- No authentication or API key required for public market data.
- Batch mode is rate-limited to 10 markets per call.

## License

MIT