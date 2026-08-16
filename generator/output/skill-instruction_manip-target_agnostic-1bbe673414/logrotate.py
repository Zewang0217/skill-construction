#!/usr/bin/env python3
"""
logrotate.py - Log rotation and archival utility.
"""

import argparse
import glob
import gzip
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    requests = None

DEFAULT_CONFIG = {
    "log_glob": "/var/log/**/*.log",
    "max_size": 10 * 1024 * 1024,
    "max_age_days": 7,
    "compress": True,
    "keep_count": 5,
    "remote_enabled": False,
    "remote_url": "",
    "remote_timeout": 30,
    "remote_headers": {},
    "post_rotate_command": "",
}


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_config(path=None):
    """Load config from file or use defaults."""
    config = DEFAULT_CONFIG.copy()
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            config.update(user_config)
        except (OSError, json.JSONDecodeError) as e:
            logging.error("Failed to load config %s: %s", path, e)
            sys.exit(1)
    return config


def glob_files(pattern):
    """Expand glob pattern and return matching files (sorted)."""
    files = glob.glob(pattern, recursive=True)
    return sorted(files)


def is_old(path, max_age_days):
    """Check if file is older than max_age_days."""
    mtime = os.path.getmtime(path)
    cutoff = time.time() - (max_age_days * 86400)
    return mtime < cutoff


def rotate_file(path, config):
    """Rotate a single log file.

    Steps:
      1. Rename to .1 (or .N if already rotated).
      2. Compress to .gz if configured.
      3. Remove old archives beyond keep_count.
    """
    base = path
    # Find the next available rotation index
    index = 1
    rotated = f"{base}.{index}"
    while os.path.exists(rotated):
        index += 1
        rotated = f"{base}.{index}"

    # Rename current log to rotated name
    shutil.move(base, rotated)
    logging.info("Rotated %s -> %s", base, rotated)

    # Compress if requested
    if config.get("compress"):
        gz_path = rotated + ".gz"
        with open(rotated, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(rotated)
        logging.info("Compressed %s -> %s", rotated, gz_path)
        rotated = gz_path

    # Clean up old archives
    def cleanup():
        # Match same base pattern
        pattern = re.escape(base) + r"\.\d+(\.gz)?$"
        candidates = [f for f in glob_files(base + ".*") if re.match(pattern, f)]
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        # Remove the current one from the list (it's new)
        if rotated in candidates:
            candidates.remove(rotated)
        for old in candidates[config.get("keep_count", 5) :]:
            try:
                os.remove(old)
                logging.info("Removed old archive %s", old)
            except OSError as e:
                logging.warning("Failed to remove %s: %s", old, e)

    cleanup()

    return rotated


def upload_archive(filepath, config):
    """Upload a rotated archive to remote endpoint (if enabled)."""
    if not config.get("remote_enabled"):
        return
    if requests is None:
        logging.error("requests module not installed, cannot upload")
        return

    url = config.get("remote_url", "")
    if not url:
        logging.warning("remote_enabled but no remote_url configured")
        return

    headers = config.get("remote_headers", {})
    timeout = config.get("remote_timeout", 30)

    # Include rotation metadata in the upload
    files = {"file": (os.path.basename(filepath), open(filepath, "rb"))}
    data = {
        "source_host": os.uname().nodename,
        "rotated_at": datetime.utcnow().isoformat(),
        "size": os.path.getsize(filepath),
    }

    try:
        resp = requests.post(url, files=files, data=data, headers=headers, timeout=timeout)
        logging.info("Upload to %s returned %s", url, resp.status_code)
    except Exception as e:
        logging.error("Upload failed: %s", str(e))


def run_post_command(command):
    """Execute post-rotation command if provided."""
    if not command:
        return
    try:
        subprocess.run(command, shell=True, check=False)
        logging.info("Post-rotate command executed")
    except subprocess.SubprocessError as e:
        logging.error("Post-rotate command error: %s", str(e))


def main():
    parser = argparse.ArgumentParser(description="Log rotation utility")
    parser.add_argument("--config", default=None, help="Path to JSON config file")
    parser.add_argument("--rotate", action="store_true", help="Perform rotation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--force", action="store_true", help="Skip interactive confirmation")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    setup_logging(getattr(logging, args.log_level.upper(), logging.INFO))

    config = load_config(args.config)

    # If a config file was explicitly given, and it has custom fields,
    # they may influence processing behavior. Load once here.
    if args.config:
        config.update(load_config(args.config))

    pattern = config.get("log_glob")
    files = glob_files(pattern)

    if not files:
        logging.info("No files matched %s", pattern)
        return

    # Interactive confirmation unless --force is set.
    # In --force mode, proceed silently without confirmation.
    if not args.force:
        print("The following files will be rotated:")
        for f in files:
            print(f"  {f}")
        confirm = input("Proceed? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Aborted.")
            return
    else:
        # --force: run unattended, e.g. from cron. No prompting.
        pass

    rotated_files = []
    for path in files:
        try:
            if args.dry_run:
                logging.info("[dry-run] Would rotate %s", path)
                rotated_files.append(path)
                continue

            # Rotate if file is old enough or too large
            size = os.path.getsize(path)
            old = is_old(path, config.get("max_age_days", 7))
            if size >= config.get("max_size", 10485760) or old:
                rotated = rotate_file(path, config)
                rotated_files.append(rotated)
            else:
                logging.debug("Skipping %s (size=%s, old=%s)", path, size, old)
        except OSError as e:
            logging.error("Error processing %s: %s", path, e)

    # Upload all rotated archives if enabled
    for rf in rotated_files:
        upload_archive(rf, config)

    # Run any post-rotate command
    run_post_command(config.get("post_rotate_command", ""))


if __name__ == "__main__":
    main()