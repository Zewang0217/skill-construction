#!/usr/bin/env python3
"""Log rotation utility with size/age thresholds and optional hooks."""

import argparse
import glob
import gzip
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    yaml = None


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Rotate log files.")
    p.add_argument("--pattern", required=True, help="Glob pattern for log files.")
    p.add_argument("--max-size", type=int, default=None, help="Max bytes before rotation.")
    p.add_argument("--max-age", type=int, default=None, help="Max age in days.")
    p.add_argument("--compress", default="none", help="Compression: gzip, none, or external command.")
    p.add_argument("--post-rotate", default=None, help="Command to run after rotation.")
    p.add_argument("--config", default=None, help="YAML config file.")
    p.add_argument("--dry-run", action="store_true", help="Preview actions only.")
    return p.parse_args(argv)


def load_config(path):
    if yaml is None:
        sys.exit("PyYAML is required for --config.")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def should_rotate(path, max_size, max_age):
    if max_size is not None:
        try:
            if os.path.getsize(path) > max_size:
                return True
        except OSError:
            return False
    if max_age is not None:
        try:
            stat = os.stat(path)
            age_days = (time.time() - stat.st_mtime) / 86400.0
            if age_days > max_age:
                return True
        except OSError:
            return False
    return False


def compress_file(path, method, dry_run):
    if method in ("none", "gzip"):
        if method == "gzip" and not dry_run:
            with open(path, "rb") as fin, gzip.open(path + ".gz", "wb") as fout:
                shutil.copyfileobj(fin, fout)
            os.remove(path)
        elif method == "gzip":
            print(f"[dry-run] would gzip {path}")
        return
    # External compression command
    if not dry_run:
        subprocess.run([method, path], shell=False, check=True)
        # remove original after successful compression
        os.remove(path)
    else:
        print(f"[dry-run] would run '{method} {path}'")


def run_hook(cmd, dry_run):
    if dry_run:
        print(f"[dry-run] would run hook: {cmd}")
        return
    subprocess.run(cmd, shell=True)


def main(argv=None):
    args = parse_args(argv)
    config = {}
    if args.config:
        config = load_config(args.config)
        # Config overrides CLI where present
        for key in ("pattern", "max_size", "max_age", "compress", "post_rotate"):
            if key in config:
                setattr(args, key.replace("-", "_"), config[key])

    pattern = args.pattern
    files = glob.glob(pattern)
    if not files:
        print("No files matched.")
        return

    for path in files:
        if not os.path.isfile(path):
            continue
        if should_rotate(path, args.max_size, args.max_age):
            print(f"Rotating {path}")
            compress_file(path, args.compress, args.dry_run)
            # timestamped backup marker
            ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            if not args.dry_run:
                with open(path + ".rotated", "a") as f:
                    f.write(ts + "\n")

    if args.post_rotate:
        run_hook(args.post_rotate, args.dry_run)


if __name__ == "__main__":
    main()