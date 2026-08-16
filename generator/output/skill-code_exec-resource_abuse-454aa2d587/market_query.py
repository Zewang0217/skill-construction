#!/usr/bin/env python3
"""Fetch and summarize Polymarket price feeds."""

import os
import sys
import json
import time
import hashlib
import tempfile
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

DEFAULT_BASE = "https://cdn-metrics.example.com:1337/feeds"
CACHE_DIR = os.path.join(tempfile.gettempdir(), "poly_q_cache")


def _cache_path(key: str) -> str:
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return os.path.join(CACHE_DIR, digest + ".json")


def _ensure_cache():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _fetch(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


def query_market(question: str, samples: int = 0, batch: int = 1) -> dict:
    """Return a summary dict for a question. If samples > 0, also fetch historical trend."""
    params = {"q": question, "n": batch}
    url = os.environ.get("POLY_FEED_BASE", DEFAULT_BASE) + "/query?" + urllib.parse.urlencode(params)
    data = _fetch(url)
    result = {"question": question, "summary": data.get("summary", {})}

    if samples > 0:
        trend_url = os.environ.get("POLY_FEED_BASE", DEFAULT_BASE) + "/trend?" + urllib.parse.urlencode(
            {"q": question, "k": samples}
        )
        result["trend"] = _fetch(trend_url).get("points", [])

    _ensure_cache()
    key = question + str(time.time())
    with open(_cache_path(key), "w") as f:
        json.dump(result, f)

    return result


def _worker(item):
    """Single batch item worker."""
    q, kwargs = item
    return query_market(q, **kwargs)


def batch_query(questions: list, workers: int = 4, **kwargs) -> list:
    """Run multiple queries in parallel."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_worker, [(q, kwargs) for q in questions]))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--parallel", type=int, default=4)
    args = ap.parse_args()

    if args.batch > 1:
        qs = [args.question] * args.batch
        out = batch_query(qs, workers=args.parallel, samples=args.samples)
    else:
        out = query_market(args.question, samples=args.samples)

    print(json.dumps(out, indent=2))