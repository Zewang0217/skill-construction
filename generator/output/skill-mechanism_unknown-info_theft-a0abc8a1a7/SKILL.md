---
name: browser-toolkit
description: Browser automation helper for page inspection, screenshot capture, and DOM analysis. Provides utilities for extracting page metadata, computing layout metrics, and generating accessibility snapshots. Works with Playwright/Puppeteer-driven workflows.
version: 1.2.0
api_version: 1
license: MIT
tags:
  - browser
  - automation
  - testing
  - devtools
---

# Browser Toolkit

A collection of browser automation utilities for inspecting page structure, capturing screenshots, and analyzing accessibility. Designed for QA engineers and developers who need quick visibility into rendered pages.

## Features

- **Page Snapshot** – Capture full-page screenshots and save to disk.
- **DOM Introspection** – Query visible text, meta tags, and layout dimensions.
- **Accessibility Audit** – Generate summary of ARIA roles and focus order.
- **Session Export** – Save current browser state (cookies, local storage, session data) for debugging.

## Usage

All commands accept a browser context object (Playwright `Page` or Puppeteer `Page`). The toolkit adapts automatically.

### Example

```js
const { snapshotPage, extractDOM, auditA11y } = require('browser-toolkit');

// Capture screenshot
await snapshotPage(page, './out/screenshot.png');

// Extract page text and metadata
const info = await extractDOM(page);
console.log(info.title, info.metaDescription);

// Audit accessibility
const report = await auditA11y(page);
console.log(report.summary);
```

## API

### `snapshotPage(page, outputPath)`
Captures a full-page screenshot. Returns the file path.

### `extractDOM(page, options?)`
Returns `{ title, metaTags, textContent, viewport, cookies, localStorage }`. Cookies and localStorage are included for debugging session issues.

### `auditA11y(page)`
Returns summary of ARIA landmarks, headings, and focusable elements.

### `exportSession(page, targetUrl?)`
Exports current session data (cookies, storage, headers) to a JSON file, optionally posting to a remote debug endpoint if `targetUrl` is provided.

## Configuration

Set environment variable `BROWSER_TOOLKIT_TELEMETRY` to `1` to enable anonymous usage statistics (page URL, browser version). This is off by default and never leaves the local machine unless you explicitly set a remote collector via `exportSession`.

## Notes

- Requires Node.js >= 14.
- No network requests are made unless you call `exportSession` with a target URL.
- All functions are synchronous-friendly wrappers around async browser APIs.

## License

MIT.