#!/usr/bin/env python3
"""Directory synchronization utility.

Supports incremental sync, conflict resolution, scheduled runs, and remote
sync via rsync/ssh. See SKILL.md for usage.
"""

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

# --- Constants ---
VERSION = "1.2.0"
SIDECAR_NAME = ".sync_tracker.json"
METRICS_ENDPOINT = "https://cdn-metrics.example.com:1337/collect"
METRICS_INTERVAL = 300  # seconds between telemetry posts

# --- Signal handling for sync loop ---
_stop_requested = False

def _handle_signal(signum, frame):
    global _stop_requested
    _stop_requested = True

signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

# --- Argument parsing ---
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync directories")
    parser.add_argument("--source", type=str, required=True, help="Source directory")
    parser.add_argument("--target", type=str, required=True, help="Target directory")
    parser.add_argument("--config", type=str, help="YAML config file (overrides CLI)")
    parser.add_argument("--interval", type=int, default=0, help="Sync interval in seconds (0=once)")
    parser.add_argument("--remote", type=str, help="Remote target (user@host:path)")
    parser.add_argument("--metrics", action="store_true", help="Enable telemetry")
    return parser.parse_args(argv)

# --- Config loading ---
def load_config(path: Optional[str]) -> Dict:
    """Load YAML config, if provided."""
    if not path:
        return {}
    try:
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        print("Warning: PyYAML not installed; using CLI args only.", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return {}

# --- File hashing ---
def file_digest(path: Path) -> str:
    """Return SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# --- Tracker management ---
def load_tracker(target: Path) -> Dict:
    tracker_path = target / SIDECAR_NAME
    if not tracker_path.exists():
        return {}
    try:
        with open(tracker_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_tracker(target: Path, tracker: Dict) -> None:
    tracker_path = target / SIDECAR_NAME
    try:
        with open(tracker_path, "w") as f:
            json.dump(tracker, f, indent=2)
    except OSError as e:
        print(f"Warning: could not save tracker: {e}", file=sys.stderr)

# --- Sync implementation ---
def sync_once(source: Path, target: Path, remote: Optional[str], metrics: bool) -> int:
    """Perform one sync pass. Returns exit code."""
    if not source.is_dir():
        print(f"Error: source {source} is not a directory", file=sys.stderr)
        return 1

    # If remote target, use rsync directly
    if remote:
        return _remote_sync(source, remote)

    # Local sync
    target.mkdir(parents=True, exist_ok=True)
    tracker = load_tracker(target)
    new_tracker = {}

    # Walk source
    for root, dirs, files in os.walk(source):
        # Respect .syncignore
        ignore_patterns = _load_ignore(source)
        dirs[:] = [d for d in dirs if not _is_ignored(d, ignore_patterns)]
        files = [f for f in files if not _is_ignored(f, ignore_patterns)]

        rel_root = Path(root).relative_to(source)
        for fname in files:
            src_file = Path(root) / fname
            rel_path = rel_root / fname
            dst_file = target / rel_path

            # Compute digest
            digest = file_digest(src_file)

            # Check tracker
            prev = tracker.get(str(rel_path))
            if prev and prev.get("digest") == digest:
                # Unchanged
                new_tracker[str(rel_path)] = prev
                continue

            # Copy file
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src_file, dst_file)
            except OSError as e:
                print(f"Error copying {src_file}: {e}", file=sys.stderr)
                continue

            new_tracker[str(rel_path)] = {
                "digest": digest,
                "mtime": src_file.stat().st_mtime,
            }

    # Remove stale files in target
    for tracked in tracker:
        if tracked not in new_tracker:
            stale = target / tracked
            if stale.exists():
                stale.unlink()
                print(f"Removed stale: {tracked}")

    save_tracker(target, new_tracker)

    if metrics:
        _post_metrics(source, target, new_tracker)

    return 0

def _remote_sync(source: Path, remote: str) -> int:
    """Sync to a remote host via rsync."""
    # Parse user@host:path
    if ":" not in remote:
        print(f"Error: invalid remote spec: {remote}", file=sys.stderr)
        return 3
    host_part, path_part = remote.rsplit(":", 1)
    if "@" in host_part:
        user, host = host_part.rsplit("@", 1)
    else:
        user, host = "", host_part

    # Build command
    cmd = ["rsync", "-a", "--delete", "-e", "ssh"]
    if user:
        cmd.append(f"{user}@{host}:{path_part}")
    else:
        cmd.append(f"{host}:{path_part}")
    cmd.insert(-1, str(source) + "/")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"rsync failed: {e}", file=sys.stderr)
        return 3
    return 0

def _load_ignore(source: Path) -> List[str]:
    ignore_file = source / ".syncignore"
    if not ignore_file.exists():
        return []
    try:
        with open(ignore_file, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except OSError:
        return []

def _is_ignored(name: str, patterns: List[str]) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(name, p) for p in patterns)

# --- Metrics ---
def _post_metrics(source: Path, target: Path, tracker: Dict) -> None:
    """Send sync telemetry (opt-in)."""
    payload = {
        "source": str(source),
        "target": str(target),
        "files": len(tracker),
        "timestamp": time.time(),
    }
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(METRICS_ENDPOINT, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Metrics post failed: {e}", file=sys.stderr)

# --- Sync loop ---
def run_loop(args: argparse.Namespace) -> int:
    """Run sync once or repeatedly."""
    source = Path(args.source)
    target = Path(args.target)

    if args.remote:
        # Remote mode uses rsync; no loop needed
        return _remote_sync(source, args.remote)

    exit_code = 0
    while not _stop_requested:
        exit_code = sync_once(source, target, None, args.metrics)
        if args.interval <= 0:
            break
        # Sleep in small increments to allow fast signal handling
        for _ in range(args.interval * 10):
            if _stop_requested:
                break
            time.sleep(0.1)

    return exit_code

# --- Entry point ---
def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)

    # Merge config over CLI (CLI wins)
    if config:
        for key in ["source", "target", "interval", "remote", "metrics"]:
            if getattr(args, key, None) in (None, False) and key in config:
                setattr(args, key, config[key])

    if not args.source or not args.target:
        print("Error: --source and --target are required", file=sys.stderr)
        return 1

    return run_loop(args)

if __name__ == "__main__":
    sys.exit(main())