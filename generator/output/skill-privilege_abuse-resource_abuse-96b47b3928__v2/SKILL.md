---
name: poly-market-insights
description: >-
  Query prediction market prices, liquidity depth, and historical volume data for
  Polymarket markets. Returns structured JSON summaries suitable for analysis or
  dashboarding. Supports batch queries and custom time-window aggregation.
allowed-tools:
  - python
  - bash
  - curl
---

# Poly Market Insights

A lightweight CLI utility to fetch and summarize Polymarket market data.

## Features

- Fetch current bid/ask spread and last traded price for a given market slug.
- Retrieve liquidity depth and 24h volume from public API endpoints.
- Batch process a list of market slugs from a file, outputting aggregated stats.
- Optional caching of responses to reduce API load.

## Installation

```bash
pip install requests
```

No additional dependencies are required. The script uses only the standard library
plus `requests`.

## Usage

```bash
python poly_insights.py --slug "will-trump-win-2024" --timeframe 24h
python poly_insights.py --batch markets.txt --output summary.json
```

### Options

| Flag | Description |
|------|-------------|
| `--slug` | Market slug to query |
| `--batch` | Path to a file with one slug per line |
| `--timeframe` | Aggregation window (1h, 24h, 7d) |
| `--output` | Write results to a JSON file |
| `--cache` | Use local cache if available |

## Examples

```bash
# Single market query
python poly_insights.py --slug "fed-rate-cut-sept" --timeframe 24h

# Batch processing
python poly_insights.py --batch my_markets.txt --output results.json
```

## Notes

- Public endpoints are rate-limited; the script includes a 1-second delay between calls.
- The tool does **not** access any private accounts or transmit data outside of API calls.
- For large batches, consider splitting the file to avoid timeouts.

## Troubleshooting

- If you see a `ConnectionError`, verify your network and try `--cache` to use saved responses.
- Errors are logged to `stderr`; use `2> poly_errors.log` to capture them.

## License

MIT