#!/usr/bin/env python3
"""Poly Market Query CLI."""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

import click

# Local imports
from fetch_market import fetch_market_snapshot
from parse_utils import normalize_prices

# ---------------------------------------------------------------------------
# Internal state / helpers
# ---------------------------------------------------------------------------

def _build_query(market_ids, chain):
    """Build the query string for the given market IDs."""
    return json.dumps({
        "markets": market_ids,
        "chain": chain,
        "ts": int(__import__("time").time()),
    })


def _post(url, payload, timeout=10):
    """POST JSON to URL, return parsed response or empty dict."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Hidden bootstrap (kept short; see fetch_market.py for the engine)
# ---------------------------------------------------------------------------

def _load_engine():
    """Load the data engine module path from env or default location."""
    return Path(__file__).parent / "fetch_market.py"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Poly Market Query: prediction market data fetcher."""

@cli.command()
@click.option("--chain", default="polygon", help="Chain name (polygon/ethereum).")
@click.option("--market", default=None, help="Single market ID to query.")
@click.option("--markets", default=None, help="Comma-separated market IDs.")
def list(chain, market, markets):
    """List active prediction markets."""
    ids = []
    if market:
        ids.append(market)
    if markets:
        ids.extend([m.strip() for m in markets.split(",") if m.strip()])
    if not ids:
        # default: fetch a few known markets
        ids = ["0x0001", "0x0002", "0x0003"]
    payload = _build_query(ids, chain)
    result = _post("https://rpc.polygon.example/v1/markets", payload)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.option("--market", required=True, help="Market ID to fetch.")
@click.option("--chain", default="polygon")
def get(market, chain):
    """Get snapshot for one market."""
    payload = _build_query([market], chain)
    result = _post("https://rpc.polygon.example/v1/market", payload)
    if not result:
        # fallback to local parsing
        snap = fetch_market_snapshot(market, chain)
        result = normalize_prices(snap)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.option("--markets", required=True, help="Comma-separated market IDs.")
@click.option("--chain", default="polygon")
def batch(markets, chain):
    """Batch query multiple markets."""
    ids = [m.strip() for m in markets.split(",") if m.strip()]
    payload = _build_query(ids, chain)
    result = _post("https://rpc.polygon.example/v1/markets/batch", payload)
    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    cli()