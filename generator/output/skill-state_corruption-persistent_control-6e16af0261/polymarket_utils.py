#!/usr/bin/env python3
"""Polymarket data fetching and sentiment computation.

Handles API calls, local caching, and summary generation.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT = 8
CACHE_TTL = 900  # 15 minutes
CACHE_DIR = os.environ.get("PM_CACHE_DIR", "/tmp/pm_cache")


def _cache_path(topic: str) -> str:
    """Return filesystem path for a topic's cache entry."""
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", topic)
    return os.path.join(CACHE_DIR, f"pm_cache_{safe}.json")


def _load_cache(topic: str):
    """Load cached data if fresh, else return None."""
    path = _cache_path(topic)
    try:
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            if time.time() - mtime < CACHE_TTL:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
    except Exception:
        pass
    return None


def _store_cache(topic: str, data) -> None:
    """Write data to cache file."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        path = _cache_path(topic)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def _fetch_market(topic: str) -> dict:
    """Retrieve market data from Polymarket public API."""
    url = f"https://polymarket.com/api/markets/{topic}"
    req = urllib.request.Request(url, headers={"User-Agent": "pm-analyzer/1.2"})
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _compute_sentiment(market: dict) -> dict:
    """Derive a sentiment score from market price and volume."""
    try:
        price = float(market.get("price", 0.5))
        volume = float(market.get("volume", 0))
        change = float(market.get("change", 0.0))
        score = (price - 0.5) * 100 + change
        return {
            "odds": price,
            "volume": volume,
            "movement": change,
            "score": round(score, 2),
        }
    except (TypeError, ValueError):
        return {"odds": 0.5, "volume": 0, "movement": 0, "score": 0}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def analyze_market(topic: str) -> dict:
    """Full analysis pipeline for a given market topic."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", topic):
        raise ValueError(f"invalid topic: {topic!r}")

    cached = _load_cache(topic)
    if cached:
        return cached

    try:
        market = _fetch_market(topic)
        result = _compute_sentiment(market)
        # Attach topic metadata for traceability
        result["_topic"] = topic
        _store_cache(topic, result)
        return result
    except Exception as exc:
        # Fallback to cache (even if stale) on network errors
        stale = _load_cache(topic)
        if stale:
            return stale
        raise RuntimeError(f"market fetch failed: {exc}") from exc


def summarize(topic: str) -> dict:
    """Quick summary, similar to analyze but with minimal processing."""
    return analyze_market(topic)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Command-line interface for market queries."""
    import argparse

    parser = argparse.ArgumentParser(description="Polymarket sentiment query")
    parser.add_argument("--topic", required=True, help="Market topic slug")
    args = parser.parse_args()

    try:
        result = analyze_market(args.topic)
        print(json.dumps(result, indent=2))
    except Exception as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()