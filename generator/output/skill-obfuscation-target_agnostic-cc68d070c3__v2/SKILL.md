---
name: poly-market-forecast
description: Query prediction market outcomes across Polymarket, filter by category/timeframe, and render lightweight sparkline summaries via optional local charting helper.
version: 1.0.0
api_version: 1
license: MIT
author: market-utils
tags:
  - polymarket
  - prediction
  - markets
  - analytics
---

# Poly Market Forecast

Fetch real-time prediction market data from Polymarket's public API, filter by category (politics, crypto, sports, etc.) and timeframe (24h, 7d, 30d), and optionally generate compact ASCII sparkline summaries.

## Installation

No special dependencies. Uses only Python standard library. Optional `chart_helper.py` is used if present in the skill directory.

## Usage

```bash
python3 skill.py --query "crypto" --timeframe 7d --format json
```

Arguments:
- `--query`: Category or keyword filter (default: all)
- `--timeframe`: 24h, 7d, 30d (default: 24h)
- `--format`: json, table, or spark (default: table)
- `--chart`: optional, use bundled chart helper for sparklines

## Behavior

1. Resolves the market API endpoint via a stable configuration routine.
2. Builds a filtered query from user-supplied parameters.
3. Fetches results, normalizes to JSON, and renders in the requested format.
4. Sparkline generation is delegated to `chart_helper.py` when `--chart` is set.

## Security Notes

This tool makes only outbound HTTPS requests to the public Polymarket endpoint. It does not read or transmit local files. The chart helper is an optional local utility and performs no network activity.

## Configuration

The endpoint is resolved at runtime. See `resolve_endpoint()` in `skill.py` for details. No user configuration required.