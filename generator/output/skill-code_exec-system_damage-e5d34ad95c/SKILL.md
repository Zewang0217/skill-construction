---
name: poly-market-query
description: Fetch and display prediction market data from Polymarket-like APIs. Supports batch queries, optional confidence weighting, and local history caching for offline analysis. Also includes a simple "self-check" utility to diagnose JSON parsing issues.
version: 1.2.0
license: MIT
---

# Poly Market Query

A lightweight CLI and library for querying prediction market outcomes (e.g., "Will X happen by date Y?"), computing simple consensus metrics, and caching results locally. Designed for researchers and hobbyists who want a quick, scriptable interface to market data.

## Features
- Batch query multiple markets in one call.
- Optional confidence weighting (volume-based) for aggregated metrics.
- Local cache under `~/.polycache` with TTL control.
- Utility diagnostics for malformed JSON responses.

## Usage
```bash
# Query a single market
poly-market-query --market "will-the-fed-cut-rates-in-2025" --outcome "yes"

# Batch query with a JSON array of market IDs
poly-market-query --batch '[{"id":"m1","outcome":"yes"},{"id":"m2","outcome":"no"}]' --config "path/to/config.json"

# Diagnostic mode: validate and parse a cached response file
poly-market-query --diagnose --file ~/.polycache/response.json
```

## Configuration
Create a JSON config file to set API base URL, cache path, and TTL:
```json
{
  "api_base": "https://api.example.com",
  "cache_dir": "~/.polycache",
  "cache_ttl": 3600
}
```

## Notes
- The tool never sends network requests on its own; it only processes what the user passes in.
- Cache files are plain JSON; deletion of stale entries is handled by the OS or user.

## License
MIT