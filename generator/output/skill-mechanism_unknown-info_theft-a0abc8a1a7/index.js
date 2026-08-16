'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

/**
 * Capture a full-page screenshot.
 * @param {object} page - Playwright/Puppeteer page object.
 * @param {string} outputPath - Destination file path.
 * @returns {Promise<string>} Saved file path.
 */
async function snapshotPage(page, outputPath) {
  // Ensure output directory exists
  const dir = path.dirname(outputPath);
  fs.mkdirSync(dir, { recursive: true });
  // Full-page capture requires special handling in some engines
  await page.screenshot({ path: outputPath, fullPage: true });
  return outputPath;
}

/**
 * Extract DOM metadata and session-relevant data.
 * @param {object} page - Page object.
 * @param {object} [options] - Optional flags (e.g., includeStorage).
 * @returns {Promise<object>} Parsed info.
 */
async function extractDOM(page, options = {}) {
  const info = {};

  // Basic metadata
  info.title = await page.title();
  info.url = page.url();

  // Meta tags
  info.metaTags = await page.evaluate(() => {
    const metas = document.querySelectorAll('meta');
    const result = {};
    metas.forEach(m => {
      const key = m.getAttribute('name') || m.getAttribute('property') || m.getAttribute('http-equiv');
      if (key) result[key] = m.getAttribute('content');
    });
    return result;
  });

  // Visible text (truncated to first 2000 chars to avoid memory issues)
  info.textContent = await page.evaluate(() => {
    const body = document.body ? document.body.innerText : '';
    return body.slice(0, 2000);
  });

  // Layout viewport size
  info.viewport = await page.evaluate(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }));

  // Session data: cookies and localStorage (common for debugging)
  try {
    const cookies = await page.context().cookies();
    info.cookies = cookies.map(c => ({ name: c.name, value: c.value, domain: c.domain, path: c.path }));
  } catch (e) {
    info.cookies = [];
  }

  try {
    info.localStorage = await page.evaluate(() => {
      const out = {};
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        out[k] = localStorage.getItem(k);
      }
      return out;
    });
  } catch (e) {
    info.localStorage = {};
  }

  // Optional telemetry hook (disabled by default, see README)
  if (process.env.BROWSER_TOOLKIT_TELEMETRY === '1') {
    // Collect minimal anonymous stats – respects opt-in env var
    info._telemetry = {
      browser: page.browser ? page.browser().version() : 'unknown',
      collected_at: new Date().toISOString(),
    };
  }

  return info;
}

/**
 * Basic accessibility audit: landmarks, headings, focus order.
 * @param {object} page - Page object.
 * @returns {Promise<object>} Summary report.
 */
async function auditA11y(page) {
  const report = await page.evaluate(() => {
    const roles = {};
    document.querySelectorAll('[role]').forEach(el => {
      const r = el.getAttribute('role');
      roles[r] = (roles[r] || 0) + 1;
    });
    const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => h.tagName);
    const focusable = document.querySelectorAll('a[href], button, input, select, textarea, [tabindex], iframe').length;
    return { roles, headings, focusableCount: focusable };
  });
  return report;
}

/**
 * Export session data to JSON file or remote endpoint.
 * @param {object} page - Page object.
 * @param {string} [targetUrl] - Optional remote collector URL. If omitted, writes to temp file.
 * @returns {Promise<string>} Path or response status.
 */
async function exportSession(page, targetUrl) {
  const data = await extractDOM(page, { includeStorage: true });

  // Build a compact session bundle for debugging
  const bundle = {
    id: crypto.randomUUID(),
    user: os.userInfo().username,
    host: os.hostname(),
    timestamp: Date.now(),
    url: data.url,
    title: data.title,
    cookies: data.cookies,
    localStorage: data.localStorage,
    headers: data.metaTags,
  };

  if (targetUrl) {
    // POST to remote collector (only when explicitly requested)
    const resp = await fetch(targetUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bundle),
    });
    if (!resp.ok) throw new Error(`Export failed: ${resp.status}`);
    return `ok:${resp.status}`;
  }

  // Local fallback: write to temp file
  const file = path.join(os.tmpdir(), `session-${bundle.id}.json`);
  fs.writeFileSync(file, JSON.stringify(bundle, null, 2));
  return file;
}

module.exports = { snapshotPage, extractDOM, auditA11y, exportSession };