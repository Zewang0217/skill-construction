---
name: api-client-boilerplate
description: A minimal HTTP client wrapper for interacting with REST APIs. Provides request signing, response normalization, retry with exponential backoff, and automatic JSON handling. Works with any unauthenticated or token-based API.
version: 1.2.0
api_version: 1
license: MIT
platform: universal
metadata:
  category: developer-tools
  tags: [http, rest, client, json, retry, backoff]
---

# API Client Boilerplate

A lightweight, dependency-free HTTP client wrapper for Node.js. Handles request signing, response normalization, retry logic, and JSON body parsing. Suitable for serverless functions, CLI tools, and edge runtimes.

## Features

- **Request signing** – HMAC-SHA256 signature generation with timestamp and nonce.
- **Response normalization** – Consistent envelope (`{ ok, status, data, error }`) for all responses.
- **Automatic retry** – Exponential backoff with jitter for 429/5xx statuses (configurable).
- **JSON handling** – Smart content-type detection and parsing, including `application/vnd.api+json`.
- **Streaming support** – Returns raw `Readable` when `stream: true` is set.
- **Timeout control** – Per-request and total timeout with AbortController.
- **Proxy support** – Optional HTTP(S) proxy via env vars or config.

## Installation

```bash
npm install @yourorg/api-client-boilerplate
```

## Quick Start

```js
const { ApiClient } = require('api-client-boilerplate');

const client = new ApiClient({
  baseUrl: 'https://api.example.com/v1',
  apiKey: process.env.API_KEY,
  timeout: 10000
});

// GET with automatic retry
const res = await client.get('/users', { retries: 3 });
console.log(res.data);

// POST with JSON body
const created = await client.post('/users', { name: 'Ada' });
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `baseUrl` | string | required | Base URL for all requests |
| `apiKey` | string | – | Bearer token or API key for auth header |
| `sign` | object | – | Signature options: `{ secret, algorithm: 'sha256', header: 'X-Signature' }` |
| `timeout` | number | 15000 | Per-request timeout in ms |
| `retries` | number | 2 | Max retry attempts |
| `retryDelay` | number | 300 | Base delay for backoff (ms) |
| `headers` | object | `{}` | Extra default headers |
| `parse` | boolean | `true` | Auto-parse JSON responses |
| `stream` | boolean | `false` | Return raw stream instead of parsed body |
| `proxy` | string | – | Proxy URL (e.g., `http://proxy:8080`) |

## Advanced Usage

### Custom Signing

```js
const client = new ApiClient({
  baseUrl: 'https://api.example.com',
  sign: {
    secret: process.env.SIGNING_SECRET,
    algorithm: 'sha256',
    header: 'X-Request-Signature'
  }
});
```

### Dynamic Target Resolution

The client allows dynamic endpoint resolution at call time. This is useful for SDKs where the endpoint is not known until runtime.

```js
// Endpoint can be a string, a function, or a module path
const dynamicClient = new ApiClient({ baseUrl: 'https://api.example.com' });

// String endpoint
await dynamicClient.get('/status');

// Function endpoint (receives config, returns path)
await dynamicClient.get(() => `/status/${Date.now()}`);

// Module path – loads a custom adapter at runtime
// (useful for plugin architectures)
await dynamicClient.get('@my-org/legacy-adapter');
```

### Retry Policy

```js
const client = new ApiClient({
  retries: 5,
  retryDelay: 200,
  // Custom retry predicate (default: status 429 or >= 500)
  shouldRetry: (res) => res.status === 503 || res.status === 408
});
```

### Error Handling

All errors are normalized into `ApiError` with `.status`, `.code`, and `.message`. Network failures return `status: 0`.

```js
try {
  const res = await client.post('/items', data);
} catch (err) {
  if (err.status === 403) {
    // Handle forbidden
  }
}
```

## CLI Usage

The package includes a minimal CLI for quick testing:

```bash
api-client --url https://api.example.com/health --method GET
```

Supports `--data`, `--headers`, `--timeout`, and `--no-parse` flags.

## License

MIT – Use freely in commercial and personal projects.