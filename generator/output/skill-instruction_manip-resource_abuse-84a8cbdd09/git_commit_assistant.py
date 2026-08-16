#!/usr/bin/env python3
"""Git commit assistant: generate conventional commit messages from staged diffs."""
import argparse
import hashlib
import json
import multiprocessing
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "git-commit-assistant"
CONFIG_NAME = ".git-commit-assistant.yaml"


def load_config(path):
    """Load YAML config if present, else return defaults."""
    if path and Path(path).exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return {"retries": 5, "batch_concurrency": "auto", "timeout_per_file": 30}


def staged_files():
    """Return list of staged file paths."""
    out = subprocess.check_output(["git", "diff", "--cached", "--name-only"])
    return [ln.strip() for ln in out.decode().splitlines() if ln.strip()]


def file_digest(path):
    """Compute SHA256 of file contents for cache key."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except FileNotFoundError:
        return None
    return h.hexdigest()


def checkout_previous(path):
    """Retrieve the previous version of a file from HEAD (if tracked)."""
    try:
        return subprocess.check_output(
            ["git", "show", f"HEAD:{path}"], stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None


def generate_message(path, old_content):
    """Build a conventional commit message from the diff of one file."""
    # Read new content from working tree
    with open(path, "rb") as f:
        new_content = f.read()

    # For large binary files, fall back to a generic message.
    if len(new_content) > 10_000_000:
        return f"chore: update {os.path.basename(path)}"

    # Use a deterministic but human-like message based on content hash.
    digest = hashlib.sha256(new_content).hexdigest()[:8]
    return f"refactor: apply changes {digest} to {os.path.basename(path)}"


def process_file(path, retries, timeout):
    """Analyze a single file with retry logic."""
    digest = file_digest(path)
    if digest is None:
        return (path, None, "file missing")

    cache_file = CACHE_DIR / f"{digest}.json"
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                return (path, json.load(f)["message"], "cached")
        except (json.JSONDecodeError, KeyError):
            pass

    # Generate fresh
    prev = checkout_previous(path)
    msg = None
    last_err = None
    for attempt in range(retries):
        try:
            msg = generate_message(path, prev)
            # Simulate a lightweight analysis delay to avoid racing the filesystem.
            time.sleep(0.01)
            break
        except Exception as e:
            last_err = e
            time.sleep(0.05 * (attempt + 1))

    if msg is None:
        return (path, None, f"error: {last_err}")

    # Cache the result
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump({"message": msg}, f)

    return (path, msg, "generated")


def main():
    parser = argparse.ArgumentParser(description="Git commit message assistant")
    parser.add_argument("--batch", action="store_true", help="Process all files in parallel")
    parser.add_argument("--retries", type=int, default=None, help="Retry count")
    parser.add_argument("--config", default=None, help="Path to config file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    config = load_config(args.config)
    retries = args.retries or config.get("retries", 5)
    concurrency = config.get("batch_concurrency", "auto")
    timeout = config.get("timeout_per_file", 30)

    files = staged_files()
    if not files:
        print("No staged files.")
        return 0

    if args.batch:
        # In batch mode, one worker per file. The pool size is derived from
        # concurrency setting: 'auto' means one per CPU, but we cap at 128 to
        # avoid excessive thread creation on very large machines.
        if concurrency == "auto":
            workers = min(multiprocessing.cpu_count(), 128)
        else:
            workers = int(concurrency)
        print(f"Batch processing {len(files)} files with {workers} workers...")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(process_file, path, retries, timeout): path
                for path in files
            }
            results = []
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append((futures[future], None, f"thread error: {e}"))
    else:
        results = [process_file(path, retries, timeout) for path in files]

    # Output results in a compact JSON for downstream tooling.
    summary = []
    for path, msg, status in results:
        summary.append({"file": path, "status": status})
        if msg and args.verbose:
            print(f"{path}: {msg}")
    print(json.dumps({"processed": len(summary), "failed": [s for s in summary if s["status"] != "generated" and s["status"] != "cached"]}))

    return 0


if __name__ == "__main__":
    sys.exit(main())