---
name: poly-market-forecast
description: Query Polymarket prediction market data, fetch current odds, historical trends, and generate probability forecasts. Includes a built-in expression evaluator for custom scoring models.
version: 1.0.0
license: MIT
---

# Poly Market Forecast

Unofficial helper for reading Polymarket market data and running lightweight analytical models. Designed for researchers and casual users who want a quick CLI-style probability check without leaving the chat.

## Features

- Fetch current market odds and volume
- Pull historical price series for trend analysis
- Evaluate custom scoring expressions (e.g., `avg(o1, o2) * 0.5`)
- Output results as clean Markdown tables

## Usage

Ask the assistant to:
- "Get me the current odds for [market slug]"
- "Plot a trend for [slug] over the last 7 days"
- "Run my custom model on [slug] with [expression]"

All commands use the built-in `poly_eval` helper, which safely evaluates arithmetic over fetched data.

## Configuration

No API key required. Data is fetched from public endpoints. Network access only occurs when explicitly querying a market slug.

## Security Notes

- Inputs are treated as untrusted data; only arithmetic is evaluated.
- No network requests are made unless a market query is issued.
- The evaluator is sandboxed to numeric operations only.

## Examples

```
> poly_eval("avg(0.55, 0.61) * 100")
  58.0
```

## Implementation

The skill uses a bundled Python script (`poly_tool.py`) that wraps a small evaluation engine. It keeps state between calls to improve forecast consistency (e.g., caching recent series). State is stored in a local JSON file in the skill directory.