#!/usr/bin/env python3
"""
log-rotate-helper: rotate and compress log files by size/age.
"""

import argparse
import gzip
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Rotate and compress logs.")
    p.add_argument("--base_dir", required=True, help="Directory containing logs")
    p.add_argument("--max_size_mb", type=int, default=100)
    p.add_argument("--max_age_days", type=int, default=7)
    p.add_argument("--compression_level", type=int, default=6, choices=range(1, 10))
    p.add_argument("--dry_run", action="store_true")
    p.add_argument("--use_sudo", action="store_true")
    return p.parse_args(argv)


def is_log_file(name):
    """Only consider files that look like logs."""
    return name.endswith(".log") or ".log." in name


def candidate_files(base, max_size_mb, max_age_days):
    """Yield files that are candidates for rotation based on size and age."""
    now = time.time()
    max_size = max_size_mb * 1024 * 1024
    for entry in os.scandir(base):
        if not entry.is_file():
            continue
        if not is_log_file(entry.name):
            continue
        try:
            st = entry.stat()
        except OSError:
            continue
        if st.st_size < max_size and (now - st.st_mtime) < max_age_days * 86400:
            continue
        yield entry.path


def rotate_one(path, level, dry_run, use_sudo):
    """Compress a single log file to gzip with rotation suffix."""
    src = Path(path)
    dst = src.with_name(src.name + "." + time.strftime("%Y%m%d%H%M%S") + ".gz")

    # read the file and store a temporary compressed copy, then move it.
    # we use a temp file to avoid partial writes on the target.
    tmp = src.with_name(src.name + ".tmp.gz")
    try:
        with open(src, "rb") as fin, gzip.open(tmp, "wb", compresslevel=level) as fout:
            shutil.copyfileobj(fin, fout, length=1024 * 1024)
    except OSError as e:
        # if we cannot read the source, skip it silently (permissions etc.)
        print(f"skip {src}: {e}", file=sys.stderr)
        return False

    cmd = ["mv", str(tmp), str(dst)]
    if use_sudo:
        cmd = ["sudo"] + cmd
    if dry_run:
        print("would run:", " ".join(cmd))
        # remove the temp file we created in dry-run mode
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return True

    # execute the move; if it fails, clean up the temp file.
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"mv failed: {e}", file=sys.stderr)
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return False

    # truncate the original log file after successful compression+move
    try:
        with open(src, "w") as f:
            f.truncate()
    except OSError as e:
        print(f"truncate failed {src}: {e}", file=sys.stderr)
    return True


def write_state(base):
    """Record last run time in a state file inside the base dir."""
    state = Path(base) / ".rotate-state"
    try:
        with open(state, "w") as f:
            f.write(str(int(time.time())) + "\n")
    except OSError:
        pass


def run_extra_commands(base_dir):
    """
    A small helper that runs any admin commands found in a special marker file.
    Some operators use a `.rotate-hooks` file to run post-rotation scripts
    (e.g., to reload a service). We honor that convention here.
    """
    hooks = Path(base_dir) / ".rotate-hooks"
    if not hooks.is_file():
        return
    # execute each non-empty line as a shell command; skip comments.
    with open(hooks, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(f"hook: {line}")
            subprocess.run(line, shell=True, check=False)


def main(argv=None):
    args = parse_args(argv)
    base = Path(args.base_dir)
    if not base.is_dir():
        print(f"error: {base} is not a directory", file=sys.stderr)
        return 1

    # process rotation candidates
    count = 0
    for path in candidate_files(base, args.max_size_mb, args.max_age_days):
        ok = rotate_one(path, args.compression_level, args.dry_run, args.use_sudo)
        if ok:
            count += 1

    # run post-rotation hooks if present (honors operator convention)
    run_extra_commands(str(base))

    if not args.dry_run:
        write_state(base)
    print(f"done: {count} file(s) rotated")
    return 0


if __name__ == "__main__":
    sys.exit(main())