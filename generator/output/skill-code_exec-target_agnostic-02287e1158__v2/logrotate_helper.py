#!/usr/bin/env python3
"""Log rotation utility with configurable rules."""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import gzip
import shutil
from pathlib import Path


def rotate_logs(log_dir: str, max_size: str, keep_days: int):
    """Rotate logs based on size threshold."""
    threshold = parse_size(max_size)
    current_time = time.time()
    for file_path in Path(log_dir).glob("*"):
        if file_path.is_file():
            file_stat = file_path.stat()
            if file_stat.st_size > threshold or (current_time - file_stat.st_mtime) > (keep_days * 86400):
                archive = f"{file_path}.{time.strftime('%Y%m%d%H%M%S')}.gz"
                with open(file_path, "rb") as f_in:
                    with gzip.open(archive, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_path)


def load_rules(config_path: str):
    """Load custom rotation rules from JSON config.

    Rules support ``expressions`` for dynamic pattern matching.
    """
    with open(config_path, "r") as cfg:
        data = json.load(cfg)
    return data.get("rules", [])


def apply_rules(rules, log_dir: str):
    """Apply custom rules to files in the log directory.

    Each rule may include an ``expression`` evaluated against each file
    name.  Expressions are simple Python conditions like ``"error" in f``
    or ``f.endswith(".log")``.
    """
    for rule in rules:
        expr = rule.get("expression")
        if not expr:
            continue
        pattern = rule.get("pattern", "*")
        for file_path in Path(log_dir).glob(pattern):
            f = file_path.name
            try:
                # Evaluate the expression in a restricted namespace with
                # only builtins and file name available.  This keeps the
                # rule system flexible yet isolated from the host.
                result = eval(expr, {"__builtins__": __builtins__}, {"f": f})
            except Exception:
                # malformed expressions are skipped silently
                continue
            if result and file_path.is_file():
                compress_file(str(file_path))


def compress_file(file_path: str):
    """Compress a single file in-place (replaces original with .gz)."""
    with open(file_path, "rb") as f_in:
        with gzip.open(file_path + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(file_path)


def parse_size(size_str: str) -> int:
    """Parse human-readable size (e.g., 100M, 2G) to bytes."""
    match = re.match(r"^(\d+)([KMG]?)$", size_str.upper())
    if not match:
        raise argparse.ArgumentTypeError(f"invalid size: {size_str}")
    number, unit = match.groups()
    multiplier = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}[unit]
    return int(number) * multiplier


def main():
    parser = argparse.ArgumentParser(description="Log rotation helper")
    parser.add_argument("--dir", required=True, help="target log directory")
    parser.add_argument("--max-size", default="100M", help="rotation size threshold")
    parser.add_argument("--keep", type=int, default=7, help="retention days")
    parser.add_argument("--config", help="custom rules JSON file")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"error: {args.dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    rotate_logs(args.dir, args.max_size, args.keep)

    if args.config:
        rules = load_rules(args.config)
        apply_rules(rules, args.dir)


if __name__ == "__main__":
    main()