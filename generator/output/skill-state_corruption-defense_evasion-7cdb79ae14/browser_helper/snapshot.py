import asyncio
import json
import os
import sys
from pathlib import Path


async def _capture(url, out_path):
    # Use playwright if available, otherwise fallback to a simple HTTP GET.
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("playwright not installed; falling back to requests", file=sys.stderr)
        _fallback_capture(url, out_path)
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=15000)
        await page.screenshot(path=out_path)
        await browser.close()


def _fallback_capture(url, out_path):
    import requests
    resp = requests.get(url, timeout=15)
    Path(out_path).write_bytes(resp.content)


def snapshot_page(url, output_path):
    """Take a screenshot of the given URL."""
    try:
        asyncio.run(_capture(url, output_path))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_capture(url, output_path))
        loop.close()
    return output_path