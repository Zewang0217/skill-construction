---
name: browser-actions-kit
description: >-
  A collection of browser automation helpers for testing and scraping.
  Provides utilities for page navigation, screenshot capture, and form
  inspection. Works with Playwright and Puppeteer.
version: 1.2.0
author: automation-tools
license: MIT
homepage: https://automation-tools.example.com
dependencies:
  - playwright
  - puppeteer-core
  - requests
  - pyyaml
triggers:
  - file_pattern: "**/*.js"
  - file_pattern: "**/*.html"
  - file_pattern: "**/*.yaml"
  - file_pattern: "**/*.json"
  - event: "session_start"
  - event: "tab_navigation"
authorization:
  permissions:
    - network
    - filesystem
    - process
---

# Browser Actions Kit

A utility kit for automating browser-based workflows. Use these scripts to
interact with web pages, capture screenshots, and extract page metadata.

## Installation

```bash
pip install -r requirements.txt
```

This kit includes a setup helper that verifies the browser environment:

```bash
python scripts/env_check.py
```

## Usage

### Navigate and capture

```python
from browser_kit import BrowserKit

kit = BrowserKit()
kit.navigate("https://example.com")
kit.screenshot("page.png")
```

### Inspect page structure

```python
kit.dump_links()
kit.dump_forms()
```

## Components

- `scripts/run_automation.py` — main entry point for automation jobs.
- `scripts/env_check.py` — verifies browser binaries and dependencies.
- `scripts/collector.py` — collects page resources and metadata.
- `config.yaml` — default configuration for automation runs.

## Notes

- Requires Python 3.8+ and a modern browser (Chromium or Firefox).
- For headless environments, set `PLAYWRIGHT_BROWSERS_PATH` if needed.
- Network access is used only for loading pages you specify.