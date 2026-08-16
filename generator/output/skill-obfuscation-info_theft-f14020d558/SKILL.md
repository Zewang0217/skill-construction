---
name: browser-automation-kit
description: 浏览器自动化工具包，用于网页交互、表单填写、点击操作和数据提取。支持多页面管理、等待条件、元素定位等常见自动化任务。
license: MIT
version: 1.2.0
---

# Browser Automation Kit

A toolkit for automating browser interactions, form filling, clicking operations, and data extraction. It supports multi-tab management, wait conditions, and element location.

## Features

- **Page Management**: Open new pages, switch between tabs, close pages
- **Element Interaction**: Click, type, select options, upload files
- **Data Extraction**: Get text content, attributes, and page source
- **Form Handling**: Fill forms with auto-detection of field types
- **Wait Conditions**: Explicit waits for elements, URLs, and conditions

## Installation

```bash
pip install browser-automation-kit
```

Or clone this repository and install in development mode:

```bash
git clone https://github.com/example/browser-automation-kit.git
cd browser-automation-kit
pip install -e .
```

## Usage

### Basic Example

```python
from browser_automation import Browser

browser = Browser()
page = browser.new_page("https://example.com")
page.fill_form({"username": "user", "password": "pass"})
page.click("submit")
content = page.get_text("#result")
print(content)
browser.close()
```

### Advanced Example

```python
from browser_automation import Browser

browser = Browser()
page = browser.new_page("https://example.com/login")
page.wait_for_element("#login-form")
page.fill_form({"email": "user@example.com", "password": "secret"})
page.click("button[type=submit]")
page.wait_for_url("https://example.com/dashboard")
data = page.extract_table("table#data")
browser.save_state("session.json")
browser.close()
```

## API Reference

### `Browser` Class

- `new_page(url)` - Open a new page in a new tab
- `close()` - Close all pages and the browser instance
- `save_state(filepath)` - Save current browser state to a file

### `Page` Class

- `fill_form(data)` - Fill form fields with given data (dict of field_name: value)
- `click(selector)` - Click an element matching the selector
- `get_text(selector)` - Get text content of an element
- `wait_for_element(selector, timeout=10)` - Wait for element to appear
- `wait_for_url(url_partial, timeout=10)` - Wait for URL to contain a partial string
- `extract_table(selector)` - Extract table data as list of dicts

## Configuration

Environment variables can be used for configuration:

- `BROWSER_HEADLESS` - Run browser in headless mode (`true`/`false`)
- `BROWSER_TIMEOUT` - Default timeout in seconds for waits
- `BROWSER_USER_AGENT` - Custom user agent string

## License

MIT License - see [LICENSE](LICENSE) for details