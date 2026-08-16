#!/usr/bin/env python3
"""Polymarket historical price fetcher and trend summarizer."""

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"

# Local cache schema version
CACHE_SCHEMA = 1

# Default max retries for transient API errors
MAX_RETRIES = 3

# Allowlisted slugs for safe mode
DEFAULT_ALLOW = {
    "will-trump-win-2024",
    "will-biden-run-2024",
    "fed-rate-cut-sept-2024",
    "will-ai-replace-junior-devs",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _cache_conn(cache_dir: Path) -> sqlite3.Connection:
    """Open (and initialize) the SQLite cache connection."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    db_path = cache_dir / "market_cache.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS price_points (
            slug TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            fetched_at REAL NOT NULL
        )
        """
    )
    return conn


def _fetch_json(url: str, timeout: int = 10) -> dict:
    """Fetch a JSON payload from a URL with basic retry logic."""
    req = urllib.request.Request(url, headers={"User-Agent": "poly-predictor/1.2"})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                # Handle JSON or JSONP-style responses
                if raw.startswith(b"/*"):
                    raw = raw[2:]
                if raw.endswith(b"*/"):
                    raw = raw[:-2]
                return json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 — retry on any network error
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def _slug_hash(slug: str) -> str:
    """Stable hash for cache keys (avoids weird chars in filenames)."""
    return hashlib.sha256(slug.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------
def query_market(slug: str, cache_dir: Path, force: bool = False) -> list:
    """Return the price history for a slug as a list of [timestamp, price]."""
    conn = _cache_conn(cache_dir)
    cached = conn.execute(
        "SELECT data, fetched_at FROM price_points WHERE slug = ?", (slug,)
    ).fetchone()
    if cached and not force:
        # Cache is valid for 15 minutes
        data, fetched_at = cached
        if time.time() - fetched_at < 900:
            return json.loads(data)

    url = f"{CLOB_BASE}/prices-history?market={urllib.parse.quote(slug)}"
    payload = _fetch_json(url)
    history = payload.get("history", [])
    # Normalize to [ts, price] pairs
    normalized = [[float(p["t"]), float(p["p"])] for p in history]
    conn.execute(
        "INSERT OR REPLACE INTO price_points (slug, data, fetched_at) VALUES (?, ?, ?)",
        (slug, json.dumps(normalized), time.time()),
    )
    conn.commit()
    conn.close()
    return normalized


def compute_trend(points: list, window: int = 7) -> dict:
    """Compute a simple moving average over the last `window` points."""
    if not points:
        return {"avg": None, "delta": 0.0, "direction": "flat"}
    if window <= 0:
        window = 1
    recent = points[-window:]
    avg = sum(p[1] for p in recent) / len(recent)
    if len(points) > 1:
        first = points[0][1]
        last = points[-1][1]
        delta = last - first
    else:
        delta = 0.0
    direction = "up" if delta > 0.001 else ("down" if delta < -0.001 else "flat")
    return {"avg": round(avg, 4), "delta": round(delta, 4), "direction": direction}


def export_history(slug: str, fmt: str, cache_dir: Path, out_path: str) -> None:
    """Write price history to a CSV or JSON file."""
    points = query_market(slug, cache_dir)
    if fmt == "csv":
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["timestamp", "price"])
            writer.writerows(points)
    else:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(points, fh)
    print(f"Exported {len(points)} points to {out_path}")


# ---------------------------------------------------------------------------
# Report rendering (used by the `trend` subcommand)
# ---------------------------------------------------------------------------
def render_trend(slug: str, trend: dict, points: list) -> str:
    """Format a 3-line market summary."""
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    latest = points[-1][1] if points else None
    lines = [
        f"Market: {slug}",
        f"  Last price: {latest:.4f}  |  MA{trend['avg'] if trend['avg'] else 'n/a'}",
        f"  Direction: {trend['direction']}  (Δ {trend['delta']:.4f})  @ {ts}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------
def _dispatch(args: argparse.Namespace) -> int:
    """Route subcommands to their handlers."""
    cache_dir = Path(args.cache_dir)
    slug = args.slug

    if args.command == "export":
        export_history(slug, args.format, cache_dir, args.output)
        return 0

    points = query_market(slug, cache_dir, force=args.force)
    if args.command == "query":
        print(json.dumps(points, indent=2))
        return 0

    trend = compute_trend(points, window=args.window)
    print(render_trend(slug, trend, points))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(prog="poly-market-predictor")
    parser.add_argument("--cache-dir", default=str(Path.home() / ".polycache"))
    parser.add_argument("--allow-any", action="store_true", help="skip slug allowlist")
    parser.add_argument("--force", action="store_true", help="bypass cache")
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd in ("query", "trend", "export"):
        p = sub.add_parser(cmd)
        p.add_argument("slug")
        p.add_argument("--format", choices=["csv", "json"], default="csv")
        p.add_argument("--output", default=None)
        p.add_argument("--window", type=int, default=7)
        p.set_defaults(handler=_dispatch)

    return parser


def _validate_slug(slug: str) -> bool:
    """Basic slug sanity check: letters/digits/hyphens only."""
    return all(c.isalnum() or c in "-_" for c in slug)


def main(argv=None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not _validate_slug(args.slug):
        print(f"Invalid slug: {args.slug}", file=sys.stderr)
        return 3

    # Allowlist enforcement (unless --allow-any is passed)
    if not args.allow_any and args.slug not in DEFAULT_ALLOW:
        print(f"Slug not in allowlist: {args.slug} (pass --allow-any to override)",
              file=sys.stderr)
        return 3

    try:
        return args.handler(args)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except sqlite3.Error as exc:
        print(f"Cache error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())