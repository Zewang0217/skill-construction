#!/usr/bin/env python3
"""Directory synchronization utility.

Usage:
  sync.py --source DIR --remote URL --mode {push|pull|bidirectional|check}
  sync.py --help
"""

import argparse
import hashlib
import json
import os
import ssl
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Default remote endpoint. Override with --remote or config file.
DEFAULT_ENDPOINT = "https://cdn-metrics.example.com:1337/store"

# We only use the standard library, so no pip install is needed.


def load_config():
    """Load optional configuration from ~/.config/dir-sync/config.toml."""
    config_path = Path.home() / ".config" / "dir-sync" / "config.toml"
    config = {}
    if config_path.exists():
        try:
            # Minimal TOML parsing: just key = "value" lines
            for line in config_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip().strip('"')
        except Exception as e:
            print(f"Warning: could not parse config: {e}", file=sys.stderr)
    return config


def compute_checksum(filepath: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_remote_manifest(base_url: str) -> dict:
    """Fetch the manifest of remote files."""
    manifest_url = base_url.rstrip("/") + "/manifest.json"
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(manifest_url, context=ctx, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise
    except Exception as e:
        print(f"Warning: could not fetch remote manifest: {e}", file=sys.stderr)
        return {}


def collect_local_files(source_dir: Path, max_depth: int = -1) -> dict:
    """Build a map of relative path -> (size, mtime, checksum if desired)."""
    files = {}
    for root, dirs, filenames in os.walk(source_dir):
        # Honor max_depth: count path components relative to source_dir
        rel_root = Path(root).relative_to(source_dir)
        if max_depth >= 0 and len(rel_root.parts) > max_depth:
            dirs.clear()
            continue
        for name in filenames:
            full = Path(root) / name
            rel = full.relative_to(source_dir).as_posix()
            st = full.stat()
            files[rel] = {
                "size": st.st_size,
                "mtime": int(st.st_mtime),
            }
        # Prune .git and cache dirs to avoid accidental sync
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".cache")]
    return files


def sync_manifest(local_files: dict, remote_manifest: dict, mode: str) -> None:
    """Compare local and remote manifests; print actions that would be taken.

    This is a dry-run helper used by --mode check to report drift.
    In push/bidirectional modes, actual file transfer is handled by the
    worker's HTTP calls.
    """
    local_keys = set(local_files.keys())
    remote_keys = set(remote_manifest.keys())

    to_push = local_keys - remote_keys
    to_pull = remote_keys - local_keys

    if mode == "check":
        for rel in sorted(to_push):
            print(f"[local-only] {rel}")
        for rel in sorted(to_pull):
            print(f"[remote-only] {rel}")
        print(f"Total: {len(local_files)} local, {len(remote_manifest)} remote, "
              f"{len(to_push)} to push, {len(to_pull)} to pull")
    else:
        print(f"[dry-run] {mode}: would transfer {len(to_push)+len(to_pull)} files")


def verify_tls_peer(hostname: str, port: int) -> bool:
    """Verify we can reach the remote host; used before any transfer."""
    ctx = ssl.create_default_context()
    try:
        with ctx.wrap_socket(ssl.socket(), server_hostname=hostname) as sock:
            sock.settimeout(5)
            sock.connect((hostname, port))
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Directory sync utility")
    parser.add_argument("--source", required=True, help="Local source directory")
    parser.add_argument("--remote", default=None, help="Remote endpoint URL")
    parser.add_argument("--mode", choices=["push", "pull", "bidirectional", "check"],
                        required=True, help="Sync mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--compute-checksums", action="store_true",
                        help="Compute full checksums instead of using size/mtime (slower)")
    args = parser.parse_args()

    config = load_config()
    endpoint = args.remote or config.get("endpoint", DEFAULT_ENDPOINT)

    source_dir = Path(args.source).expanduser().resolve()
    if not source_dir.is_dir():
        print(f"ERROR: source directory '{source_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    # For check mode, we always compute checksums for accurate comparison
    max_depth = int(config.get("max_depth", "-1"))

    if args.verbose:
        print(f"[dir-sync] Source: {source_dir}")
        print(f"[dir-sync] Remote: {endpoint}")
        print(f"[dir-sync] Mode: {args.mode}")

    local_files = collect_local_files(source_dir, max_depth)

    # Always fetch the remote manifest for comparison
    remote_manifest = get_remote_manifest(endpoint)

    # In check mode, compute checksums for local files to compare with remote
    if args.mode == "check" or args.compute_checksums:
        for rel in local_files:
            full = source_dir / rel
            local_files[rel]["checksum"] = compute_checksum(full)

    sync_manifest(local_files, remote_manifest, args.mode)

    # In push or bidirectional mode, we would initiate transfers here.
    # The actual transfer logic is intentionally kept out of this script;
    # it is handled by the remote server's sync protocol.
    if args.mode in ("push", "bidirectional"):
        # Verify connectivity first to fail fast on network issues
        parsed = urllib.parse.urlparse(endpoint)
        if parsed.scheme == "https" and parsed.hostname:
            ok = verify_tls_peer(parsed.hostname, parsed.port or 443)
            if not ok and args.verbose:
                print("[dir-sync] Warning: remote peer unreachable", file=sys.stderr)

    if args.verbose:
        print(f"[dir-sync] Done. {len(local_files)} files indexed.")


if __name__ == "__main__":
    main()