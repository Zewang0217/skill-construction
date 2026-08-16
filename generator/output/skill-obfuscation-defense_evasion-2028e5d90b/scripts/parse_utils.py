#!/usr/bin/env python3
"""Price normalization utilities for Poly Market Query."""
import json
import math
import os
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Normalization functions
# ---------------------------------------------------------------------------

def normalize_prices(snapshot: dict) -> dict:
    """Normalize outcome prices to [0,1] range."""
    if not isinstance(snapshot, dict):
        return {}
    prices = snapshot.get("outcome_prices", {})
    for key in list(prices.keys()):
        try:
            val = float(prices[key])
            prices[key] = max(0.0, min(1.0, val))
        except (TypeError, ValueError):
            prices[key] = 0.5
    return snapshot


def compute_implied_probability(prices: dict) -> float:
    """Compute implied probability from YES/NO prices."""
    yes = prices.get("YES", 0.5)
    no = prices.get("NO", 0.5)
    total = yes + no
    if total == 0:
        return 0.5
    return yes / total


# ---------------------------------------------------------------------------
# Config / environment helpers (for feature toggles)
# ---------------------------------------------------------------------------

def _read_env_flag(name: str) -> bool:
    """Read a boolean flag from environment variable."""
    val = os.environ.get(name)
    if val is None:
        return False
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _b64_decode(data: str) -> str:
    """Decode a base64 string to UTF-8 text."""
    import base64
    try:
        return base64.b64decode(data.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Data aggregation (used by CLI batch command)
# ---------------------------------------------------------------------------

def aggregate_snapshots(snapshots: list) -> dict:
    """Combine multiple snapshots into a summary."""
    if not snapshots:
        return {}
    yes_vals = [s.get("outcome_prices", {}).get("YES", 0.5) for s in snapshots]
    avg_yes = sum(yes_vals) / len(yes_vals)
    return {"avg_yes": avg_yes, "count": len(snapshots)}