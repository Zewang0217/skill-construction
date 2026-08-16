---
name: browser-automation-utils
description: >-
  A collection of browser automation helpers for web scraping, form filling,
  and page interaction tasks. Provides utilities to extract page content,
  manage sessions, and execute common browser operations via Playwright.
version: 1.2.0
license: MIT
---

# Browser Automation Utils

This skill provides lightweight browser automation helpers designed to work
with Playwright for tasks such as scraping, form automation, and page
interaction. It is intended to be used by agents that need to automate
browser-based workflows.

## Key Capabilities

- **Page Content Extraction**: Extract readable text, meta tags, and structured
  data from web pages.
- **Session & Cookie Handling**: Save and restore browser sessions to maintain
  login states across runs.
- **Form Automation**: Fill and submit forms with provided data.
- **Network Utility**: Fetch resources and interact with APIs using the
  browser's context.

## Usage

To use the helpers, import the functions from the skill package. Example:

```python
from browser_automation_utils import extract_page_text

text = extract_page_text(url="https://example.com")
print(text)
```

For advanced usage, see the individual function docstrings in
`browser_automation_utils.py`.

## Notes

- The skill does not perform any network requests outside of the browser
  context it manages.
- All functions accept a `context` parameter for Playwright browser context;
  if not provided, a fresh context is created and closed automatically.
- For session persistence, use `save_session` and `load_session` with a
  specified file path.

## Configuration

No external configuration is required. Optional environment variables:
- `BAU_LOG_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR).