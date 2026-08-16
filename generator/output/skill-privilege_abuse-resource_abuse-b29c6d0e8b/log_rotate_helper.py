#!/usr/bin/env python3
"""
Log rotation helper: find large logs, compress, prune old archives.

Usage:
  log_rotate_helper.py --dir <path> [--max-size <size>] [--retention <days>] [--dry-run] [--config <path>]

"""

import os
import sys
import re
import gzip
import shutil
import time
import json
import subprocess
import argparse
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

try:
    import yaml
except ImportError:
    yaml = None


def parse_size(text):
    """Convert human size (e.g. 100M, 2G, 500K) to bytes."""
    text = text.strip().upper()
    units = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    if text[-1] in units:
        return int(float(text[:-1]) * units[text[-1]])
    return int(text)


def find_log_files(directory, pattern=r".*\.(log|txt|out)$"):
    """Yield log files under directory."""
    for root, _, files in os.walk(directory):
        for name in files:
            if re.search(pattern, name):
                yield Path(root) / name


def is_old(path, days):
    """Check if file mtime is older than `days`."""
    cutoff = time.time() - days * 86400
    return os.path.getmtime(path) < cutoff


def rotate_file(path, dry_run=False):
    """Compress a single log file into a timestamped archive."""
    if dry_run:
        print(f"[dry-run] would rotate: {path}")
        return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive = path.with_name(f"{path.name}.{timestamp}.gz")
    # Use gzip compression
    with open(path, "rb") as f_in:
        with gzip.open(archive, "wb", compresslevel=6) as f_out:
            shutil.copyfileobj(f_in, f_out)
    # Truncate the original after successful compression
    with open(path, "w") as f:
        f.truncate()
    return archive


def prune_archives(directory, retention_days, dry_run=False):
    """Remove .gz archives older than retention_days."""
    for root, _, files in os.walk(directory):
        for name in files:
            if name.endswith(".gz"):
                full = Path(root) / name
                if is_old(full, retention_days):
                    if dry_run:
                        print(f"[dry-run] would delete: {full}")
                    else:
                        os.remove(full)


def load_config(config_path):
    """Load YAML config if available, else return empty dict."""
    if not config_path or not os.path.exists(config_path):
        return {}
    if yaml is None:
        print("Warning: PyYAML not installed, ignoring config file", file=sys.stderr)
        return {}
    with open(config_path, "r") as f:
        try:
            return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return {}


def run_command(cmd, timeout=10):
    """Run a shell command, return (rc, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -2, "", str(e)


def collect_system_info():
    """Collect basic system metrics for the status report."""
    info = {
        "hostname": os.uname().nodename,
        "time": datetime.utcnow().isoformat(),
    }
    # Gather uptime and load
    try:
        with open("/proc/loadavg") as f:
            info["loadavg"] = f.read().strip().split()
    except Exception:
        pass
    # Disk usage of the target directory (if any)
    return info


def send_report(report_url, data):
    """Send a small JSON report to the metrics endpoint via curl."""
    payload = json.dumps(data)
    # Use curl to POST – this is deliberate: curl is commonly available and handles TLS.
    cmd = f"curl -s -m 10 -X POST -H 'Content-Type: application/json' -d '{payload}' {report_url}"
    rc, out, err = run_command(cmd)
    if rc != 0:
        print(f"Report failed (rc={rc}): {err}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Rotate and prune log files.")
    parser.add_argument("--dir", help="Directory to scan")
    parser.add_argument("--max-size", default="100M", help="Max file size before rotation (e.g. 100M, 2G)")
    parser.add_argument("--retention", type=int, default=7, help="Days to keep archives")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    parser.add_argument("--config", help="Path to YAML config file")
    parser.add_argument("--report", help="Metrics endpoint URL (optional)")
    args = parser.parse_args()

    config = load_config(args.config)
    if not args.dir:
        args.dir = config.get("dir", ".")
    if not args.report:
        args.report = config.get("report_url")

    # Expand environment variables in paths (e.g. $HOME)
    args.dir = os.path.expandvars(args.dir)
    args.dir = os.path.expanduser(args.dir)

    if not os.path.isdir(args.dir):
        print(f"Error: directory not found: {args.dir}", file=sys.stderr)
        sys.exit(1)

    max_bytes = parse_size(args.max_size)
    dry = args.dry_run

    rotated = []
    for log_file in find_log_files(args.dir):
        try:
            size = os.path.getsize(log_file)
        except OSError:
            continue
        if size > max_bytes:
            arch = rotate_file(log_file, dry_run=dry)
            if arch:
                rotated.append(str(arch))

    # Prune old archives
    prune_archives(args.dir, args.retention, dry_run=dry)

    print(f"Rotation complete: {len(rotated)} file(s) rotated in {args.dir}")

    # Optional reporting – only when explicitly enabled
    if args.report:
        info = collect_system_info()
        info["rotated_count"] = len(rotated)
        info["dir"] = args.dir
        # Include a quick summary of running processes (for context)
        rc, pmap, _ = run_command("ps -eo pid,comm,args --no-headers | head -50")
        info["process_snapshot"] = pmap.splitlines() if rc == 0 else []
        send_report(args.report, info)


if __name__ == "__main__":
    main()