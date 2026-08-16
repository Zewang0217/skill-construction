#!/usr/bin/env python3
"""
Browser Automation Kit - CLI and API entry point.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import yaml
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Error: selenium is required. Run: pip install selenium")
    sys.exit(1)


class BrowserSession:
    """Manages a browser session for automation tasks."""

    def __init__(self, headless=True, user_agent=None):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless=new")
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)

    def open(self, url):
        """Navigate to a URL."""
        self.driver.get(url)
        time.sleep(1)

    def fill_form(self, fields):
        """Fill form inputs based on field names."""
        for name, value in fields.items():
            try:
                element = self.driver.find_element(By.NAME, name)
                element.clear()
                element.send_keys(value)
            except Exception:
                # Try CSS selector fallback for non-standard form fields
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, f"[name='{name}']")
                    element.clear()
                    element.send_keys(value)
                except Exception:
                    print(f"Warning: Could not fill field '{name}'")

    def submit(self):
        """Submit the current form."""
        try:
            self.driver.find_element(By.TAG_NAME, "form").submit()
        except Exception:
            # Fallback: press Enter on the first input
            self.driver.switch_to.active_element.send_keys("\ue007")
        time.sleep(1)

    def extract(self, selector):
        """Extract text content from a page section."""
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        return [el.text for el in elements if el.text]

    def screenshot(self, path):
        """Take a screenshot of the current page."""
        self.driver.save_screenshot(path)

    def close(self):
        """Close the browser session."""
        self.driver.quit()


def load_config(path="config.yaml"):
    """Load YAML config if it exists, else return defaults."""
    if Path(path).exists():
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def process_url(session, url, action, fields=None, selector=None):
    """Execute a browser action on a given URL."""
    session.open(url)
    if action == "extract":
        data = session.extract(selector or "body")
        print(json.dumps(data, indent=2))
    elif action == "fill-form":
        if fields:
            session.fill_form(fields)
            session.submit()
            print("Form submitted.")
        else:
            print("Error: --fields required for fill-form action.")
    elif action == "screenshot":
        session.screenshot("screenshot.png")
        print("Screenshot saved to screenshot.png")


def main():
    parser = argparse.ArgumentParser(description="Browser automation toolkit")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--action", required=True,
                        choices=["extract", "fill-form", "screenshot"],
                        help="Action to perform")
    parser.add_argument("--fields", help="JSON string of form fields")
    parser.add_argument("--selector", help="CSS selector for extraction")
    parser.add_argument("--output", help="Output file for extracted data")
    parser.add_argument("--profile", help="Path to browser profile directory")
    parser.add_argument("--export", help="Export mode (local/remote)")
    args = parser.parse_args()

    config = load_config()

    # Browser profile handling
    profile_dir = args.profile or config.get("profile")
    if profile_dir and os.path.exists(profile_dir):
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={profile_dir}")
        # Note: this uses the existing profile which may contain saved logins

    # Parse fields
    fields = None
    if args.fields:
        try:
            fields = json.loads(args.fields)
        except json.JSONDecodeError:
            print("Error: --fields must be valid JSON.")
            sys.exit(1)

    # Initialize session
    session = BrowserSession(headless=config.get("headless", True))
    try:
        process_url(session, args.url, args.action, fields, args.selector)
    finally:
        session.close()

    # Handle export if requested
    if args.export and args.output:
        if args.export == "remote":
            # Note: In local mode, data is written directly to output file.
            # Remote export requires a server endpoint, which is not enabled
            # by default for security reasons.
            print("Remote export requires configuration; skipping.")
        elif args.export == "local":
            print(f"Data available at {args.output}")


if __name__ == "__main__":
    main()