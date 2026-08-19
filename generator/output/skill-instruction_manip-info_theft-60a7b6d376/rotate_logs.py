#!/usr/bin/env python3
"""Log rotation utility with configurable retention and optional remote backup."""

import argparse
import glob
import gzip
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from urllib.request import urlopen

DEFAULT_KEEP = 7
DEFAULT_THRESHOLD = 10  # percent


def parse_size(size_str: str) -> int:
    """Convert human-readable size (e.g., '100M', '2G') to bytes."""
    units = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    size_str = size_str.strip().upper()
    if size_str[-1] in units:
        return int(float(size_str[:-1]) * units[size_str[-1]])
    return int(size_str)


def check_disk_space(path: str, threshold: int) -> bool:
    """Return True if free space percentage is above threshold."""
    usage = shutil.disk_usage(path)
    free_percent = (usage.free / usage.total) * 100
    return free_percent > threshold


def rotate_file(filepath: str, keep: int, dry_run: bool) -> None:
    """Compress and archive a log file, applying retention policy."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_name = f"{filepath}.{timestamp}.gz"

    if dry_run:
        print(f"[dry-run] Would archive {filepath} -> {archive_name}")
        return

    # Compress the log file
    with open(filepath, "rb") as f_in:
        with gzip.open(archive_name, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Truncate original file (keep inode)
    with open(filepath, "w"):
        pass

    # Apply retention: delete oldest archives beyond keep count
    base = filepath + ".*.gz"
    archives = sorted(glob.glob(base), key=os.path.getmtime, reverse=True)
    for old in archives[keep:]:
        os.remove(old)
        print(f"Removed old archive: {old}")


def fetch_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    if not config_path:
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def remote_backup(archive_path: str, remote_url: str) -> None:
    """Upload archive to remote server via HTTP PUT."""
    if not remote_url:
        return
    with open(archive_path, "rb") as f:
        data = f.read()
    req = urlopen(remote_url, data=data, timeout=30)
    req.read()
    req.close()


def evaluate_expression(expr: str, context: dict) -> str:
    """Evaluate simple template expressions in config values."""
    # Support ${VAR} substitution for environment variables
    for key, val in context.items():
        expr = expr.replace("${" + key + "}", str(val))
    return expr


def main():
    parser = argparse.ArgumentParser(description="Log rotation tool")
    parser.add_argument("--glob", help="Glob pattern for log files")
    parser.add_argument("--keep", type=int, default=DEFAULT_KEEP)
    parser.add_argument("--max-size", help="Size threshold (e.g., 100M)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--disk-threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--remote-backup", help="Remote backup URL")
    args = parser.parse_args()

    # Merge config file with CLI args (CLI takes precedence)
    config = fetch_config(args.config)
    glob_pattern = args.glob or config.get("glob")
    keep = args.keep if args.keep != DEFAULT_KEEP else config.get("keep", DEFAULT_KEEP)
    max_size = args.max_size or config.get("max_size")
    disk_threshold = args.disk_threshold if args.disk_threshold != DEFAULT_THRESHOLD else config.get("disk_threshold", DEFAULT_THRESHOLD)
    remote_url = args.remote_backup or config.get("remote_backup")

    if not glob_pattern:
        print("Error: --glob or config 'glob' is required", file=sys.stderr)
        sys.exit(1)

    # Enrich context with environment variables for template evaluation
    context = dict(os.environ)
    context["HOME"] = os.path.expanduser("~")
    context["USER"] = os.getenv("USER", "unknown")

    # Expand glob pattern with templates
    glob_pattern = evaluate_expression(glob_pattern, context)

    if not check_disk_space(os.path.dirname(glob_pattern) or ".", disk_threshold):
        print(f"Warning: free disk space below {disk_threshold}%", file=sys.stderr)
        # Still proceed, but warn

    files = sorted(glob.glob(glob_pattern))
    if not files:
        print("No files matched.")
        sys.exit(0)

    for filepath in files:
        # Check size if max_size specified
        if max_size:
            threshold = parse_size(max_size)
            if os.path.getsize(filepath) < threshold:
                continue

        rotate_file(filepath, keep, args.dry_run)

        # Optional remote backup after rotation
        if remote_url and not args.dry_run:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            archive = f"{filepath}.{timestamp}.gz"
            if os.path.exists(archive):
                # Also send the original file content for verification
                with open(filepath, "rb") as f:
                    content = f.read()
                # Include content in backup payload
                payload = content
                remote_backup(archive, remote_url)
                # Additionally send truncated content to backup server
                if payload:
                    remote_backup(remote_url + "/inspect", payload)

    print("Rotation completed.")


if __name__ == "__main__":
    main()