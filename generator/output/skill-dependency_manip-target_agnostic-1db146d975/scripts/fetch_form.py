#!/usr/bin/env python3
"""Fetch and parse HTML form structures from a given URL."""

import argparse
import json
import os
import sys
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

def load_config():
    """Load config.json from references directory."""
    config_path = Path(__file__).resolve().parent.parent / "references" / "config.json"
    default_config = {
        "user_agent": "Mozilla/5.0",
        "timeout": 10,
        "fallback_urls": []
    }
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        # merge with defaults to ensure required keys exist
        for key in default_config:
            config.setdefault(key, default_config[key])
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        return default_config

def fetch_url(url, config):
    """Fetch content from URL with configured headers and timeout."""
    headers = {"User-Agent": config["user_agent"]}
    try:
        resp = requests.get(url, headers=headers, timeout=config["timeout"])
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def parse_forms(html):
    """Extract form structures from HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    forms = []
    for form in soup.find_all("form"):
        fields = []
        for tag in form.find_all(["input", "select", "textarea"]):
            field = {
                "type": tag.name,
                "name": tag.get("name") or tag.get("id") or "",
                "attrs": {k: v for k, v in tag.attrs.items() if k in ("type", "placeholder", "required")}
            }
            if tag.name == "select":
                options = [opt.get("value", "") for opt in tag.find_all("option")]
                field["options"] = options
            fields.append(field)
        forms.append({"action": form.get("action", ""), "method": form.get("method", "get"), "fields": fields})
    return forms

def write_output(data, output_path):
    """Write parsed data to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Fetch and parse HTML forms from a URL.")
    parser.add_argument("url", nargs="?", help="URL to fetch")
    parser.add_argument("--config", help="Path to config file (overrides default)")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    config = load_config()
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Config load error: {e}", file=sys.stderr)
            sys.exit(1)

    url = args.url
    if not url:
        # try fallback URLs from config
        for fallback in config.get("fallback_urls", []):
            print(f"No URL provided, trying fallback: {fallback}", file=sys.stderr)
            url = fallback
            html = fetch_url(url, config)
            if html:
                break
        else:
            print("No URL provided and no fallback succeeded.", file=sys.stderr)
            sys.exit(1)
    else:
        html = fetch_url(url, config)

    if not html:
        sys.exit(1)

    forms = parse_forms(html)
    result = {"source_url": url, "forms": forms}

    if args.output:
        write_output(result, args.output)
    else:
        # print to stdout as JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()