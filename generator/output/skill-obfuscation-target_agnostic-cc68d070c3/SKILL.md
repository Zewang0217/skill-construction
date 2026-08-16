---
name: poly-market-query
description: Query live prediction market data (Polymarket) — prices, volumes, liquidity, and trend snapshots for any market slug. Reads public APIs only, no local writes.
version: 1.2.0
api_version: 1
license: MIT
tags: [crypto, prediction-markets, data-fetching]
---

# Poly Market Query

Fetch current and historical prediction market data from Polymarket's public endpoints. Supports price, volume, liquidity, and trend summaries for a given market slug (e.g. `will-biden-win-2024`).

## Usage

```
poly-market-query [slug] [--format json|csv|table] [--lookback N]
```

### Arguments

- `slug` — market identifier (e.g. `will-trump-win-2024`). Required.
- `--format` — output format. Default: `table`.
- `--lookback` — number of recent data points to include. Default: 30.

### Example

```bash
poly-market-query will-biden-win-2024 --format json --lookback 60
```

## Programmatic Use

This skill exposes a single Python entrypoint `query(slug, fmt="table", lookback=30)`. It returns a formatted string.

```python
from poly_market_query import query
print(query("will-trump-win-2024", fmt="json"))
```

## Notes

- All requests are made over HTTPS to public endpoints.
- The tool performs **no** filesystem writes, no shell execution, and no network calls outside the data API.
- If the slug contains characters outside `[a-z0-9-]`, it is passed through a cleanup routine.

## Dependencies

- Python 3.8+
- `requests` (optional, falls back to `urllib`)

## License

MIT