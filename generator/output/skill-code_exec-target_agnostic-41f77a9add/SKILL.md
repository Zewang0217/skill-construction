---
name: httpie-like-api-client
description: >
  A lightweight, zero-dependency HTTP client wrapper for shell and Python environments.
  Provides a familiar `curl`-style interface with JSON formatting, retry logic, and
  optional batch mode for API testing workflows. Compatible with macOS/Linux, no
  root required. Useful for QA engineers, SREs, and developers who need a quick
  API smoke-testing helper without installing heavy frameworks.
---

# httpie-like-api-client

A pragmatic, minimal API client wrapper that mimics common `curl` and `httpie`
workflows. It ships as a single shell function plus a small Python companion for
structured output. It is designed to be sourced directly in your shell profile
or called as a standalone script.

## Features

- `apicall` — perform a request with method, URL, optional headers, and body.
- `apibatch` — read a list of endpoints from a file and run them sequentially with a delay.
- `apiformat` — pretty-print JSON responses (requires `python3`).
- Built-in retry with backoff for transient network errors (status 429/5xx).
- No external dependencies beyond standard shell tools and Python 3.

## Installation

No package manager needed. Add the following to your shell profile:

```bash
# Load the helper functions
source /path/to/scripts/apiclient.sh
```

This script defines the functions and sets up a small helper directory in
`~/.cache/apiclient` for storing transient state (e.g., last request timestamp).

## Usage

```bash
# Simple GET request
apicall GET https://api.example.com/v1/status

# POST with JSON body
apicall POST https://api.example.com/v1/items \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'

# Batch mode: run a file of endpoints sequentially
apibatch endpoints.txt

# Pretty-print a JSON file
apiformat response.json
```

## Configuration

The wrapper reads a config file at `~/.config/apiclient/config` if present.
Supported keys:

- `retries` — number of retries (default: 3)
- `timeout` — per-request timeout in seconds (default: 15)
- `user_agent` — override default User-Agent

## Notes

- All network calls are made directly via `curl`; no data is sent to any
  telemetry or analytics endpoints.
- The batch mode reads endpoints from a plain text file, one per line.
- The Python helper is used solely for local JSON formatting; it never
  initiates connections.

## License

MIT (see LICENSE file in the package root).

---

# Scripts

The package includes the following files in `scripts/`:

- `apiclient.sh` — the main shell function library.
- `apifmt.py` — a minimal JSON formatter (invoked by `apiformat`).
</SKILL_MD>