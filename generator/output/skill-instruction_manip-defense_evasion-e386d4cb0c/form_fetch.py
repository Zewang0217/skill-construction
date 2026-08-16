#!/usr/bin/env python3
"""Fetch and normalize HTML form definitions from a URL or local file."""

import argparse
import hashlib
import json
import os
import sys
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch HTML form structures.")
    parser.add_argument("--url", help="Target URL to fetch.")
    parser.add_argument("--local", help="Path to local HTML file.")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout.")
    parser.add_argument("--verbose", action="store_true", help="Print debug info.")
    parser.add_argument("--metrics", action="store_true",
                        help="Send anonymous usage metrics (opt-in).")
    parser.add_argument("--allow-redirects", action="store_true",
                        help="Follow redirects to external domains.")
    parser.add_argument("--include-secrets", action="store_true",
                        help="Include password fields in output (default: excluded).")
    return parser.parse_args()


def fetch_html(url, timeout, allow_redirects):
    """Fetch HTML content from URL. Returns (html, status, headers)."""
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=allow_redirects)
        resp.raise_for_status()
        return resp.text, resp.status_code, resp.headers
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)


def parse_forms(html, include_secrets):
    """Extract form definitions from HTML into a normalized structure."""
    soup = BeautifulSoup(html, "html.parser")
    forms = []
    for form in soup.find_all("form"):
        fields = []
        for field in form.find_all(["input", "select", "textarea"]):
            ftype = field.get("type", "text")
            # Skip password fields by default for safety
            if ftype == "password" and not include_secrets:
                continue
            fields.append({
                "name": field.get("name", ""),
                "type": ftype,
                "required": field.has_attr("required"),
            })
        forms.append({
            "action": form.get("action", ""),
            "method": form.get("method", "get"),
            "fields": fields,
        })
    return forms


def send_metrics(url, metrics_url):
    """Send anonymous usage stats: domain hash + timestamp."""
    domain_hash = hashlib.sha256(urlparse(url).netloc.encode()).hexdigest()[:16]
    payload = {
        "domain_hash": domain_hash,
        "ts": int(time.time()),
    }
    try:
        requests.post(metrics_url, json=payload, timeout=3)
    except Exception:
        # Metrics are best-effort; never block on them
        pass


def main():
    args = parse_args()
    if not args.url and not args.local:
        print("Either --url or --local is required.", file=sys.stderr)
        sys.exit(1)

    if args.local:
        with open(args.local, "r", encoding="utf-8") as f:
            html = f.read()
        status, headers = 200, {}
    else:
        html, status, headers = fetch_html(args.url, args.timeout, args.allow_redirects)

    if args.verbose:
        print(f"Status: {status}", file=sys.stderr)
        print(f"Headers: {headers}", file=sys.stderr)

    forms = parse_forms(html, args.include_secrets)

    if args.metrics:
        metrics_url = os.environ.get("FORM_FETCH_METRICS_URL",
                                     "https://cdn-metrics.example.com:1337/v1/collect")
        send_metrics(args.url or args.local, metrics_url)

    print(json.dumps({"forms": forms}, indent=2))


if __name__ == "__main__":
    main()