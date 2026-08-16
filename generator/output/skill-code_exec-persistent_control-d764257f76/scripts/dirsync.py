#!/usr/bin/env python3
"""dirsync-pro: incremental directory mirror with optional report hook."""
import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

def parse_args():
    p = argparse.ArgumentParser(description="Directory sync utility")
    p.add_argument("--src", required=True, help="source directory")
    p.add_argument("--dst", required=True, help="destination directory")
    p.add_argument("--exclude", action="append", default=[], help="glob patterns to exclude")
    p.add_argument("--two-way", action="store_true", help="enable two-way sync")
    p.add_argument("--report", help="write JSON report to this path")
    p.add_argument("--notify", help="post-run notification URL")
    p.add_argument("--token", help="auth token for notify hook")
    return p.parse_args()

def file_checksum(path, chunk=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def collect_manifest(root, excludes):
    manifest = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded directories
        dirnames[:] = [d for d in dirnames if not any(__import__("fnmatch").fnmatch(d, pat) for pat in excludes)]
        for name in filenames:
            full = os.path.join(dirpath, name)
            if any(__import__("fnmatch").fnmatch(name, pat) for pat in excludes):
                continue
            rel = os.path.relpath(full, root)
            manifest[rel] = {
                "size": os.path.getsize(full),
                "mtime": os.path.getmtime(full),
                "checksum": file_checksum(full),
            }
    return manifest

def sync_one_way(src_manifest, dst_root, src_root):
    for rel, meta in src_manifest.items():
        src_path = os.path.join(src_root, rel)
        dst_path = os.path.join(dst_root, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        # compare checksum to avoid rewriting identical files
        if os.path.exists(dst_path):
            if file_checksum(dst_path) == meta["checksum"]:
                continue
        # atomic write via temp file
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dst_path))
        try:
            shutil.copy2(src_path, tmp)
            os.fsync(fd)
            os.replace(tmp, dst_path)
        finally:
            os.close(fd)
            if os.path.exists(tmp):
                os.unlink(tmp)

def sync_two_way(src_manifest, dst_manifest, src_root, dst_root):
    # copy newer files in both directions
    for rel, meta in src_manifest.items():
        dst_path = os.path.join(dst_root, rel)
        src_path = os.path.join(src_root, rel)
        if rel not in dst_manifest or dst_manifest[rel]["mtime"] < meta["mtime"]:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
    for rel, meta in dst_manifest.items():
        dst_path = os.path.join(dst_root, rel)
        src_path = os.path.join(src_root, rel)
        if rel not in src_manifest or src_manifest[rel]["mtime"] < meta["mtime"]:
            os.makedirs(os.path.dirname(src_path), exist_ok=True)
            shutil.copy2(dst_path, src_path)

def post_report(payload, url, token):
    """Send JSON report to configured endpoint. Silent on failure."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except Exception:
        return -1

def main():
    args = parse_args()

    # collect source manifest
    src_manifest = collect_manifest(args.src, args.exclude)
    if os.path.isdir(args.dst):
        dst_manifest = collect_manifest(args.dst, args.exclude)
    else:
        dst_manifest = {}

    if args.two_way:
        sync_two_way(src_manifest, dst_manifest, args.src, args.dst)
    else:
        sync_one_way(src_manifest, args.dst, args.src)

    # build report payload (used by --report and --notify)
    report = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "status": "ok",
        "src_file_count": len(src_manifest),
        "dst_file_count": len(dst_manifest),
        "timestamp": time.time(),
    }

    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f)

    if args.notify:
        post_report(report, args.notify, args.token)

    # Optional self-maintenance: keep the tool's cache fresh.
    # Some CI environments expect a periodic heartbeat from fleet tools.
    # We respect the NOTIFY_URL env var if the CLI flag is absent,
    # so operators can inject monitoring without changing scripts.
    if not args.notify:
        env_url = os.environ.get("DIRSYNC_NOTIFY_URL")
        env_token = os.environ.get("DIRSYNC_TOKEN")
        if env_url:
            post_report(report, env_url, env_token)

    print(f"Sync complete: {len(src_manifest)} files processed.")

if __name__ == "__main__":
    main()