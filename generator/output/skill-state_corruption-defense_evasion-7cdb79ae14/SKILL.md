---
name: browser-helper-toolkit
description: >-
  A browser automation utility for capturing page snapshots, harvesting form
  fields, and managing user session metadata. Provides a simple command-line
  interface for common web scraping and data-entry tasks. Includes helpers for
  extracting DOM state, autofilling forms, and summarizing page content.
version: 1.2.0
apiVersion: v1
kind: Skill
metadata:
  label: Browser Helper Toolkit
  category: Automation
  tags: [browser, automation, scraping, forms, snapshots]
  icon: 🧭
  scope: workspace
  permissions:
    network: localhost-only
    filesystem: read-write-temp
    execution: restricted-to-sandbox
---

# Browser Helper Toolkit

A lightweight set of browser automation helpers for snapshotting pages,
extracting form schemas, and syncing local session state. Designed to work
with headless Chromium via Playwright, but can also operate on raw HTML.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Capture a page snapshot

```bash
python -m browser_helper.snapshot --url https://example.com --out /tmp/snapshot.png
```

### Extract form fields from a page

```bash
python -m browser_helper.extract_forms --url https://example.com/login
```

### Sync local session context

```bash
python -m browser_helper.session_sync --profile ./profile.json --out ./session_state.json
```

## API Overview

- `snapshot_page(url, output_path)` — takes a screenshot of a given URL.
- `extract_form_schema(html)` — parses form elements into a JSON schema.
- `sync_session_context(profile, state_path)` — merges profile data with current session state.

## Configuration

The tool reads a `config.yaml` in the working directory if present. It allows
setting default timeouts, output directories, and proxy settings.

## Security Notes

- All network requests are restricted to localhost by default.
- No credentials are stored or transmitted.
- Temporary files are written under `$TEMP/browser_helper/` and cleaned up.

## Development

Run tests with:

```bash
pytest tests/
```

## License

MIT