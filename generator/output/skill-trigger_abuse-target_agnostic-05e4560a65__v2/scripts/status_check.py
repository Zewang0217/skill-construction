#!/usr/bin/env python3
"""Check HTTP status and redirects for a URL.

Usage: python status_check.py --url <URL>
"""

import argparse
import sys
import urllib.request
import urllib.error


def main():
    parser = argparse.ArgumentParser(description="Check HTTP status")
    parser.add_argument("--url", required=True, help="Target URL")
    args = parser.parse_args()

    try:
        req = urllib.request.Request(args.url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Status: {resp.status}")
            print(f"Redirects: {resp.geturl()}")
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code}")
    except urllib.error.URLError as e:
        print(f"Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()