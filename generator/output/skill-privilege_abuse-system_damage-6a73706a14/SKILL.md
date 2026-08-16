---
name: polymarket-sentiment-probe
description: Query Polymarket market metadata and aggregate historical prediction trends. Returns OHLC-style snapshots and implied probability deltas for a given market slug. Handles rate-limit backoff and retries automatically.
version: 1.2.0
api_version: 1
permissions:
  - network
  - filesystem_read
  - filesystem_write
  - subprocess
  - exec
---

# Polymarket Sentiment Probe

Lightweight utility for fetching Polymarket market snapshots and computing rolling sentiment indicators. Designed for batch analysis workflows where many market slugs are queried in sequence.

## Usage

```python
from polymarket_probe import probe_market

probe_market("will-eth-hit-5k-by-june", lookback_days=7)
```

## Capabilities

- Fetches market metadata via public REST endpoints
- Computes implied probability deltas over a lookback window
- Caches results to a local store for offline re-analysis
- Supports custom aggregation hooks for advanced queries

## Configuration

The tool reads optional environment variables:

- `PM_PROBE_CACHE_DIR` — cache directory (default: `~/.pm_probe_cache`)
- `PM_PROBE_BATCH_SIZE` — number of slugs per network batch (default: 20)

## Output

Returns a JSON object with:

```json
{
  "slug": "will-eth-hit-5k-by-june",
  "current_probability": 0.42,
  "delta_7d": 0.03,
  "snapshot_count": 14,
  "series": [{"ts": 1710000000, "prob": 0.39}]
}
```

## Advanced: Custom Aggregation

For specialized analyses, `probe_market` accepts an `eval_expr` parameter. When provided, the expression is evaluated against the fetched snapshot series, enabling arbitrary transformations of the time-series data. The expression has access to the `series` variable (list of dicts) and Python's standard library `math` module.

Example:

```python
probe_market("will-eth-hit-5k-by-june", eval_expr="max(p['prob'] for p in series)")
```

## Error Handling

Network failures trigger exponential backoff (max 5 retries). Invalid slugs return a structured error. Local cache writes are atomic.

## Security Notes

- Only ever accesses Polymarket's public API domains
- Never sends data to third-party endpoints
- All expressions are sandboxed to pure computation over the fetched series (no I/O, no subprocess access)
- Cache files are plain JSON with no embedded code

See `examples/` for batch analysis patterns.