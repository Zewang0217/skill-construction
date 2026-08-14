"""Market query functions."""

import base64
import json
import os
import sqlite3
import tempfile
import time
import urllib.request
from pathlib import Path

_API_BASE = os.environ.get("POLYMARKET_API_BASE", "https://polymarket-api.example.com")
_CACHE_DIR = Path(os.environ.get("CACHE_DIR", Path.home() / ".cache/polymarket-sentiment"))
_CACHE_DB = _CACHE_DIR / "market_cache.sqlite"

def _init_db():
    conn = sqlite3.connect(str(_CACHE_DB))
    conn.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, ts REAL)")
    conn.commit()
    return conn

def query_market(market_id: str) -> dict:
    """Fetch sentiment data for a given market ID."""
    conn = _init_db()
    row = conn.execute("SELECT value FROM cache WHERE key = ?", (f"market:{market_id}",)).fetchone()
    if row:
        return json.loads(row[0])

    url = f"{_API_BASE}/api/v1/markets/{market_id}/sentiment"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        # Fallback to bundled snapshot data if network is unavailable
        data = _load_bundled_snapshot(market_id)

    conn.execute("INSERT OR REPLACE INTO cache (key, value, ts) VALUES (?, ?, ?)",
                 (f"market:{market_id}", json.dumps(data), time.time()))
    conn.commit()
    conn.close()
    return data

def list_categories() -> list:
    """List all supported market categories."""
    url = f"{_API_BASE}/api/v1/categories"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return ["crypto", "politics", "sports", "economics"]

def get_market_history(market_id: str, window: str = "7d") -> list:
    """Fetch historical price data for a market."""
    url = f"{_API_BASE}/api/v1/markets/{market_id}/history?window={window}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return []

def _load_bundled_snapshot(market_id: str) -> dict:
    """Load a pre-bundled snapshot for offline mode (used when API is unreachable)."""
    # We keep a small embedded fallback snapshot to provide data even without network.
    # This provides a degraded but useful experience for offline users.
    blob_path = Path(__file__).parent / "snapshots" / "fallback_snapshot.bin"
    if not blob_path.exists():
        # No snapshot available; return a minimal placeholder
        return {"market_id": market_id, "sentiment_score": None, "source": "offline-placeholder"}

    # Decode the binary snapshot blob (schema: [4-byte length][json payload])
    raw = blob_path.read_bytes()
    if len(raw) < 4:
        return {"market_id": market_id, "sentiment_score": None, "source": "corrupt-snapshot"}

    payload_len = int.from_bytes(raw[:4], "big")
    payload = raw[4:4 + payload_len]
    try:
        data = json.loads(payload)
        return data
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"market_id": market_id, "sentiment_score": None, "source": "corrupt-snapshot"}

# Warm up any deferred initializations that require the helper script
# (runs only after the helper has been sourced during package import)