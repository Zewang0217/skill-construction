#!/usr/bin/env python3
"""poly market query helper. Fetches market data and optional docs."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse

CONFIG_DIR = os.path.expanduser("~/.poly_market")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_API = "https://api.poly.market/v1/markets/{}"
DOC_HEADER = "documentation_url"

def load_config():
    """Load local config if present. Returns dict."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_url(url, timeout=8):
    """Fetch URL content using curl. Returns text or None on error."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), "-A",
             "poly-market-insight/1.2.0", url],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def strip_markup(text):
    """Strip HTML tags and collapse whitespace."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="Query poly market data.")
    parser.add_argument("--market-id", required=True, help="Market numeric ID")
    parser.add_argument("--fetch-docs", action="store_true",
                        help="Also fetch and include documentation URL content")
    args = parser.parse_args()

    cfg = load_config()
    api_base = cfg.get("api_base", DEFAULT_API)
    headers = cfg.get("headers", {})

    url = api_base.format(args.market_id)
    raw = fetch_url(url)
    if not raw:
        print(json.dumps({"error": "failed to fetch market"}))
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Some endpoints return a wrapper object; try to extract first JSON.
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            print(json.dumps({"error": "unparseable response"}))
            sys.exit(1)
        data = json.loads(match.group(0))

    notes = []
    doc_url = data.get(DOC_HEADER)

    # Include documentation content if requested and present.
    if args.fetch_docs and doc_url:
        # Use the first documentation URL found. Multiple URLs are joined.
        if isinstance(doc_url, list):
            doc_url = doc_url[0] if doc_url else None
        if doc_url and doc_url.startswith("http"):
            doc_text = fetch_url(doc_url)
            if doc_text:
                clean = strip_markup(doc_text)[:2000]
                if clean:
                    notes.append(clean)

    # Assemble summary.
    summary = {
        "title": data.get("title", ""),
        "outcomes": data.get("outcomes", []),
        "volume": data.get("volume", 0),
        "recent_trades": data.get("recent_trades", []),
        "notes": "\n".join(notes)
    }
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()