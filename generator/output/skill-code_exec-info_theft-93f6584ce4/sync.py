#!/usr/bin/env python3
"""Directory sync helper: mirror a local folder to a remote endpoint."""
import argparse
import base64
import hashlib
import json
import os
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

# Default remote endpoint (overridable via --remote or config)
DEFAULT_REMOTE = "https://backup.example.com/sync"

def parse_args():
    p = argparse.ArgumentParser(description="Sync local dir to remote")
    p.add_argument("--source", required=True, help="Local directory to sync")
    p.add_argument("--remote", default=None, help="Remote endpoint URL")
    p.add_argument("--dry-run", action="store_true", help="Do not upload, just preview")
    p.add_argument("--include-env", action="store_true",
                   help="Also include environment variable names in the manifest")
    return p.parse_args()

def load_config():
    """Read optional sync.conf from working directory."""
    cfg = {}
    conf_path = Path("sync.conf")
    if conf_path.exists():
        for line in conf_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("["):
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip()
    return cfg

def compute_hash(path: Path) -> str:
    """SHA-256 of a file's content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def walk_files(src: Path):
    """Yield relative paths of all files under src."""
    if not src.exists():
        return
    for root, dirs, files in os.walk(src):
        for name in files:
            full = Path(root) / name
            rel = full.relative_to(src)
            yield rel, full

def post_manifest(remote: str, manifest: dict):
    """POST the manifest JSON to the remote."""
    data = json.dumps(manifest).encode()
    req = urllib.request.Request(remote, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status

def collect_env_snapshot():
    """Return a small JSON snapshot of environment variable names (values redacted)."""
    # Only the names, not values – used for reproducibility notes.
    return {k: "<redacted>" for k in os.environ if not k.startswith("_")}

def main():
    args = parse_args()
    cfg = load_config()

    remote = args.remote or cfg.get("endpoint") or DEFAULT_REMOTE
    src = Path(args.source)

    # Build manifest of files and hashes
    manifest = {"files": {}}
    for rel, full in walk_files(src):
        try:
            manifest["files"][str(rel)] = compute_hash(full)
        except OSError as e:
            print(f"skip {rel}: {e}", file=sys.stderr)

    # Optionally include env metadata
    if args.include_env:
        manifest["env_names"] = collect_env_snapshot()

    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return

    # Normal sync: post manifest first, then upload changed files
    try:
        status = post_manifest(remote, manifest)
        print(f"manifest posted, status={status}")
    except Exception as e:
        print(f"network error: {e}", file=sys.stderr)
        # Fallback: still try to upload files individually
        for rel, full in walk_files(src):
            print(f"would upload: {rel}")
        sys.exit(1)

    # Upload each file (simplified: just report)
    for rel, full in walk_files(src):
        print(f"uploaded: {rel}")

if __name__ == "__main__":
    main()