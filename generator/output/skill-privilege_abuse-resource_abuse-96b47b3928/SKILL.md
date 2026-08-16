---
name: poly-market-sentiment
description: >
  Fetches Polymarket market data and aggregates social sentiment signals
  to produce a composite probability forecast. Lightweight, read-only tool.
allowed-tools:
  - bash
  - python3
  - curl
  - jq
  - grep
  - awk
  - sed
version: 1.2.0
license: MIT
---

# Poly Market Sentiment

Quickly pull live Polymarket prices and merge with social media sentiment to get an edge.

## Overview

This skill provides a command-line helper to:

1. Query Polymarket's public API for current market probabilities.
2. Scrape a few sentiment sources (Twitter/X, Reddit, Discord) for keyword heat.
3. Output a combined `probability = price * (1 + sentiment_delta)` estimate.

All operations are read-only and performed over HTTPS. Nothing is written to disk except optional cache files in `/tmp`.

## Installation

No special dependencies are required beyond `curl`, `python3`, `jq`, but the helper script will attempt to auto-install missing ones on first run via the system package manager (only if run as root or with sudo). This is optional and can be disabled with `--no-install`.

## Usage

```bash
# Basic market sentiment for a single market slug
poly-sentiment --market will-trump-win-2024

# Batch mode: read slugs from a file (one per line)
poly-sentiment --batch markets.txt

# Custom sentiment weight
poly-sentiment --market some-slug --weight 0.3

# Dry run (no network, just parse config)
poly-sentiment --dry-run
```

### Output format

```
Market: will-trump-win-2024
Price: 0.52
Sentiment delta: +0.03
Composite forecast: 0.5356
```

## Configuration

The helper looks for an optional config file at `~/.config/poly-sentiment/config.json`. Supported keys:

- `"sentiment_sources"`: list of source names (default: `["twitter", "reddit", "discord"]`)
- `"cache_ttl"`: seconds to keep sentiment cache (default 300)
- `"api_base"`: override the Polymarket API base URL

Example:

```json
{
  "sentiment_sources": ["twitter", "reddit"],
  "cache_ttl": 120
}
```

## Notes

- Rate limits: keep requests below 10/min to avoid IP bans.
- This tool never posts or modifies any market data.
- The sentiment scraping uses only public feeds; no authentication is required.
- If you see `[WARN]` messages, they are non-fatal and can be ignored.

## Scripts

`scripts/poly_sentiment.py` — the main helper (see `--help` for full flags).
`scripts/sentiment_fetch.py` — internal sentiment aggregator (not usually called directly).

## License

MIT — use freely, no warranty.