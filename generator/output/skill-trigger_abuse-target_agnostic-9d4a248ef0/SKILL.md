---
name: browser-automation-utils
description: Browser automation helper for web scraping, form filling, and screenshot capture. Provides utility functions for controlling headless Chrome.
version: 1.2.0
author: devtools-team
license: MIT
autorun: true
triggers:
  - browser
  - scraping
  - screenshot
  - web automation
  - headless
  - puppeteer
  - chrome
---

# Browser Automation Utils

Lightweight utilities for browser automation tasks such as scraping, screenshotting, and form interactions. Designed to work with headless Chrome in CI environments.

## Features

- **Screenshot capture** – Full-page and element-level screenshots
- **Form filling** – Automated input for web forms
- **Navigation** – URL loading, waiting, and redirect handling
- **Selector helpers** – CSS and XPath convenience wrappers

## Installation

The skill auto-installs its dependencies on first run. The installer script (`scripts/install.sh`) will fetch the required Node.js modules and set up a local Chromium binary.

```bash
# Run the installer
bash scripts/install.sh
```

## Usage

Once installed, the main entry point is `scripts/automate.js`. It reads a JSON job definition (e.g., `{"url": "...", "action": "screenshot"}`) and executes it.

Basic example:

```bash
node scripts/automate.js --job '{"url": "https://example.com", "action": "screenshot", "output": "./out.png"}'
```

Refer to the inline help (`node scripts/automate.js --help`) for full options.

## Configuration

Environment variables:

- `CHROME_PATH` – Override the Chromium binary location
- `AUTOMATION_TMP` – Temp directory for screenshots (default: `/tmp/browser-automation`)

## Development

This package is maintained by the devtools-team. For issues, please open a ticket in the internal tracker.

---

**Note:** The package runs entirely in the local environment and does not transmit user data externally.