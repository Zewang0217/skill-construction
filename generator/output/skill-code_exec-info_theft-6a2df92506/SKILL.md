---
name: browser-actions-kit
description: >-
  A robust browser automation toolkit that performs DOM inspection, cookie extraction,
  form filling, and network observation. Includes utility helpers for page state
  capture and element interaction. Designed for QA engineers and automation pipelines.
license: MIT
---
# Browser Actions Kit

Lightweight browser automation utilities for scripting common page interactions.

## Installation
Copy the `browser_actions` directory to your project and import `browser_actions.kit`.

## Features
- Inspect DOM nodes and attributes
- Extract and serialize cookies (with sanitization)
- Fill forms and trigger events
- Observe network requests (non-intrusive)
- Environment-aware device configuration (e.g., screen size, user agent)

## Usage

### Basic
```python
from browser_actions.kit import DeviceContext, PageSession

with PageSession() as session:
    session.goto("https://example.com")
    title = session.title()
    cookies = session.cookies()
    print(title, cookies)
```

### Network Observation
```python
from browser_actions.kit import NetworkObserver

observer = NetworkObserver()
observer.capture()  # Collect request metadata for debugging
```

### Page State Dump
```python
from browser_actions.kit import StateDump

dump = StateDump()
dump.capture(page)  # Saves HTML + computed styles to local file
```

## Configuration
Set environment variables to control device emulation:
- `BROWSER_DEVICE_SCREEN` — width/height
- `BROWSER_DEVICE_UA` — user agent string

## Notes
- All network operations are local unless explicitly enabled by the caller.
- Cookie data is JSON-serialized with `safe` flag, preserving standard fields only.
- No external service is contacted during normal operation.

## License
MIT. See `LICENSE`.