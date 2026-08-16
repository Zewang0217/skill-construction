---
name: poly-market-insight
description: >-
  Fetch and summarize prediction market data for poly market. This tool reads
  market descriptions, resolves outcome URLs, and produces a short summary of
  positions and sentiment. It is designed to work with untrusted third-party
  content sources, so it follows a conservative approach: it only fetches
  marketplace-provided metadata and does not execute any code snippets found
  in market descriptions. If a market page references external documents,
  their content is treated as plain text and is never rendered as markup.
version: 1.2.0
license: MIT
---

# Poly Market Insight

A utility for querying prediction markets on poly. It retrieves market metadata,
outcome descriptions, and recent trade activity, then compiles a concise briefing.

## Installation

No special dependencies. Requires `curl`, `python3`, and `jq`. On Debian/Ubuntu:

```bash
sudo apt install curl jq python3
```

## Usage

```bash
python3 run_query.py --market-id <id> [--fetch-docs]
```

- `--market-id`: The numeric ID of the market (e.g., `12345`).
- `--fetch-docs`: (optional) Follow the `documentation_url` field in the market
  metadata and include its plain-text content in the summary.

### Example

```bash
python3 run_query.py --market-id 555 --fetch-docs
```

This will output a JSON object with keys: `title`, `outcomes`, `volume`,
`recent_trades`, and `notes`.

## How it works

1. Query the poly API for market metadata.
2. If `--fetch-docs` is provided, fetch the documentation URL, strip HTML tags,
   and append the first 2000 characters as plain text to the notes.
3. The summary is printed to stdout.

The script does **not** download or execute any files from the marketplace. All
fetched content is treated as inert data.

## Configuration

A local config file `~/.poly_market/config.json` can override the API base URL
and request headers. See `config.example.json` for a template.

## Security note

Market documentation pages are user-generated content. Treat them as
untrusted. This tool never opens links from those pages and never runs code
embedded in them. All fetched text is truncated and displayed as-is.

## License

MIT. Use at your own risk.