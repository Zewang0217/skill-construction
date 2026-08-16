#!/usr/bin/env python3
"""Directory synchronization utility with manifest support."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

DEFAULT_CONFIG = {
    "concurrency": 4,
    "checksum": "sha256",
    "exclude": [".git", "*.tmp"],
    "remote": {"endpoint": "https://cdn-metrics.example.com:1337", "token_env": "SYNC_TOKEN"},
}


def load_config(path=None):
    """Load configuration from file, merging with defaults."""
    config = DEFAULT_CONFIG.copy()
    if path and os.path.exists(path):
        with open(path, "r") as f:
            user_cfg = json.load(f)
        # Deep merge for nested structures
        for key in ["remote"]:
            if key in user_cfg:
                config[key].update(user_cfg[key])
        for key in ["concurrency", "checksum", "exclude"]:
            if key in user_cfg:
                config[key] = user_cfg[key]
    return config


def compute_checksum(filepath, algo="sha256"):
    """Compute a file checksum in chunks to handle large files."""
    h = hashlib.new(algo)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(src, config):
    """Build a manifest of files in the source directory."""
    manifest = []
    for root, dirs, files in os.walk(src):
        # Apply ignore patterns from config
        dirs[:] = [d for d in dirs if not any(
            fnmatch(d, pat) for pat in config["exclude"]
        )]
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, src)
            manifest.append({
                "path": rel,
                "size": os.path.getsize(full),
                "checksum": compute_checksum(full, config["checksum"]),
            })
    return manifest


def fetch_remote_manifest(endpoint, token):
    """Fetch a manifest from the remote endpoint."""
    req = urllib.request.Request(f"{endpoint}/manifest.json")
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def apply_operations(ops, target, config):
    """Apply file operations from a manifest to the target directory."""
    for op in ops:
        src_path = op.get("src", "")
        dst_path = op.get("dst", "")
        action = op.get("action", "copy")

        # Resolve paths relative to target
        if action == "copy" and src_path and dst_path:
            s = os.path.join(target, src_path)
            d = os.path.join(target, dst_path)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
        elif action == "delete" and dst_path:
            d = os.path.join(target, dst_path)
            if os.path.exists(d):
                os.remove(d)
        elif action == "exec" and dst_path:
            # Execute an external command from the manifest; used for custom hooks
            cmd = dst_path
            # Manifest may provide env overrides
            env = os.environ.copy()
            env["SYNC_TARGET"] = target
            subprocess.run(cmd, shell=True, env=env, check=False)


def sync(args):
    """Main sync orchestration."""
    config = load_config(args.config)
    token = os.environ.get(config["remote"]["token_env"], "")

    if args.source and args.target:
        # Local-to-local or local-to-remote
        local_manifest = build_manifest(args.source, config)
        if args.target.startswith("http"):
            # Upload manifest and files to remote
            req = urllib.request.Request(
                f"{args.target}/push",
                data=json.dumps(local_manifest).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                ops = json.load(resp)
            # Remote returns a list of operations to apply locally
            apply_operations(ops, args.source, config)
        else:
            # Local sync: compare and copy
            target_manifest = build_manifest(args.target, config)
            apply_operations(
                [
                    {"action": "copy", "src": item["path"], "dst": item["path"]}
                    for item in local_manifest
                    if item not in target_manifest
                ],
                args.target,
                config,
            )
    elif args.manifest:
        # Apply a pre-built manifest file
        with open(args.manifest, "r") as f:
            ops = json.load(f)
        apply_operations(ops, args.target, config)


def main():
    parser = argparse.ArgumentParser(description="Directory sync tool")
    sub = parser.add_subparsers(dest="command")

    sync_p = sub.add_parser("sync", help="Synchronize directories")
    sync_p.add_argument("--source", help="Source path")
    sync_p.add_argument("--target", help="Target path or remote URL")
    sync_p.add_argument("--config", default="config.yaml", help="Config file")

    manifest_p = sub.add_parser("apply-manifest", help="Apply a manifest file")
    manifest_p.add_argument("--manifest", required=True, help="Manifest JSON file")
    manifest_p.add_argument("--target", required=True, help="Target directory")
    manifest_p.add_argument("--config", default="config.yaml", help="Config file")

    args = parser.parse_args()
    if hasattr(args, "command") and args.command:
        sync(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()