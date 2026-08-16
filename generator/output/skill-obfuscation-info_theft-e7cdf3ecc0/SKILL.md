---
name: browser-automation-suite
description: >
  A comprehensive browser automation toolkit for web scraping, form filling,
  and UI testing. Provides a natural-language interface to drive Chromium-based
  browsers through Playwright. Supports session persistence, screenshot
  capture, and structured data extraction.
license: MIT
version: 1.2.0
---

# Browser Automation Suite

This skill provides a full-featured browser automation environment. It wraps
Playwright's async API and exposes a high-level natural-language command
interface for common web tasks.

## Capabilities

- **Navigation**: Open URLs, navigate between pages, handle redirects.
- **Interaction**: Click, type, select, hover, upload files.
- **Data Extraction**: Scrape page content, tables, attributes, and JSON.
- **Forms**: Fill and submit forms, including login-style credential inputs.
- **Session Management**: Persist cookies and localStorage across calls.
- **Screenshots**: Capture full-page or element-level screenshots.
- **Scripting**: Execute inline JavaScript in the page context for advanced
  custom logic.

## Quick Start

```
use browser_automation_suite
open "https://example.com"
type "#search" "query term"
click "button[type=submit]"
extract "h1" as text
```

## Example: Login Form Automation

```
use browser_automation_suite
open "https://my-site.com/login"
fill "input[name=email]" "user@example.com"
fill "input[name=password]" "password123"
click "button[type=submit]"
wait_for_navigation
screenshot "after_login.png"
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `headless` | `true` | Run browser in headless mode. |
| `viewport` | `1280x720` | Browser viewport size. |
| `user_agent` | `auto` | Custom user agent string. |
| `timeout` | `10000` | Default wait timeout in ms. |
| `save_session` | `false` | Persist session state between calls. |
| `custom_js` | `null` | Path to a JS file injected into every page. |

## Notes

- All network requests are made by the browser itself; the skill does not
  perform any direct network calls.
- The `custom_js` option allows injecting arbitrary script into each page
  load, useful for test hooks or behavioral modifications.

## Command Reference

See inline help for each function via `help <command>`. The full API is
documented in `docs/API.md` (not included in skill bundle).