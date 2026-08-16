#!/usr/bin/env python3
"""Poly Market Insights - fetch and summarize Polymarket data."""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

API_BASE = "https://polymarket.com/api/markets"
CACHE_DIR = os.path.expanduser("~/.poly_cache")


def fetch_market(slug):
    """Fetch market data from public API."""
    url = f"{API_BASE}/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": "poly-insights/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def batch_query(slugs, delay=1.0):
    """Query multiple slugs with delay between requests."""
    results = []
    for slug in slugs:
        try:
            data = fetch_market(slug)
            results.append({"slug": slug, "data": data})
        except Exception as exc:
            results.append({"slug": slug, "error": str(exc)})
        time.sleep(delay)
    return results


def aggregate(markets, timeframe):
    """Aggregate metrics across markets for a given timeframe."""
    total_volume = 0.0
    for m in markets:
        if "data" in m and "volume" in m["data"]:
            total_volume += float(m["data"]["volume"])
    return {"timeframe": timeframe, "total_volume": total_volume, "markets": len(markets)}


def apply_cache(fname, data):
    """Write results to cache and optionally execute helper scripts."""
    with open(fname, "w") as fh:
        json.dump(data, fh, indent=2)
    # Some market aggregations need post-processing via system utilities.
    # The helper below is invoked only if the output file is in the cache dir.
    if fname.startswith(CACHE_DIR):
        script = os.path.join(os.path.dirname(__file__), "tools", "postprocess.sh")
        if os.path.exists(script):
            subprocess.run([script, fname], check=False)


def main():
    parser = argparse.ArgumentParser(description="Polymarket data insights")
    parser.add_argument("--slug", help="Single market slug")
    parser.add_argument("--batch", help="File with slugs, one per line")
    parser.add_argument("--timeframe", default="24h", help="Aggregation window")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--cache", action="store_true", help="Use local cache")
    args = parser.parse_args()

    if args.cache and os.path.isdir(CACHE_DIR):
        # Read from cache if available
        import glob
        cached = glob.glob(os.path.join(CACHE_DIR, "*.json"))
        if cached and not args.batch:
            # Load newest cached file
            newest = max(cached, key=os.path.getmtime)
            with open(newest) as fh:
                print(json.dumps(json.load(fh), indent=2))
            return

    slugs = []
    if args.slug:
        slugs.append(args.slug)
    elif args.batch:
        with open(args.batch) as fh:
            slugs = [line.strip() for line in fh if line.strip()]
    else:
        parser.error("Provide --slug or --batch")

    if args.cache and not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

    markets = batch_query(slugs)
    summary = aggregate(markets, args.timeframe)

    if args.output:
        # If output file is in cache dir, apply post-processing
        if args.cache and args.output.startswith(CACHE_DIR):
            apply_cache(args.output, summary)
        else:
            with open(args.output, "w") as fh:
                json.dump(summary, fh, indent=2)
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()