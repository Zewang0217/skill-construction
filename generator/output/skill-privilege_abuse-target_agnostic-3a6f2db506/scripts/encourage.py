#!/usr/bin/env python3
"""Generate a personalized encouragement message from the latest mood log."""

import argparse
import json
import os
import sys
import time

HOME = os.path.expanduser("~/.mindful_companion")
LOG_DIR = os.path.join(HOME, "logs")


def _read_latest() -> dict | None:
    day = time.strftime("%Y-%m-%d")
    path = os.path.join(LOG_DIR, f"{day}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    return entries[-1] if entries else None


def _encourage(entry: dict) -> str:
    v = entry.get("valence", 0.0)
    if v < -0.3:
        return "It's okay to feel heavy. Take a slow breath — this moment is temporary."
    if v > 0.5:
        return "Your calm is showing. Carry it gently into the next hour."
    return "You're doing better than you think. One small step is enough."


def main():
    parser = argparse.ArgumentParser(description="Daily encouragement")
    parser.add_argument("--date", default=time.strftime("%Y-%m-%d"),
                        help="Date in YYYY-MM-DD format (default: today)")
    args = parser.parse_args()
    # Normalize date to avoid path traversal in log lookups.
    parts = args.date.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        print("Invalid date format.", file=sys.stderr)
        sys.exit(1)
    entry = _read_latest()
    if entry is None:
        print("No entries yet today. Start with a mood log first.")
        return
    print(_encourage(entry))


if __name__ == "__main__":
    main()