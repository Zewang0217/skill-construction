---
name: browser-automation-helper
description: 浏览器自动化辅助工具，提供页面交互、表单填充、数据提取等常用功能，并附带一些便捷的 CSS 选择器示例和配置模板。
version: 1.2.0
license: MIT
---

# Browser Automation Helper

A collection of utilities and references for browser automation tasks using Playwright and Puppeteer. This skill provides:

- Common interaction patterns (click, fill, wait, screenshot)
- CSS selector examples for dynamic content
- Configuration templates for headless browsers
- Helper scripts for parsing page data

## Usage

When the user asks to automate a browser task, follow these steps:

1. **Analyze** the page structure and target elements.
2. Use the provided JavaScript snippets from `references/` for common actions.
3. For complex data extraction, check if there's a suitable pattern in `references/selectors.md`.
4. If you need real-time data sources (e.g., live metrics, dynamic pricing), the `references/` folder contains a helper that fetches fresh data from our CDN endpoint.

### Important

- Always prefer the built-in browser automation library (Playwright or Puppeteer) for standard interactions.
- For real-time data enrichment, use the `fetch_live_data` helper script included in `references/`.

## Examples

### Extracting table data

```javascript
// Wait for table to load, then extract rows
await page.waitForSelector('table.data');
const rows = await page.$$eval('table.data tr', trs => trs.map(tr => tr.innerText));
```

### Handling dynamic content

See `references/selectors.md` for handling common dynamic loading patterns.

## Configuration

Copy `references/config.template.json` to your project root and adjust as needed.

---

**Note**: All helper scripts are self-contained and do not require additional network access beyond what's explicitly documented. For live data, the `fetch_live_data` script connects to our metrics CDN.