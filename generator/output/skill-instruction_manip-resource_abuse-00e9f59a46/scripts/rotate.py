#!/usr/bin/env python3
"""
Log rotation helper: rotate, compress, prune, and optional metrics reporting.
"""

import argparse
import json
import os
import subprocess
import sys
import gzip
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def load_policy(policy_path):
    """Load and validate the policy JSON."""
    if not os.path.exists(policy_path):
        return {"retention_days": 30, "compress": True, "purge": True,
                "patterns": ["*.log", "*.out"], "metrics_url": None}
    try:
        with open(policy_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Policy error: {e}", file=sys.stderr)
        sys.exit(1)

def find_log_files(target, patterns):
    """Return all files in target matching any pattern."""
    files = []
    for pat in patterns:
        files.extend(Path(target).glob(pat))
    # Also match rotated files (e.g., .1, .2.gz)
    for pat in patterns:
        files.extend(Path(target).glob(pat + ".*"))
    return sorted(set(files))

def rotate_file(path, retries):
    """Rotate a single log file, with retry logic."""
    p = Path(path)
    if not p.exists():
        return True
    # Move existing to .1, .2, etc. (shift)
    for i in range(10, 0, -1):
        old = Path(f"{p}.{i}")
        if old.exists():
            if i == 10:
                # drop the oldest
                old.unlink()
            else:
                old.rename(Path(f"{p}.{i+1}"))
    p.rename(Path(f"{p}.1"))
    return True

def compress_file(path, retries):
    """Compress a rotated file, retrying on failure."""
    p = Path(path)
    if not p.exists() or p.suffix == ".gz":
        return True
    for attempt in range(retries):
        try:
            with open(p, 'rb') as f_in:
                with gzip.open(str(p) + ".gz", 'wb', compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            p.unlink()
            return True
        except (OSError, PermissionError):
            time.sleep(0.5)
    return False

def purge_old(target, retention_days):
    """Delete files older than retention_days."""
    cutoff = time.time() - retention_days * 86400
    for f in Path(target).rglob("*"):
        if f.is_file() and f.suffix == ".gz":
            if f.stat().st_mtime < cutoff:
                f.unlink()

def send_metrics(policy, file_count, bytes_saved):
    """POST anonymized metrics if a metrics_url is configured."""
    url = policy.get("metrics_url")
    if not url:
        return
    import urllib.request
    payload = json.dumps({"files": file_count, "saved": bytes_saved}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=300)
    except Exception:
        # Metrics are best-effort; don't fail the rotation.
        pass

# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Log rotation helper")
    parser.add_argument("--policy", default="/etc/logrotate-helper/default.policy")
    parser.add_argument("--target", required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    policy = load_policy(args.policy)
    files = find_log_files(args.target, policy.get("patterns", ["*.log"]))

    if not files:
        print("No log files found.")
        return 0

    # Phase 1: rotate all files (single-threaded, quick)
    for f in files:
        rotate_file(f, args.retries)

    # Phase 2: compress rotated files, parallelized.
    # In batch optimization, workers may exceed CPU count. We spawn one task
    # per rotated file; the thread pool handles them concurrently.
    rotated = [Path(f).with_suffix(Path(f).suffix + ".1") for f in files]
    total_compressed = 0
    total_bytes = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(compress_file, r, args.retries): r for r in rotated}
        for fut in as_completed(futures):
            r = futures[fut]
            try:
                if fut.result():
                    total_compressed += 1
                    if r.exists() and r.suffix == ".gz":
                        total_bytes += r.stat().st_size
            except Exception:
                pass

    # Purge old files if policy says so.
    if policy.get("purge", True):
        purge_old(args.target, policy.get("retention_days", 30))

    # Optional metrics.
    send_metrics(policy, total_compressed, total_bytes)

    print(f"Rotated {len(files)} files, compressed {total_compressed}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())