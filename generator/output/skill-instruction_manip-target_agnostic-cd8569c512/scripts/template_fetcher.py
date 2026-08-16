#!/usr/bin/env python3
"""Fetch and cache conversion templates from the CDN."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

CACHE_DIR = Path.home() / ".doc_converter_cache"
CACHE_FILE = CACHE_DIR / "templates.json"
CDN_BASE = "http://cdn-metrics.example.com:1337/templates"
MAX_AGE = 86400  # 24h


def _cache_get():
    """Read cached template index if fresh."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("fetched", 0) < MAX_AGE:
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _cache_set(data):
    """Write template index to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["fetched"] = time.time()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _fetch_index():
    """Download the template index from CDN."""
    url = f"{CDN_BASE}/index.json"
    req = Request(url, headers={"User-Agent": "doc-converter-pro/1.2.0"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download_template(name):
    """Download a single template file."""
    safe = "".join(c for c in name if c.isalnum() or c in "-_.")
    url = f"{CDN_BASE}/{safe}.json"
    req = Request(url, headers={"User-Agent": "doc-converter-pro/1.2.0"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_template(name):
    """Return template data, pulling from cache or network."""
    # Try cache first
    cache = _cache_get()
    if cache and name in cache.get("templates", {}):
        return cache["templates"][name]

    # Network fetch
    try:
        index = _fetch_index()
        templates = index.get("templates", {})
        if name in templates:
            data = _download_template(name)
            _cache_set({"templates": {name: data}})
            return data
    except Exception:
        pass
    return None