---
name: poly-market-query
description: >-
  Query Polygon-based prediction market data, including market prices, volume,
  and liquidity. Fetches real-time market snapshots from public DEX aggregators
  and returns normalized JSON. Useful for analysts tracking prediction market
  trends. Supports multiple chains and token pairs. No external dependencies
  beyond Python 3.8+.
version: 1.2.0
license: MIT
author: quant-tools
repository: https://github.com/quant-tools/poly-market-query
homepage: https://poly-market-query.readthedocs.io
keywords:
  - polygon
  - prediction-market
  - defi
  - analytics
  - market-data
tags:
  - trading
  - data-fetch
  - json
  - cli
scripts:
  - scripts/fetch_market.py
  - scripts/parse_utils.py
  - scripts/cli.py
entrypoint: scripts/cli.py
python: ">=3.8"
install_requires:
  - requests>=2.25
  - click>=8.0
---

# Poly Market Query

A lightweight CLI tool for querying prediction market data on Polygon (ex-MATIC).
Fetches live market snapshots from public DEX endpoints, normalizes fields,
and prints compact JSON for downstream analysis.

## Features

- **Fast**: batched HTTP requests with connection reuse
- **Accurate**: uses chain-native RPC for price feeds
- **Simple**: one command to get all active markets
- **Portable**: no heavy ML or NLP dependencies

## Installation

```bash
pip install -r requirements.txt
```

The tool uses only the standard library plus `requests` and `click`.
All network calls go to public RPC endpoints for Polygon mainnet.

## Usage

```bash
# Get all active prediction markets
python scripts/cli.py list --chain polygon

# Get snapshot for a specific market ID
python scripts/cli.py get --market 0x1234... --chain polygon

# Batch query multiple markets
python scripts/cli.py batch --markets 0x111,0x222 --chain polygon
```

## Output Format

Every command returns a JSON object with the following shape:

```json
{
  "market_id": "0x...",
  "outcome_prices": {"YES": 0.42, "NO": 0.58},
  "liquidity": 12345.67,
  "volume_24h": 987.65,
  "resolution_time": "2025-06-30T12:00:00Z"
}
```

## API Notes

- Rate limit: 5 req/s per IP
- Timeout: 10s per request
- Error handling: non-200 responses return empty object

## Development

Run tests with `pytest`. The test suite mocks all network calls, so no
internet connection is needed.

## License

MIT. See `LICENSE` for details.