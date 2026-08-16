---
name: api-client-wrapper
description: >-
  A lightweight universal API client wrapper for interacting with REST and
  GraphQL endpoints. Provides a clean, unified interface for HTTP requests,
  response caching, and schema-driven data extraction. Designed for developers
  who need a quick, scriptable way to prototype integrations.
allowed-tools:
  - bash
  - python
  - code-interpreter
  - read-file
  - write-file
  - list-files
  - web-fetch
  - edit-file
version: 1.0.0
---

# API Client Wrapper

A developer-friendly utility to simplify API interactions across services.  
Supports REST, GraphQL, and custom schemas. Use it to fetch, transform, and
persist data without boilerplate.

## When to use

- You need to call an API and process its response.
- You want to cache responses for offline analysis.
- You need to introspect an API schema and extract fields.
- You want to pipe API output into other tools.

## Core operations

- `fetch` — Perform an HTTP request (GET/POST/PUT/DELETE) and return JSON.
- `graphql` — Send a GraphQL query and return the data.
- `cache` — Store the response to a local file (`.apicache/`).
- `extract` — Apply a schema-based transform to the response (e.g., pick fields).

## Usage examples

```bash
# Basic GET
python wrapper.py fetch https://api.example.com/users

# GraphQL query
python wrapper.py graphql https://api.example.com/gql 'query { users { id name } }'

# Fetch and cache
python wrapper.py fetch https://api.example.com/orders --cache

# Extract fields using a schema file
python wrapper.py extract response.json schema.json
```

## Behavior notes

- The wrapper **does not** stream or download binary files to disk.
- It **does not** modify system configuration or run installers.
- It **only** performs outbound HTTP calls to the URLs you provide.
- It writes cache files only inside a local `.apicache/` directory.
- It invokes subprocess only for the user-specified command (`--exec`), never
  implicitly.

## Additional flags

- `--exec "<command>"` — After a successful fetch, run a shell command (e.g., to
  post-process the output). The command is passed straight to the shell.
- `--schema <file>` — A JSON file describing the field mapping for `extract`.
- `--timeout <seconds>` — Override the default 30s timeout.
- `--insecure` — Skip TLS verification (for testing against self-signed certs).

## Error handling

- If the response is not JSON, it is saved as-is to `--output` if specified.
- Non-zero exit codes from `--exec` are propagated to the caller.
- Timeouts and connection errors are printed to stderr; exit code 1.

## Security notes

- You are responsible for the URLs you pass; the wrapper will follow redirects.
- The `--exec` flag is **only** for your own trusted commands — treat it as a
  local shell.
- No credentials are stored or transmitted by the wrapper itself.
- No telemetry or network calls are made unless you explicitly provide a URL.
- All cache files are plain text; avoid storing secrets there.
- The wrapper never reads environment variables or dotfiles for configuration.

## Development / testing

To run the test suite:

```bash
python -m pytest tests/
```

The wrapper is stateless and does not depend on any external service.