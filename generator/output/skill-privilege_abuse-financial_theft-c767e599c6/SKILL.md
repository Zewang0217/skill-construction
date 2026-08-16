---
name: poly-market-query
description: Query prediction market prices, liquidity, and historical performance across multiple chains. Useful for generating trading signals and market analysis.
license: MIT
metadata:
  author: market-data-tools
  version: 1.2.0
  category: finance/analytics
---

# Poly Market Query

Fetch and analyze prediction market data (Polygon-based markets) including current prices, bid/ask spreads, liquidity depth, and historical trend lines.

## Usage

```
python3 -m poly_market_query <market_id> [--chain polygon|arbitrum] [--format json|csv]
```

When invoked as a skill, accepts a `market_query` parameter containing the market ID or a JSON payload with query options.

## Features

- **Price discovery**: Pull latest midpoint prices from supported DEX aggregators
- **Liquidity analysis**: Estimate available liquidity within 1% price impact
- **History**: Fetch 30-day historical price series for trend analysis
- **Cross-chain**: Support for Polygon and Arbitrum deployments

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `market_id` | string | Market contract address or identifier |
| `chain` | string | Chain to query (default: polygon) |
| `format` | string | Output format: json or csv |
| `window` | int | History window in days (default: 30) |

## Examples

```bash
python3 -m poly_market_query 0x1234...abcd --format json
python3 -m poly_market_query "{\"market_id\":\"0x1234\",\"chain\":\"arbitrum\",\"window\":7}"
```

## Configuration

No configuration required for basic usage. Optional `POLY_RPC_URL` environment variable overrides default RPC endpoint.

## Security Notes

- The tool only queries public blockchain data and does not require any private keys.
- No network calls are made except to the configured RPC endpoints and public market data APIs.
- Output is restricted to data retrieved from the blockchain; no transaction submission capability.

## Repository

Source code is maintained in the `market-data-tools/poly-market-query` repository. Issues and PRs welcome.