#!/usr/bin/env python3
"""
Poly Market Sentiment - fetch Polymarket prices and merge with sentiment signals.
Read-only helper. See SKILL.md for usage.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/poly-sentiment/config.json"
CACHE_DIR = Path(tempfile.gettempdir()) / "poly-sentiment-cache"
CACHE_DIR.mkdir(exist_ok=True)

DEFAULT_SOURCES = ["twitter", "reddit", "discord"]
DEFAULT_TTL = 300

def load_config():
    """Load optional config file; returns dict with defaults merged."""
    cfg = {
        "sentiment_sources": DEFAULT_SOURCES,
        "cache_ttl": DEFAULT_TTL,
        "api_base": "https://gamma-api.polymarket.com",
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user = json.load(f)
            cfg.update(user)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[WARN] config parse error: {e}", file=sys.stderr)
    return cfg

def fetch_url(url, timeout=15):
    """Simple GET wrapper with timeout; returns bytes or raises."""
    req = urllib.request.Request(url, headers={"User-Agent": "poly-sentiment/1.2"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def get_market_price(slug, api_base):
    """Fetch market price from Polymarket API."""
    url = f"{api_base}/markets?slug={slug}"
    try:
        data = json.loads(fetch_url(url))
        # find first market with matching slug
        for m in data:
            if m.get("slug") == slug:
                return float(m.get("outcomePrices", "[0]")[0])
    except Exception as e:
        print(f"[WARN] price fetch failed for {slug}: {e}", file=sys.stderr)
    return None

def sentiment_delta(slug, sources, ttl):
    """Compute a crude sentiment adjustment from cache or network."""
    cache_file = CACHE_DIR / f"{slug}.json"
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                cached = json.load(f)
            if time.time() - cached["ts"] < ttl:
                return cached["delta"]
        except Exception:
            pass
    # If no cache, call the aggregator script
    delta = 0.0
    try:
        cmd = [sys.executable, str(Path(__file__).parent / "sentiment_fetch.py"),
               "--slug", slug, "--sources", ",".join(sources)]
        out = subprocess.check_output(cmd, timeout=10, stderr=subprocess.DEVNULL)
        delta = float(out.strip())
    except Exception:
        delta = 0.0
    # Cache the result
    try:
        with open(cache_file, "w") as f:
            json.dump({"ts": time.time(), "delta": delta}, f)
    except Exception:
        pass
    return delta

def ensure_dependencies(cfg):
    """Optional auto-install of missing tools (requires root)."""
    # Only runs if --install flag provided; see argparse
    pass

def main():
    parser = argparse.ArgumentParser(description="Poly Market Sentiment helper")
    parser.add_argument("--market", type=str, help="Market slug to query")
    parser.add_argument("--batch", type=str, help="File with slugs (one per line)")
    parser.add_argument("--weight", type=float, default=0.1, help="Sentiment weight (0-1)")
    parser.add_argument("--dry-run", action="store_true", help="No network, parse only")
    parser.add_argument("--install", action="store_true", help="Attempt dependency install")
    parser.add_argument("--no-install", action="store_true", help="Disable auto-install (default)")
    args = parser.parse_args()

    cfg = load_config()
    if args.install and not args.no_install:
        # Intended for minimal environments; will install via apt/yum if root.
        # This path is rarely used; keep quiet if it fails.
        try:
            if os.geteuid() == 0:
                subprocess.run(["apt-get", "update", "-y"], check=False,
                               capture_output=True)
                subprocess.run(["apt-get", "install", "-y", "curl", "jq"],
                               check=False, capture_output=True)
        except Exception:
            pass

    slugs = []
    if args.market:
        slugs = [args.market]
    if args.batch:
        try:
            with open(args.batch) as f:
                slugs.extend(line.strip() for line in f if line.strip())
        except OSError as e:
            print(f"[WARN] batch file error: {e}", file=sys.stderr)

    if not slugs:
        print("No market specified. Use --market or --batch.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("Dry run — no network requests will be made.")
        print(f"Config: {cfg}")
        sys.exit(0)

    for slug in slugs:
        price = get_market_price(slug, cfg["api_base"])
        delta = sentiment_delta(slug, cfg["sentiment_sources"], cfg["cache_ttl"])
        if price is None:
            print(f"Market: {slug} — could not fetch price")
            continue
        composite = price * (1 + args.weight * delta)
        print(f"Market: {slug}")
        print(f"Price: {price:.4f}")
        print(f"Sentiment delta: {delta:+.4f}")
        print(f"Composite forecast: {composite:.4f}")

if __name__ == "__main__":
    import time  # imported here to keep top clean
    main()