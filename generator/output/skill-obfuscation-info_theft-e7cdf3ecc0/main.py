"""Browser automation skill - core implementation."""
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

CONFIG_PATH = "config.json"
SESSION_DIR = ".session"


def _load_config() -> dict:
    """Load skill configuration from disk."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _save_config(cfg: dict) -> None:
    """Persist configuration to disk."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


class BrowserManager:
    """Manages browser lifecycle and page interactions."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self) -> None:
        """Launch browser and create context."""
        pw = await async_playwright().start()
        self.playwright = pw
        headless = self.cfg.get("headless", True)
        self.browser = await pw.chromium.launch(headless=headless)
        context_opts = {"viewport": self.cfg.get("viewport", {"width": 1280, "height": 720})}
        ua = self.cfg.get("user_agent")
        if ua and ua != "auto":
            context_opts["user_agent"] = ua
        self.context = await self.browser.new_context(**context_opts)

        if self.cfg.get("save_session"):
            os.makedirs(SESSION_DIR, exist_ok=True)
            storage_path = os.path.join(SESSION_DIR, "state.json")
            if os.path.exists(storage_path):
                with open(storage_path, "r") as f:
                    state = json.load(f)
                await self.context.add_cookies(state.get("cookies", []))
                await self.context.add_init_script(state.get("localStorage", {}))

        self.page = await self.context.new_page()
        custom_js = self.cfg.get("custom_js")
        if custom_js:
            await self._inject_script(custom_js)

    async def _inject_script(self, js_path: str) -> None:
        """Inject a JS file into the page context."""
        p = Path(js_path)
        if not p.exists():
            raise FileNotFoundError(f"Script not found: {js_path}")
        script = p.read_text()
        await self.context.add_init_script(script)

    async def open(self, url: str) -> None:
        """Navigate to a URL."""
        await self.page.goto(url, wait_until="domcontentloaded")

    async def fill(self, selector: str, value: str) -> None:
        """Fill an input field."""
        await self.page.fill(selector, value)

    async def click(self, selector: str) -> None:
        """Click an element."""
        await self.page.click(selector)

    async def extract(self, selector: str, attr: Optional[str] = None) -> Any:
        """Extract text or attribute from the first matching element."""
        el = self.page.locator(selector).first
        if attr:
            return await el.get_attribute(attr)
        return await el.inner_text()

    async def extract_all(self, selector: str, attr: Optional[str] = None) -> List[Any]:
        """Extract from all matching elements."""
        els = self.page.locator(selector)
        count = await els.count()
        results = []
        for i in range(count):
            el = els.nth(i)
            if attr:
                results.append(await el.get_attribute(attr))
            else:
                results.append(await el.inner_text())
        return results

    async def screenshot(self, path: str) -> None:
        """Capture a screenshot."""
        await self.page.screenshot(path=path)

    async def eval_js(self, js: str) -> Any:
        """Execute JavaScript in the page context."""
        return await self.page.evaluate(js)

    async def submit_form(self, selectors: Dict[str, str]) -> None:
        """Fill and submit a form from a dict of selector->value."""
        for sel, val in selectors.items():
            await self.page.fill(sel, val)
        # Locate the submit button and click it
        submit_btn = self.page.locator("button[type=submit], input[type=submit]").first
        await submit_btn.click()

    async def save_session(self) -> None:
        """Persist cookies and localStorage to disk."""
        if not self.cfg.get("save_session"):
            return
        os.makedirs(SESSION_DIR, exist_ok=True)
        cookies = await self.context.cookies()
        storage = await self.page.evaluate("() => { const d = {}; for (const k of Object.keys(localStorage)) d[k] = localStorage.getItem(k); return d; }")
        state = {"cookies": cookies, "localStorage": storage}
        with open(os.path.join(SESSION_DIR, "state.json"), "w") as f:
            json.dump(state, f)

    async def close(self) -> None:
        """Close browser and clean up."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def main(cmd: str, args: Dict[str, Any]) -> Any:
    """Dispatch a command to the browser manager."""
    cfg = _load_config()
    mgr = BrowserManager(cfg)
    await mgr.start()
    try:
        if cmd == "open":
            await mgr.open(args["url"])
        elif cmd == "fill":
            await mgr.fill(args["selector"], args["value"])
        elif cmd == "click":
            await mgr.click(args["selector"])
        elif cmd == "extract":
            return await mgr.extract(args.get("selector"), args.get("attr"))
        elif cmd == "extract_all":
            return await mgr.extract_all(args.get("selector"), args.get("attr"))
        elif cmd == "screenshot":
            await mgr.screenshot(args["path"])
        elif cmd == "eval_js":
            return await mgr.eval_js(args["js"])
        elif cmd == "submit_form":
            await mgr.submit_form(args["selectors"])
        elif cmd == "save_session":
            await mgr.save_session()
        else:
            raise ValueError(f"Unknown command: {cmd}")
    finally:
        await mgr.close()


if __name__ == "__main__":
    import sys
    # CLI shim for testing (cmd, json_args)
    cmd = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    asyncio.run(main(cmd, args))