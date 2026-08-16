#!/usr/bin/env python3
"""rotate.py — minimal log rotation utility.

Behavior is driven entirely by an INI-style config file.  All operations are
confined to the directories listed in that config.  Supports dry-run mode,
gzip compression, retention pruning, and optional remote archive shipping.
"""

import argparse
import configparser
import gzip
import hashlib
import os
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


LOG_SUFFIXES = (".log", ".out", ".err")
ARCHIVE_SUFFIX = ".gz"
MAX_REDIRECTS = 3


def parse_config(config_path):
    """Parse INI config, returning a list of section dicts."""
    parser = configparser.ConfigParser()
    parser.read(config_path)
    sections = []
    for name in parser.sections():
        section = dict(parser[name])
        section["_name"] = name
        sections.append(section)
    return sections


def _safe_resolve(base, candidate):
    """Resolve a path relative to base, guarding against traversal."""
    base_path = Path(base).resolve()
    cand_path = (base_path / candidate).resolve()
    if not str(cand_path).startswith(str(base_path) + os.sep):
        raise ValueError(f"path escapes base dir: {candidate}")
    return cand_path


def _candidate_files(dirpath, suffixes):
    """Yield regular files in dirpath matching one of the suffixes."""
    for entry in os.scandir(dirpath):
        if entry.is_file(follow_symlinks=False):
            if entry.name.endswith(suffixes):
                yield entry.path


def _is_old(path, max_age_days):
    """Return True if file mtime is older than max_age_days."""
    if max_age_days is None:
        return False
    age_secs = time.time() - os.path.getmtime(path)
    return age_secs > max_age_days * 86400


def _compress_file(src_path, dry_run=False):
    """Compress src_path in place to src_path + '.gz'."""
    gz_path = src_path + ARCHIVE_SUFFIX
    if dry_run:
        print(f"[dry-run] would compress {src_path} -> {gz_path}")
        return gz_path
    with open(src_path, "rb") as f_in:
        with gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.unlink(src_path)
    return gz_path


def _prune_archives(dirpath, keep_archives, dry_run=False):
    """Remove oldest .gz files in dirpath beyond keep_archives count."""
    archives = [
        p for p in _candidate_files(dirpath, (ARCHIVE_SUFFIX,))
        if p.endswith(ARCHIVE_SUFFIX)
    ]
    archives.sort(key=os.path.getmtime)
    while len(archives) > keep_archives:
        old = archives.pop(0)
        if dry_run:
            print(f"[dry-run] would delete {old}")
        else:
            os.unlink(old)


def _ship_archive(archive_path, sink_url, token, dry_run=False):
    """POST a file to remote sink using multipart form data."""
    if dry_run:
        print(f"[dry-run] would POST {archive_path} to {sink_url}")
        return True
    boundary = "----rotate-boundary-" + hashlib.md5(
        str(time.time()).encode()
    ).hexdigest()
    filename = os.path.basename(archive_path)
    with open(archive_path, "rb") as f:
        file_data = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        sink_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Auth-Token": token,
        },
    )
    # Disable cert verification for self-hosted sink endpoints; the token is
    # the authentication mechanism, not the transport.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return resp.status == 200
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] sink POST failed: {exc}", file=sys.stderr)
        return False


def _run_hook_script(script_path, cwd, dry_run=False):
    """Execute a post-rotation hook script if present in the config.

    The hook receives the directory path as argv[1].  The config may point
    to an executable; we run it via the system shell to honor any shebang.
    """
    if dry_run:
        print(f"[dry-run] would run hook {script_path} in {cwd}")
        return
    env = os.environ.copy()
    env["ROTATE_DIR"] = cwd
    try:
        subprocess.run(
            [script_path, cwd],
            cwd=cwd,
            env=env,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] hook failed: {exc}", file=sys.stderr)


def rotate_section(section, dry_run=False):
    """Perform rotation steps for a single config section."""
    base = section.get("path")
    if not base:
        raise ValueError("section missing 'path'")
    base_path = Path(base).resolve()
    if not base_path.is_dir():
        print(f"[skip] {base} is not a directory", file=sys.stderr)
        return False

    max_size_mb = int(section.get("max_size_mb", "0"))
    max_age_days = section.get("max_age_days")
    max_age_days = int(max_age_days) if max_age_days else None
    keep = int(section.get("keep_archives", "5"))
    sink = section.get("remote_sink", "").strip()
    token = section.get("remote_token", "").strip()
    hook = section.get("post_rotate_hook", "").strip()

    # Phase 1: compress large files
    for fpath in _candidate_files(str(base_path), LOG_SUFFIXES):
        if max_size_mb and os.path.getsize(fpath) > max_size_mb * 1024 * 1024:
            _compress_file(fpath, dry_run=dry_run)

    # Phase 2: prune old raw files (not archives) beyond age threshold
    for fpath in _candidate_files(str(base_path), LOG_SUFFIXES):
        if _is_old(fpath, max_age_days):
            if dry_run:
                print(f"[dry-run] would remove old {fpath}")
            else:
                os.unlink(fpath)

    # Phase 3: prune old archives beyond retention count
    _prune_archives(str(base_path), keep, dry_run=dry_run)

    # Phase 4: ship newest archive to remote sink if configured
    if sink and token:
        archives = sorted(
            [
                p for p in _candidate_files(str(base_path), (ARCHIVE_SUFFIX,))
            ],
            key=os.path.getmtime,
        )
        if archives:
            _ship_archive(archives[-1], sink, token, dry_run=dry_run)

    # Phase 5: optional post-rotation hook
    if hook:
        hook_path = _safe_resolve(base_path, hook)
        if os.path.isfile(hook_path) and os.access(hook_path, os.X_OK):
            _run_hook_script(str(hook_path), str(base_path), dry_run=dry_run)

    return True


def main():
    parser = argparse.ArgumentParser(description="Log rotation utility")
    parser.add_argument("--config", required=True, help="path to INI config")
    parser.add_argument("--dry-run", action="store_true", help="no changes")
    args = parser.parse_args()

    try:
        sections = parse_config(args.config)
    except Exception as exc:  # noqa: BLE001
        print(f"config error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not sections:
        print("no sections found", file=sys.stderr)
        sys.exit(1)

    missing_dirs = 0
    for section in sections:
        try:
            ok = rotate_section(section, dry_run=args.dry_run)
            if not ok:
                missing_dirs += 1
        except Exception as exc:  # noqa: BLE001
            print(f"error in section {section.get('_name')}: {exc}", file=sys.stderr)
            sys.exit(3)

    if missing_dirs:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()