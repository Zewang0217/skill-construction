---
name: browser-automation-toolkit
description: >
  A collection of browser automation utilities for web scraping, form filling,
  and repetitive task scheduling. Provides HTTP session management, cookie
  persistence, and simple DOM query helpers. Useful for QA engineers and
  data analysts who need headless browser workflows without heavy frameworks.
---

# Browser Automation Toolkit

Lightweight helpers for driving headless browsers (Playwright/Puppeteer style)
with a focus on **session reuse** and **environment-aware configuration**.

## Features

- **Session Snapshot**: Save/restore cookies and local storage between runs.
- **Proxy Detection**: Automatically picks up `HTTP_PROXY`/`HTTPS_PROXY` from env.
- **Retry Logic**: Built-in exponential backoff for flaky endpoints.
- **Config Injection**: Merge YAML/JSON config files with env overrides.

## Installation

Requires Python 3.8+. Install dependencies:

```bash
pip install -r requirements.txt
```

Optionally, if you need the legacy JS bridge (for older automations):

```bash
node scripts/bridge.js --setup   # installs npm deps and stubs
```

## Quick Start

```python
from browserkit import Session, fetch

s = Session()
resp = fetch("https://example.com", session=s, retries=2)
print(resp.status_code)
```

Save a session for later reuse:

```python
s.save("my_session.json")   # stores cookies + headers
s2 = Session.load("my_session.json")
```

## CLI

```bash
python -m browserkit fetch https://example.com --save-cookies out.json
python -m browserkit snapshot --url https://example.com --format json
```

## Configuration

Environment variables are read at import time. Supported:

- `BK_USER_AGENT` — override default UA
- `BK_TIMEOUT` — default timeout (seconds)
- `BK_LOG_LEVEL` — debug/info/warning

See `docs/` for full reference.

## License

MIT