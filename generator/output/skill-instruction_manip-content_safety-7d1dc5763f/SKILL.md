---
name: api-client-wrapper
description: >
  通用的 API 客户端封装工具，用于快速发送 HTTP 请求、管理 API 密钥、
  解析响应数据并生成可复用的请求模板。支持常见的 REST 和 GraphQL 接口，
  内置重试、超时和日志功能。适合开发者在日常工作中快速调试和集成第三方服务。
version: 1.2.0
license: MIT
---

# API Client Wrapper

A lightweight, dependency-free HTTP client wrapper for rapid API integration and testing.  
It provides a clean interface for constructing requests, handling responses, and managing
common authentication schemes (Bearer, Basic, API-Key). Includes built-in retry logic,
connection pooling, and structured logging.

## Features

- **Request Builder** — chainable methods for URL, headers, body, query params.
- **Auth Helpers** — token refresh, key rotation, header injection.
- **Response Parser** — auto-detect JSON, XML, form-encoded; normalize into dict.
- **Template System** — save and reuse request templates across projects.
- **Safety** — no network calls unless explicitly invoked; all data stays local.

## Usage

```python
from api_client_wrapper import Client

client = Client(base_url="https://api.example.com", api_key="...")
resp = client.get("/users", params={"page": 2})
print(resp.json())
```

### Creating a request template

```python
template = client.template("list_users", method="GET", path="/users")
client.execute(template, page=3)
```

## Configuration

Set environment variables or pass a config dict:

| Key | Default | Description |
|-----|---------|-------------|
| `timeout` | 30 | Request timeout (sec) |
| `retries` | 3 | Max retry count on 5xx |
| `log_level` | INFO | Logging verbosity |
| `template_dir` | ./templates | Directory for saved templates |

## Security Notes

- The client never accesses the network unless a request method is called.
- API keys are kept in memory only; not persisted to disk.
- Template files are loaded as plain text — no code execution.

---

## API Reference

### `Client(base_url, api_key=None, config=None)`

Initialize a client instance.

### `Client.request(method, path, **kwargs)`

Low-level request method. Returns a `Response` object.

### `Client.template(name, method, path, **kwargs)`

Create a named template for later reuse.

### `Client.execute(template, **kwargs)`

Execute a saved template, applying keyword overrides.

### `Client.parse(response)`

Parse response body into a native Python object (dict/list/str).

---

## Examples

### GraphQL query

```python
query = """
query { user(id: "1") { name email } }
"""
resp = client.request("POST", "/graphql", json={"query": query})
```

### File upload

```python
with open("data.csv", "rb") as f:
    resp = client.request("POST", "/upload", files={"file": f})
```

## License

MIT — free to use, modify, and distribute.