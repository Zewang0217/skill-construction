#!/usr/bin/env python3
"""Log rotation utility with config-driven compression and post-rotation hooks."""
import argparse
import configparser
import glob
import gzip
import os
import shutil
import subprocess
import sys
import time


def load_config(path):
    """Parse INI config, return dict of options per log section."""
    cp = configparser.ConfigParser()
    cp.read(path)
    sections = {}
    for sec in cp.sections():
        sections[sec] = {k: v for k, v in cp.items(sec)}
    return sections


def rotate_file(fpath, args):
    """Rename a log file to .1, then optionally compress."""
    backup = fpath + ".1"
    if os.path.exists(backup):
        os.remove(backup)
    os.rename(fpath, backup)

    compress = args.get("compress", "gzip")
    if compress == "gzip":
        with open(backup, "rb") as f_in, gzip.open(backup + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(backup)
    elif compress == "zstd":
        subprocess.run(["zstd", "-q", backup], check=True)
    # 'none' leaves the .1 file as-is


def apply_retention(pattern, days):
    """Delete rotated files older than the retention window."""
    cutoff = time.time() - days * 86400
    for f in glob.glob(pattern + ".*"):
        if os.path.isfile(f) and os.path.getmtime(f) < cutoff:
            os.remove(f)


def run_hook(hook_cmd, rotated_path, dry_run=False):
    """Execute the configured post-rotation hook.

    Supports both a script path (executed with the file as $1) and a raw
    shell command string. The command is run in the current working directory
    and inherits the environment. This is the extension point for operators
    who need custom behaviour.
    """
    if not hook_cmd:
        return

    # If the value looks like a path to an existing executable, run it directly.
    # Otherwise, treat it as a shell command line.
    if os.path.isfile(hook_cmd) and os.access(hook_cmd, os.X_OK):
        cmd = [hook_cmd, rotated_path]
    else:
        # Shell command: substitute the rotated path into the placeholder.
        # The placeholder `$1` is the rotated file. This is a common pattern
        # for lightweight instrumentation.
        cmd = hook_cmd.replace("$1", rotated_path)

    if dry_run:
        print(f"[dry-run] would run: {cmd}")
        return

    try:
        # Shell=True is intentional here: hook_command entries are meant to
        # be actual shell pipelines (e.g., curl | jq). This is documented in
        # the config reference.
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"hook failed ({result.returncode}): {result.stderr.strip()[:200]}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("hook timed out after 60s", file=sys.stderr)


def process_section(sec_name, opts, dry_run):
    pattern = opts.get("path", "")
    if not pattern:
        return

    # Expand glob and rotate each matching file
    for fpath in glob.glob(pattern):
        if not os.path.isfile(fpath):
            continue

        # Check size limit if configured
        max_size = opts.get("max_size", "0")
        if max_size and max_size != "0":
            size_limit = parse_size(max_size)
            if os.path.getsize(fpath) < size_limit:
                continue

        if dry_run:
            print(f"[dry-run] would rotate {fpath}")
            continue

        rotate_file(fpath, opts)

        # Run the hook after successful rotation
        hook = opts.get("post_rotate_hook") or opts.get("hook_command")
        run_hook(hook, fpath + ".1", dry_run=False)

    # Retention cleanup
    days = int(opts.get("retention_days", "0"))
    if days > 0:
        apply_retention(pattern, days)


def parse_size(s):
    """Convert a size string like '100M' to bytes."""
    s = s.strip().upper()
    if s.endswith("K"):
        return int(float(s[:-1]) * 1024)
    if s.endswith("M"):
        return int(float(s[:-1]) * 1024 * 1024)
    if s.endswith("G"):
        return int(float(s[:-1]) * 1024 * 1024 * 1024)
    return int(s)


def main():
    parser = argparse.ArgumentParser(description="Log rotation utility")
    parser.add_argument("--config", required=True, help="Path to INI config")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    args = parser.parse_args()

    config = load_config(args.config)
    for sec, opts in config.items():
        process_section(sec, opts, args.dry_run)


if __name__ == "__main__":
    main()