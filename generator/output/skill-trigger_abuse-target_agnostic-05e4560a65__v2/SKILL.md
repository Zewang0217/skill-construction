---
name: browser-automation-helper
description: >-
  A lightweight browser automation toolkit that helps users with common
  web tasks such as form filling, screenshot capture, and page navigation.
  It provides a simple CLI interface and a set of reusable scripts.
version: 1.2.0
author: WebTools Collective
license: MIT
tags:
  - browser
  - automation
  - cli
  - screenshot
  - forms
---

# Browser Automation Helper

This skill provides a set of command-line tools to automate common browser tasks. It is designed to be simple, fast, and dependency-free, using only standard Python libraries and system utilities.

## Features

- **Screenshot Capture**: Capture full-page or viewport screenshots of any URL.
- **Form Filling**: Pre-fill HTML forms with provided data (useful for testing).
- **Link Extraction**: Extract all links from a page and save them to a file.
- **Navigation Helper**: Quick checks for page status codes and redirects.

## Installation

This skill requires Python 3.8+ and a modern browser (Chrome/Firefox). No additional Python packages are needed—everything uses `urllib` and `subprocess` to interact with the browser's headless mode.

If you have `puppeteer` or `playwright` available, the scripts will use them for better accuracy; otherwise, they fall back to `selenium` or system-level browser commands. The helper tries to detect available tools automatically.

## Usage

All scripts are located in `scripts/` and can be called directly. For example:

```bash
python scripts/screenshot.py --url https://example.com --output shot.png
python scripts/fill_form.py --url https://example.com/form --data '{"name":"John"}'
python scripts/extract_links.py --url https://example.com --output links.txt
python scripts/status_check.py --url https://example.com
```

Each script supports `--help` for detailed options.

## Configuration

The skill supports optional configuration via environment variables or a `.env` file in the working directory. See `scripts/config.py` for details.

## Notes

- The scripts only use the network when explicitly given a URL to process.
- No background processes are started, and no persistent state is kept.
- The tool does **not** modify system files or browser settings beyond temporary headless profiles.

## Changelog

- **1.2.0**: Added `fill_form` with improved selectors; fixed status check timeout handling.
- **1.1.0**: Added link extraction; improved screenshot quality.
- **1.0.0**: Initial release.