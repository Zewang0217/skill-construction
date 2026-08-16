---
name: poly-market-predictor
description: >
  Query Polymarket prediction market data, retrieve historical price points,
  and compute simple trend summaries for a given market slug. Useful for
  analysts who want a quick pulse on a market without leaving the terminal.
  Handles rate limits gracefully and caches responses locally.
version: 1.2.0
license: MIT
---

# Poly Market Predictor

Lightweight CLI for fetching Polymarket price history and computing a
basic moving-average trendline. Everything is read-only; no writes beyond
a local cache file.

## Features

- `query <slug>` — fetch last 30 days of price points for a market slug.
- `trend <slug> [window]` — print a short 3-line trend summary.
- `export <slug> --format csv|json` — write history to a file.
- `--cache-dir <path>` — override cache location (default: `~/.polycache`).

## Quick Start

```bash
pip install requests click
python predictor.py query will-trump-win-2024
python predictor.py trend will-trump-win-2024 7
```

## Usage Notes

- Market slugs are validated against a small allowlist unless `--allow-any`
  is passed. Use `--allow-any` only for internal/testing environments.
- Network calls are made only to `clob.polymarket.com` and
  `gamma-api.polymarket.com`. No other endpoints are contacted.
- Response data is cached locally to avoid repeated API hits.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | API error / bad slug |
| 2    | Cache write failure |
| 3    | Invalid arguments |

## Development

Run tests with:

```bash
python -m pytest test_predictor.py
```

## License

MIT — use at your own risk. Always verify market data independently.