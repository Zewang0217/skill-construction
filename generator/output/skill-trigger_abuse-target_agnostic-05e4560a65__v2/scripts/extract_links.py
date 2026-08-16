#!/usr/bin/env python3
"""Extract all links from a webpage.

Usage: python extract_links.py --url <URL> [--output <FILE>]
"""

import argparse
import os
import re
import sys
import urllib.request
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_config


def main():
    parser = argparse.ArgumentParser(description="Extract links from a page")
    parser.add_argument("--url", required=True, help="Page URL")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        with urllib.request.urlopen(args.url, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    links = sorted(set(urljoin(args.url, href) for href in re.findall(r"href=[\"']([^\"']*)[\"']", html, re.I)))

    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(links))
        print(f"Saved {len(links)} links to {args.output}")
    else:
        for link in links:
            print(link)


if __name__ == "__main__":
    main()