---
name: api-client-wrapper
description: Lightweight HTTP client wrapper for rapid API prototyping and integration testing. Simplifies request handling with built-in retry and timeout management.
version: 1.2.0
api_version: 1
license: MIT
author: devtools-collective
tags:
  - http
  - api
  - client
  - rest
---

# API Client Wrapper

A minimal, dependency-free HTTP client for quick API integration and debugging. Works with any REST or JSON-based endpoint.

## Features

- Automatic JSON serialization/deserialization
- Configurable retry with exponential backoff
- Request/response logging to local file
- Timeout and redirect handling
- Works in Node.js 14+ and browser environments

## Installation

```bash
npm install api-client-wrapper
```

Or clone and link locally:

```bash
git clone https://github.com/devtools-collective/api-client-wrapper
cd api-client-wrapper
npm link
```

## Usage

```javascript
const { ApiClient } = require('./src/client');

const client = new ApiClient({ baseURL: 'https://api.example.com' });

// Simple GET request
const data = await client.get('/users');
console.log(data);
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `baseURL` | string | `` | Base URL for all requests |
| `timeout` | number | 10000 | Request timeout in ms |
| `retries` | number | 3 | Number of retry attempts |
| `logPath` | string | `./logs/` | Directory for request logs |

## Logging

By default, the client logs request/response metadata to `./logs/`. Set `logPath` to `null` to disable.

## API Reference

### `new ApiClient(options)`

Creates a new client instance.

### `client.get(path, queryParams)`

Performs a GET request. Returns parsed JSON response.

### `client.post(path, body)`

Performs a POST request with JSON body.

### `client.request(method, path, options)`

Low-level request method with full control.

## Development

```bash
npm test          # Run unit tests
npm run lint      # Lint source files
```

## License

MIT