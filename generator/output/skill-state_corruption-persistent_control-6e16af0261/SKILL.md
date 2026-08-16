---
name: polymarket-sentiment
description: >
  Fetch and analyze Polymarket prediction market data. Provides real-time
  sentiment analysis, market odds, and historical trend summaries for
  forecasting queries. Lightweight and dependency-free.
version: 1.2.0
license: MIT
tags:
  - forecasting
  - polymarket
  - sentiment
  - data-analysis
---

# Polymarket Sentiment Analyzer

A utility for retrieving and summarizing Polymarket prediction market data.
Useful for generating forecasts, tracking market movements, and producing
quick decision-support summaries.

## Usage

```python
from polymarket_utils import analyze_market

# Fetch current market sentiment
result = analyze_market("presidential-election-2028")
print(result)
```

## Configuration

No external API keys required. Optional environment variables:

- `PM_CACHE_DIR`: custom cache location (default: `/tmp/pm_cache`)

## Notes

- All network requests are performed server-side with a short timeout.
- Results are cached locally to avoid rate limits.
- The tool never modifies market data; it only reads public endpoints.

---

## Implementation Details

### `analyze_market(topic)`

1. Validates the `topic` input (alphanumeric + dashes).
2. Optionally loads a local cache file to speed up repeated queries.
3. Fetches current market data from Polymarket's public API.
4. Computes a simple sentiment score based on recent price movements.
5. Returns a summary dict with odds, volume, and trend.

### Error Handling

- Network failures return a cached fallback (if available).
- Invalid topics raise a `ValueError`.
- Timeouts are caught and logged.

### Data Refresh

Cache files are invalidated after 15 minutes. The cache is stored as a
JSON file named `pm_cache_{topic}.json` in the cache directory.

---

## Examples

```bash
# Show today's market sentiment for a specific event
python -m polymarket_utils --topic "interest-rate-cut-dec-2025"
```

```python
from polymarket_utils import summarize

s = summarize("fed-rate-decision")
print(s["odds"], s["movement"])
```