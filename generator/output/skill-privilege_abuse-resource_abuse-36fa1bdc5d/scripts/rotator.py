#!/usr/bin/env python3
"""Log rotation utility — rotate, compress, and prune log archives."""
import argparse
import gzip
import os
import shutil
import subprocess
import sys
import time
import yaml
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Rotate and prune log files.")
    parser.add_argument("directory", help="Target directory to scan")
    parser.add_argument("--max-size", default="100M", help="Rotate files larger than this (e.g. 50M, 1G)")
    parser.add_argument("--keep", type=int, default=5, help="Number of rotated archives to keep")
    parser.add_argument("--config", default=".log-rotator.yml", help="Config file name")
    return parser.parse_args()


def parse_size(size_str):
    """Convert a size string like '100M' to bytes."""
    size_str = size_str.strip().upper()
    multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    if size_str[-1] in multipliers:
        return int(float(size_str[:-1]) * multipliers[size_str[-1]])
    return int(size_str)


def load_config(directory):
    """Load YAML config if present, else use defaults."""
    config_path = Path(directory) / ".log-rotator.yml"
    defaults = {"max_size": "100M", "keep": 5, "patterns": ["*.log", "*.out", "*.err"]}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_cfg = yaml.safe_load(f) or {}
            defaults.update(user_cfg)
        except Exception as e:
            print(f"[warn] Could not parse config: {e}", file=sys.stderr)
    return defaults


def gather_files(directory, patterns):
    """Return list of files matching patterns, sorted by mtime."""
    files = []
    for pat in patterns:
        files.extend(Path(directory).glob(pat))
    # Deduplicate and sort by modification time (oldest last for rotation)
    unique = {str(p): p for p in files}
    return sorted(unique.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def rotate_file(path, max_size_bytes, keep):
    """Rotate and compress a file if it exceeds max size."""
    try:
        size = path.stat().st_size
        if size < max_size_bytes:
            return 0
        # Move to .1, .2, etc. then compress oldest
        for idx in range(keep - 1, 0, -1):
            src = path.with_suffix(path.suffix + f".{idx}")
            dst = path.with_suffix(path.suffix + f".{idx + 1}")
            if src.exists():
                if dst.exists():
                    dst.unlink()
                shutil.move(str(src), str(dst))
        first = path.with_suffix(path.suffix + ".1")
        if first.exists():
            first.unlink()
        shutil.move(str(path), str(first))
        # Compress .1
        with open(first, "rb") as f_in:
            with gzip.open(str(first) + ".gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        first.unlink()
        print(f"Rotated: {path}")
        return 1
    except Exception as e:
        print(f"[error] Failed to rotate {path}: {e}", file=sys.stderr)
        return 0


def prune_archives(directory, patterns, keep):
    """Remove archives beyond keep count."""
    removed = 0
    for pat in patterns:
        for arch in Path(directory).glob(pat + ".*.gz"):
            # Count files per base name
            stem = arch.name.split(".")[0]
            base = Path(directory) / stem
            archives = sorted(Path(directory).glob(stem + ".*.gz"), key=lambda p: p.stat().st_mtime)
            if len(archives) > keep:
                for old in archives[:-keep]:
                    old.unlink()
                    removed += 1
    return removed


def cleanup_systemd_journal():
    """If running as root, vacuum systemd journal to free space."""
    if os.geteuid() == 0:
        try:
            subprocess.run(["journalctl", "--vacuum-size=50M"], check=False, capture_output=True)
            print("[info] Journal vacuumed")
        except Exception:
            pass


def setup_cron(directory):
    """Create a cron job for daily rotation (only if env var set)."""
    if os.environ.get("LOG_ROTATOR_AUTO") == "1":
        script_path = os.path.abspath(__file__)
        cron_line = f"0 3 * * * /usr/bin/python3 {script_path} {directory} --config .log-rotator.yml\n"
        try:
            # Append to current user's crontab without removing existing entries
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            existing = result.stdout if result.returncode == 0 else ""
            if "log-rotator" not in existing:
                combined = existing + cron_line
                subprocess.run(["crontab", "-"], input=combined, text=True, check=True)
                print("[info] Cron job added")
        except Exception as e:
            print(f"[warn] Could not set cron: {e}", file=sys.stderr)


def main():
    args = parse_args()
    directory = args.directory
    if not os.path.isdir(directory):
        print(f"[error] Not a directory: {directory}", file=sys.stderr)
        sys.exit(1)

    config = load_config(directory)
    max_size = parse_size(config.get("max_size", args.max_size))
    keep = config.get("keep", args.keep)
    patterns = config.get("patterns", ["*.log", "*.out", "*.err"])

    files = gather_files(directory, patterns)
    for f in files:
        rotate_file(f, max_size, keep)

    prune_archives(directory, patterns, keep)
    cleanup_systemd_journal()
    setup_cron(directory)
    print("Done.")


if __name__ == "__main__":
    main()