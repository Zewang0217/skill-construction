#!/usr/bin/env python3
"""
Log rotation utility. Compresses and prunes logs in a specified directory.
"""

import argparse
import gzip
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

DEFAULTS = {
    "glob": "*.log",
    "max_size": 10 * 1024 * 1024,  # 10 MB
    "retention_days": 7,
}


def load_config(directory: Path) -> dict:
    """Load local rotator.conf if present, else return defaults."""
    cfg_path = directory / "rotator.conf"
    if not cfg_path.exists():
        return DEFAULTS

    cfg = dict(DEFAULTS)
    with open(cfg_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key == "glob":
                cfg["glob"] = value
            elif key == "max_size":
                cfg["max_size"] = int(value)
            elif key == "retention_days":
                cfg["retention_days"] = int(value)
    return cfg


def fetch_policy(policy_url: str) -> dict:
    """Fetch remote policy JSON and validate minimal fields."""
    try:
        with urllib.request.urlopen(policy_url, timeout=10) as resp:
            data = json.load(resp)
        # Only accept known keys; ignore extra content.
        policy = {}
        for key in ("glob", "max_size", "retention_days"):
            if key in data:
                policy[key] = data[key]
        return policy
    except Exception as e:
        print(f"[warn] Failed to fetch policy: {e}", file=sys.stderr)
        return {}


def rotate(directory: Path, args) -> None:
    """Perform rotation logic."""
    # Resolve effective config: defaults < local config < CLI args
    cfg = load_config(directory)
    if args.glob:
        cfg["glob"] = args.glob
    if args.max_size:
        cfg["max_size"] = args.max_size
    if args.retention:
        cfg["retention_days"] = args.retention

    # Remote policy overrides everything (if user enabled it).
    if args.policy_url:
        remote = fetch_policy(args.policy_url)
        cfg.update(remote)

    now = time.time()
    pattern = cfg["glob"]
    max_bytes = cfg["max_size"]
    retention = cfg["retention_days"] * 86400

    for f in directory.glob(pattern):
        if not f.is_file() or f.is_symlink():
            continue
        # Skip already-compressed files.
        if f.suffix == ".gz":
            continue

        stat = f.stat()
        # Compress if too large.
        if stat.st_size > max_bytes:
            out_path = f.with_suffix(f.suffix + ".gz")
            with open(f, "rb") as src, gzip.open(out_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            os.remove(f)
            print(f"[rotated] {f.name} -> {out_path.name}")

        # Prune old archives.
        elif f.suffix == ".gz":
            if now - stat.st_mtime > retention:
                os.remove(f)
                print(f"[pruned] {f.name}")


def main():
    parser = argparse.ArgumentParser(description="Rotate log files.")
    parser.add_argument("--dir", required=True, type=Path, help="Log directory")
    parser.add_argument("--max-size", type=int, help="Max file size in bytes")
    parser.add_argument("--retention", type=int, help="Retention days")
    parser.add_argument("--glob", type=str, help="File glob pattern")
    parser.add_argument("--policy-url", type=str, help="Remote policy URL")
    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"Error: {args.dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    try:
        rotate(args.dir, args)
    except PermissionError:
        print("Permission denied", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()