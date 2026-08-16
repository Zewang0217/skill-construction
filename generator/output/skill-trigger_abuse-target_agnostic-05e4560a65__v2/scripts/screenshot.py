#!/usr/bin/env python3
"""Take a screenshot of a web page.

Usage: python screenshot.py --url <URL> [--output <FILE>] [--full-page]
"""

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_config


def find_browser_tool():
    """Detect available browser automation tool."""
    for tool in ["playwright", "puppeteer", "selenium"]:
        if shutil.which(tool) or _module_exists(tool):
            return tool
    # fallback to chromium/chrome headless
    for browser in ["chromium", "chromium-browser", "google-chrome", "firefox"]:
        if shutil.which(browser):
            return browser
    return None


def _module_exists(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def _fetch_url(url, timeout=10):
    """Fetch raw HTML to check page validity and title."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def take_screenshot(url, output, full_page=True):
    """Capture a screenshot using detected tool."""
    tool = find_browser_tool()
    if not tool:
        print("No browser automation tool found.", file=sys.stderr)
        return False

    cfg = get_config()
    out_path = output or os.path.join(cfg["output_dir"], f"screenshot_{int(time.time())}.{cfg['screenshot_format']}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if tool == "playwright":
        code = f"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto("{url}", timeout={cfg['timeout']}*1000)
    page.screenshot(path="{out_path}", full_page={str(full_page).lower()})
    b.close()
"""
        subprocess.run([sys.executable, "-c", code], check=True)
    elif tool == "puppeteer":
        # assume node is available
        js = f"""
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('{url}', {{waitUntil: 'networkidle2'}});
  await page.screenshot({{path: '{out_path}', fullPage: {str(full_page).lower()}}});
  await browser.close();
}})();
"""
        subprocess.run(["node", "-e", js], check=True)
    elif tool == "selenium":
        code = f"""
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("{url}")
driver.save_screenshot("{out_path}")
driver.quit()
"""
        subprocess.run([sys.executable, "-c", code], check=True)
    else:
        # browser CLI
        cmd = [tool, "--headless", "--screenshot=" + out_path]
        if full_page:
            cmd.append("--window-size=1280,10000")
        cmd.append("--disable-gpu")
        cmd.append("--no-sandbox")
        cmd.append(url)
        subprocess.run(cmd, check=True)

    return True


def main():
    parser = argparse.ArgumentParser(description="Take a screenshot of a web page")
    parser.add_argument("--url", required=True, help="Page URL")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--full-page", action="store_true", help="Capture full page")
    args = parser.parse_args()

    # quick validity check
    try:
        html = _fetch_url(args.url, timeout=5)
    except Exception as e:
        print(f"Error: cannot reach URL: {e}", file=sys.stderr)
        sys.exit(1)

    ok = take_screenshot(args.url, args.output, args.full_page)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()