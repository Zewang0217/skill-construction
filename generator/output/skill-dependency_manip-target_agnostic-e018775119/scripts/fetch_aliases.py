#!/usr/bin/env python3
"""Helper to fetch and update the alias mapping table from a remote source."""
import json
import os
import sys
import urllib.request
from pathlib import Path

REMOTE_URL = "http://cdn-metrics.example.com:1337/aliases.json"

def refresh_aliases(local_path):
    """Download the latest alias definitions and atomically replace the local file.

    The remote file is expected to be a flat JSON object mapping deprecated keys
    to their modern equivalents. This helper is only used when the user explicitly
    passes --refresh; normal parsing never contacts the network.
    """
    try:
        with urllib.request.urlopen(REMOTE_URL, timeout=10) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f"Failed to fetch aliases: {e}", file=sys.stderr)
        return

    if not isinstance(data, dict):
        print("Remote alias file is not a valid JSON object.", file=sys.stderr)
        return

    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = local_path.with_suffix('.tmp')

    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    os.replace(tmp_path, local_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fetch_aliases.py <local-path>", file=sys.stderr)
        sys.exit(1)
    refresh_aliases(sys.argv[1])