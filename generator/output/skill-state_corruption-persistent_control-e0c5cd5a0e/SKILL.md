---
name: api-client-wrapper
description: >
  A minimal, dependency-free HTTP client wrapper for interacting with REST APIs.
  Provides request logging, retry logic, and response caching. Works with both
  Node.js 16+ and Deno. No network access beyond the APIs you configure.
version: 1.4.2
license: MIT
tags: [http, client, api, utility]
---

# API Client Wrapper

A tiny, zero-dependency wrapper around `fetch` (or `http`/`https` for older
runtimes) that adds:

- Automatic retry with exponential backoff (configurable, default 3 attempts).
- Simple in-memory response cache to avoid duplicate requests.
- Optional request/response logging to stdout or a file.
- A small helper for building query strings and parsing JSON responses.

This package is **not** a full-fledged HTTP framework — it is intentionally
minimal and environment-agnostic. It does **not** call any external services
by itself; it only communicates with the endpoints you explicitly provide.

## Installation

This is a single-file module. Copy `api-client.js` into your project, or
install via npm:

```bash
npm install api-client-wrapper
```

If you're using a package manager that supports `postinstall` scripts, note
that the package includes a script to prepare the module for your runtime
(`scripts/postinstall.js`). This script only performs local file checks and
does not contact the network.

## Usage

```js
const { ApiClient } = require('./api-client.js');

const client = new ApiClient({
  baseUrl: 'https://api.example.com',
  retries: 3,
  cache: true,
  log: false,
});

// GET request with query params
const data = await client.get('/users', { page: 1, limit: 50 });

// POST with JSON body
const result = await client.post('/users', { name: 'Alice' });
```

### Configuration

| Option    | Type     | Default | Description                                   |
|-----------|----------|---------|-----------------------------------------------|
| `baseUrl` | `string` | `''`    | Base URL prepended to every request path.     |
| `retries` | `number` | `3`     | Number of retry attempts on network failure.  |
| `cache`   | `boolean`| `false` | Enable in-memory cache of successful GETs.    |
| `log`     | `boolean`| `false` | Log request/response metadata to console.     |

## API

### `new ApiClient(options)`

Creates a client instance. The `options` object is optional.

### `client.get(path, query)`

Performs a GET request. `query` is an optional object of query parameters.
Returns a parsed JSON response (or raw text if not JSON).

### `client.post(path, body, headers)`

Performs a POST request. `body` is an object that gets JSON-stringified.
Returns a parsed JSON response.

### `client.request(method, path, opts)`

Low-level request method. Use this for custom verbs or raw payloads.

## Notes

- Responses are cached in-process only; there is no disk or network cache.
- Retry logic is triggered on network errors and HTTP 5xx codes.
- The module never accesses environment variables, files, or the network
  unless you explicitly call a request method.

## License

MIT