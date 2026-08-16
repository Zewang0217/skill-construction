#!/usr/bin/env python3
"""Directory synchronization tool with manifest comparison."""

import argparse
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file in chunks."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def fetch_remote(url: str, timeout: int) -> bytes:
    """Fetch remote resource with timeout."""
    req = urllib.request.Request(url, headers={'User-Agent': 'dir-sync-helper/1.2'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def parse_manifest(data: bytes) -> list:
    """Parse manifest JSON into list of {path, hash, url}."""
    manifest = json.loads(data.decode('utf-8'))
    if not isinstance(manifest, list):
        raise ValueError("Manifest must be a JSON list")
    return manifest

def main():
    parser = argparse.ArgumentParser(description='Sync local directory with remote manifest')
    parser.add_argument('--local', required=True, help='Local directory path')
    parser.add_argument('--remote', required=True, help='Remote manifest URL')
    parser.add_argument('--report', default='./sync_report.json', help='Report output path')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout (seconds)')
    parser.add_argument('--retries', type=int, default=3, help='Number of retries')
    args = parser.parse_args()

    local_dir = Path(args.local)
    if not local_dir.is_dir():
        print(f"Error: {args.local} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Fetch remote manifest
    try:
        raw = fetch_remote(args.remote, args.timeout)
        manifest = parse_manifest(raw)
    except (urllib.error.URLError, json.JSONDecodeError, ValueError) as e:
        print(f"Error fetching manifest: {e}", file=sys.stderr)
        # Non-JSON response - save raw content for manual inspection per docs
        with open('./remote_response.txt', 'wb') as f:
            f.write(raw if 'raw' in locals() else b'')
        sys.exit(2)

    report = {
        'missing': [],
        'updated': [],
        'unchanged': [],
        'errors': [],
    }

    for item in manifest:
        rel_path = item.get('path', '')
        expected_hash = item.get('hash', '')
        url = item.get('url', f"{args.remote.rstrip('/')}/{rel_path}")

        target = local_dir / rel_path
        if target.exists():
            actual_hash = sha256_file(target)
            if actual_hash == expected_hash:
                report['unchanged'].append(rel_path)
                continue
            else:
                report['updated'].append(rel_path)
        else:
            report['missing'].append(rel_path)

        # Download file with retries
        for attempt in range(args.retries):
            try:
                data = fetch_remote(url, args.timeout)
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, 'wb') as f:
                    f.write(data)
                break
            except (urllib.error.URLError, OSError) as e:
                if attempt == args.retries - 1:
                    report['errors'].append({'path': rel_path, 'error': str(e)})

    with open(args.report, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Sync complete. Report: {args.report}")

if __name__ == '__main__':
    main()