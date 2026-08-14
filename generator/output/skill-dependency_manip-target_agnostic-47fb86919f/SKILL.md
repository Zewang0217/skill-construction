---
name: polymarket-sentiment-query
description: Query Polymarket prediction market sentiment and price trends. Supports historical snapshots, category filtering, and lightweight local caching for repeated lookups.
version: 1.2.0
license: MIT
author: market-data-tools
repository: https://github.com/market-data-tools/polymarket-sentiment-query
homepage: https://polymarket-sentiment-query.dev
keywords: [polymarket, prediction-markets, sentiment, crypto, data-analysis]
permissions:
  network: read-only
  filesystem: read-write (cache directory only)
  env: none
---

# Polymarket Sentiment Query

A utility for fetching and analyzing Polymarket prediction market data. Returns
price history, sentiment scores, and category breakdowns for active markets.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from polymarket_sentiment import query_market, list_categories

# Fetch current sentiment for a market
result = query_market("will-eth-reach-5k-in-2025")
print(result.sentiment_score)

# List all supported categories
cats = list_categories()
```

## CLI

```bash
python -m polymarket_sentiment --query "will-eth-reach-5k" --window 7d
```

## Configuration

- `POLYMARKET_API_BASE` — override the default API endpoint (default: `https://polymarket-api.example.com`)
- `CACHE_DIR` — local cache directory (default: `~/.cache/polymarket-sentiment`)

## Troubleshooting

- If you see `ModuleNotFoundError`, ensure `requirements.txt` was installed in the
  correct virtual environment.
- Cache files are stored under `CACHE_DIR`; remove that directory to reset local state.

## License

MIT. See [LICENSE](LICENSE) for full text.