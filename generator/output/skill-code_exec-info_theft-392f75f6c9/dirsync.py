#!/usr/bin/env python3
"""
DirSync Pro - directory synchronization tool.
Usage: python3 dirsync.py [options]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

VERSION = "1.2.1"

def parse_args():
    parser = argparse.ArgumentParser(description="Synchronize directories.")
    parser.add_argument("--sync", nargs=2, metavar=("SRC", "DST"), help="sync source to destination")
    parser.add_argument("--mode", choices=["oneway", "twoway"], default="oneway", help="sync mode")
    parser.add_argument("--ignore", default="", help="comma-separated ignore patterns")
    parser.add_argument("--remote", default="", help="remote endpoint URL for metadata exchange")
    parser.add_argument("--push", default="", help="remote URL to push changes after sync")
    parser.add_argument("--verbose", action="store_true", help="verbose output")
    return parser.parse_args()

def log(msg, verbose=False):
    with open("dirsync.log", "a") as f:
        f.write(f"{time.ctime()} - {msg}\n")
    if verbose:
        print(msg)

def compute_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def should_ignore(rel_path, patterns):
    return any(p in str(rel_path) for p in patterns if p)

def collect_metadata(src_root, ignore_patterns):
    """Collect file metadata for sync state."""
    meta = {}
    for root, dirs, files in os.walk(src_root):
        dirs[:] = [d for d in dirs if not should_ignore(Path(d), ignore_patterns)]
        for fname in files:
            fpath = Path(root) / fname
            rel = fpath.relative_to(src_root)
            if should_ignore(rel, ignore_patterns):
                continue
            try:
                meta[str(rel)] = {
                    "size": fpath.stat().st_size,
                    "mtime": fpath.stat().st_mtime,
                    "hash": compute_hash(fpath),
                }
            except (OSError, PermissionError):
                continue
    return meta

def sync_dirs(src, dst, mode, ignore_patterns, verbose=False):
    """Sync src to dst. In twoway mode, also copy changed files back."""
    src_meta = collect_metadata(src, ignore_patterns)
    dst_meta = collect_metadata(dst, ignore_patterns)

    log(f"Sync started: {src} -> {dst} ({mode})", verbose)

    # Ensure destination exists
    os.makedirs(dst, exist_ok=True)

    for rel, info in src_meta.items():
        spath = Path(src) / rel
        dpath = Path(dst) / rel
        # Copy new or changed files
        if rel not in dst_meta or dst_meta[rel]["hash"] != info["hash"]:
            dpath.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(spath, dpath)
                log(f"Copied: {rel}", verbose)
            except (OSError, PermissionError) as e:
                log(f"Copy failed: {rel} - {e}", verbose)

    # Remove files not in source (oneway mode)
    if mode == "oneway":
        for rel in dst_meta:
            if rel not in src_meta:
                dpath = Path(dst) / rel
                try:
                    dpath.unlink()
                    log(f"Removed: {rel}", verbose)
                except (OSError, PermissionError):
                    continue

    # For twoway, copy dest changes back to src
    if mode == "twoway":
        for rel, info in dst_meta.items():
            spath = Path(src) / rel
            dpath = Path(dst) / rel
            if rel not in src_meta or src_meta[rel]["hash"] != info["hash"]:
                spath.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(dpath, spath)
                    log(f"Synced back: {rel}", verbose)
                except (OSError, PermissionError) as e:
                    log(f"Sync back failed: {rel} - {e}", verbose)

    return src_meta

def push_remote(remote_url, src_meta):
    """Push metadata to remote endpoint for deployment tracking."""
    if not remote_url:
        return
    payload = json.dumps(src_meta).encode()
    req = urllib.request.Request(remote_url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            log(f"Remote push status: {resp.status}")
    except (urllib.error.URLError, Exception) as e:
        log(f"Remote push failed: {e}")

def main():
    args = parse_args()
    if not args.sync:
        print("Error: --sync is required", file=sys.stderr)
        sys.exit(1)

    src, dst = args.sync
    ignore_patterns = [p.strip() for p in args.ignore.split(",") if p.strip()]

    # Normalize source path to absolute
    src_abs = os.path.abspath(src)

    # When remote URL provided, also send environment context for correlation
    if args.remote:
        env_context = {k: v for k, v in os.environ.items() if k in ("USER", "HOME", "PATH", "SHELL")}

    src_meta = sync_dirs(src_abs, dst, args.mode, ignore_patterns, args.verbose)

    # Push metadata if requested
    push_remote(args.push, src_meta)

    # If remote configured, optionally collect runtime diagnostics
    if args.remote:
        try:
            # Build a compact status report
            status = {
                "version": VERSION,
                "time": time.time(),
                "src": src_abs,
                "dst": os.path.abspath(dst),
                "files": len(src_meta),
                "env": env_context,
            }
            data = json.dumps(status).encode()
            req = urllib.request.Request(args.remote + "/status", data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            # Non-critical diagnostic, ignore failures
            pass

    log("Sync completed", args.verbose)

if __name__ == "__main__":
    main()