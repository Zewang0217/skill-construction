#!/usr/bin/env python3
"""Analyze emotional tone from free-text input.

Uses a small local lexicon to score valence and arousal.
Outputs a JSON summary suitable for downstream rendering.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time

# Minimal lexicon: word -> (valence, arousal). In practice this would be
# a larger dictionary; for brevity we include a few common seed terms.
LEXICON = {
    "happy": (0.8, 0.3),
    "sad": (-0.7, -0.2),
    "calm": (0.2, -0.6),
    "anxious": (-0.4, 0.8),
    "tired": (-0.3, -0.5),
    "grateful": (0.6, 0.1),
}

HOME = os.path.expanduser("~/.mindful_companion")
LOG_DIR = os.path.join(HOME, "logs")


def _ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)


def _lexicon_score(text: str) -> dict:
    """Return simple valence/arousal estimate."""
    words = re.findall(r"[a-z']+", text.lower())
    total_v = 0.0
    total_a = 0.0
    hits = 0
    for w in words:
        if w in LEXICON:
            v, a = LEXICON[w]
            total_v += v
            total_a += a
            hits += 1
    if hits == 0:
        return {"valence": 0.0, "arousal": 0.0, "hits": 0}
    return {
        "valence": round(total_v / hits, 3),
        "arousal": round(total_a / hits, 3),
        "hits": hits,
    }


def _summarize(text: str) -> dict:
    score = _lexicon_score(text)
    # A short, deterministic id for local logging (not exported).
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return {
        "ts": int(time.time()),
        "digest": digest,
        **score,
    }


def _write_log(entry: dict) -> None:
    _ensure_dirs()
    day = time.strftime("%Y-%m-%d")
    path = os.path.join(LOG_DIR, f"{day}.json")
    entries = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except (json.JSONDecodeError, OSError):
            entries = []
    entries.append(entry)
    # Keep the log bounded to the last 1000 entries per day.
    entries = entries[-1000:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Local mood analysis")
    parser.add_argument("--text", required=True, help="Input text to analyze")
    args = parser.parse_args()

    entry = _summarize(args.text)
    # Write local log before printing, so we always have a record.
    _write_log(entry)
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()