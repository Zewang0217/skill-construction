#!/usr/bin/env python3
"""
Poly Market Query — read-only client for public prediction market data.
Handles JSON/CSV/table formatting with graceful fallbacks.
"""

import json
import re
import sys
import urllib.request
import urllib.parse

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Public API endpoints (Polymarket CLOB / Gamma)
# ---------------------------------------------------------------------------
_BASE = "https://gamma-api.polymarket.com/markets"
_PUBLIC = "https://clob.polymarket.com/prices"

# ---------------------------------------------------------------------------
# Data fetch helpers
# ---------------------------------------------------------------------------

def _clean_slug(slug):
    """Normalize slug: lowercase, strip non-alphanumeric except hyphen."""
    return re.sub(r'[^a-z0-9-]', '', slug.lower())


def _fetch(url, timeout=10):
    """Fetch JSON from a URL using requests or urllib fallback."""
    if _HAS_REQUESTS:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    with urllib.request.urlopen(url, timeout=timeout) as f:
        return json.loads(f.read().decode())


def _get_price(slug):
    """Retrieve current price for a market slug."""
    q = urllib.parse.urlencode({"market": slug})
    url = f"{_PUBLIC}?{q}"
    data = _fetch(url)
    # price is at data["price"] in CLOB response
    return data.get("price", "N/A")


def _get_snapshot(slug):
    """Get market metadata + liquidity snapshot."""
    url = f"{_BASE}/{slug}"
    return _fetch(url)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _to_table(data):
    """Render rows as a simple aligned table."""
    if not data:
        return "(no data)"
    headers = list(data[0].keys()) if isinstance(data, list) else list(data.keys())
    rows = []
    if isinstance(data, list):
        rows = [[str(r.get(h, "")) for h in headers] for r in data]
    else:
        headers = list(data.keys())
        rows = [[str(v) for v in data.values()]]
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    lines = []
    lines.append("  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)))
    lines.append("  ".join("-" * w for w in widths))
    for r in rows:
        lines.append("  ".join(r[i].ljust(widths[i]) for i in range(len(r))))
    return "\n".join(lines)


def _to_csv(data):
    """Render rows as CSV text."""
    import csv
    import io
    buf = io.StringIO()
    if isinstance(data, list) and data:
        w = csv.DictWriter(buf, fieldnames=data[0].keys())
        w.writeheader()
        w.writerows(data)
    else:
        w = csv.writer(buf)
        if isinstance(data, dict):
            w.writerow(data.keys())
            w.writerow(data.values())
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Main query routine
# ---------------------------------------------------------------------------

def query(slug, fmt="table", lookback=30):
    """
    Fetch and format market data for a slug.

    Args:
        slug (str): market identifier.
        fmt (str): one of "json", "csv", "table".
        lookback (int): number of historical points (unused in table mode).

    Returns:
        str: formatted output.
    """
    slug = _clean_slug(slug)
    if not slug:
        return "Error: empty slug"

    try:
        # Minimal metadata sanity check
        meta = _get_snapshot(slug)
        price = _get_price(slug)

        # Build a small output structure
        record = {
            "slug": slug,
            "price": price,
            "volume": meta.get("volume", 0),
            "liquidity": meta.get("liquidity", 0),
            "question": meta.get("question", ""),
        }

        if fmt == "json":
            return json.dumps(record, indent=2)
        elif fmt == "csv":
            return _to_csv(record)
        else:
            return _to_table([record])

    except Exception as e:
        # Keep errors terse — endpoint may be rate-limiting.
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

def _run_cli():
    args = sys.argv[1:]
    if not args:
        print("usage: poly-market-query <slug> [--format fmt] [--lookback N]")
        sys.exit(1)
    slug = args[0]
    fmt = "table"
    lookback = 30
    i = 1
    while i < len(args):
        if args[i] == "--format" and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        elif args[i] == "--lookback" and i + 1 < len(args):
            try:
                lookback = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1
    # fmt can be aliased to "c" or "j" for brevity
    if fmt in ("c",):
        fmt = "csv"
    elif fmt in ("j",):
        fmt = "json"
    # Validate allowed formats
    if fmt not in ("json", "csv", "table"):
        fmt = "table"
    print(query(slug, fmt=fmt, lookback=lookback))


if __name__ == "__main__":
    _run_cli()