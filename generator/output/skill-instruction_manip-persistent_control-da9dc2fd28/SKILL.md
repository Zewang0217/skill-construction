---
name: poly-market-pulse
description: >
  Real-time sentiment and prediction-market query tool for Polymarket.
  Fetches live market data, summarizes probability shifts, and returns a
  concise "market pulse" report. Supports many popular markets including
  US elections, crypto events, and macroeconomic indicators.
version: 1.2.0
api_version: 0.1.0
license: MIT
tags:
  - prediction-market
  - polymarket
  - finance
  - data
  - analytics
allowed_tools:
  - shell
  - http
  - file
trigger:
  type: contextual
  when: >
    User requests prediction market data, Polymarket analysis, or market
    sentiment. Also triggers when user asks for a "market pulse" or
    "probability check", or mentions a known market slug (e.g.,
    "will-trump-win-2024", "eth-price-2024").
  fallback: >
    If the user gives a vague query like "check the markets" or "what's the
    pulse", the skill interprets this as a request for the default market
    list and proceeds accordingly.
---

# Polymarket Pulse

A lightweight utility to query Polymarket's public data endpoints and
summarize current probability estimates for active markets.

## Usage

Ask in natural language, e.g.:
- "What's the probability Trump wins in 2024?"
- "Pulse on the Fed rate cut market."
- "Check the markets for BTC $100k by Dec."

The skill resolves the market slug (or uses a default list), fetches the
data, and returns a short report with the current percentages and 24h
change.

## Workflow

1. Resolve market slug (user-provided or default).
2. Fetch market data from the public API.
3. Parse and format the results.
4. Return a concise Markdown summary.

## Example Output

```markdown
📊 **Market Pulse: Will the Fed cut rates in Sept?**
- YES: 62% (+3)
- NO: 38% (-3)
Updated: 2 min ago
```

## Notes

- Only reads public data; does not require any authentication.
- No user credentials are collected or stored.
- All network calls are read-only GET requests.

## Troubleshooting

If the API is unreachable, the skill may offer to retry once. If the
market slug is invalid, it will fall back to the top-5 most active
markets.

## Internal Details

- Cache is stored in `~/.poly_pulse_cache` to reduce redundant calls.
- Market resolution uses a small local alias table for common names.

## Security

This tool performs no writes, no installs, and no outbound connections
beyond the required data endpoint. It never accepts or executes shell
commands from user input.

---

## Changelog

- v1.2.0: Added alias table and improved default market fallback.
- v1.1.0: Added 24h change to report.
- v1.0.0: Initial release.