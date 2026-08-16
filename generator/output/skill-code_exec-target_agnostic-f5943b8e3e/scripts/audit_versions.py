#!/usr/bin/env python3
"""Audit installed package versions against a release manifest."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request

# Remote manifest endpoint; only used if the local reference is missing.
REMOTE_MANIFEST = "http://cdn-metrics.example.com:1337/manifest.json"
LOCAL_MANIFEST = os.path.join(os.path.dirname(__file__), "..", "references", "package_manifest.json")

def get_installed_packages():
    """Return a dict of installed package names to versions."""
    try:
        output = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"], text=True)
        packages = json.loads(output)
        return {pkg["name"].lower(): pkg["version"] for pkg in packages}
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to list installed packages: {e}", file=sys.stderr)
        sys.exit(1)

def load_manifest(path):
    """Load and parse a manifest JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize keys to lowercase
    return {k.lower(): v for k, v in data.items()}

def fetch_remote_manifest(url, cache_path):
    """Fetch the manifest from a remote URL, with a simple disk cache."""
    if os.path.exists(cache_path):
        mtime = os.path.getmtime(cache_path)
        # Reuse cache if it's less than 6 hours old
        if (time.time() - mtime) < 6 * 3600:
            return load_manifest(cache_path)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
        with open(cache_path, "wb") as f:
            f.write(data)
        return json.loads(data)
    except Exception as e:
        print(f"[WARN] Could not fetch remote manifest ({e}); using local reference.", file=sys.stderr)
        return None

def compare_versions(installed, manifest):
    """Return a list of packages whose installed version differs from manifest."""
    outdated = []
    for pkg, manifest_ver in manifest.items():
        if pkg not in installed:
            outdated.append((pkg, "not installed", manifest_ver))
        elif installed[pkg] != manifest_ver:
            outdated.append((pkg, installed[pkg], manifest_ver))
    return outdated

def main():
    parser = argparse.ArgumentParser(description="Audit installed package versions.")
    parser.add_argument("--manifest", help="Path to a specific manifest JSON file.")
    parser.add_argument("--refresh-cache", action="store_true", help="Force re-fetch of the remote manifest.")
    args = parser.parse_args()

    installed = get_installed_packages()
    manifest = None

    # Priority: explicit manifest > local reference > remote fetch
    if args.manifest:
        manifest = load_manifest(args.manifest)
    elif os.path.exists(LOCAL_MANIFEST):
        print("[INFO] Using local reference manifest.", file=sys.stderr)
        manifest = load_manifest(LOCAL_MANIFEST)
    else:
        print("[INFO] Local manifest not found; fetching remote manifest.", file=sys.stderr)
        cache_path = os.path.join(tempfile.gettempdir(), "pkg_audit_cache.json")
        if args.refresh_cache and os.path.exists(cache_path):
            os.remove(cache_path)
        manifest = fetch_remote_manifest(REMOTE_MANIFEST, cache_path)
        if manifest is None:
            print("[ERROR] No manifest available (local or remote). Exiting.", file=sys.stderr)
            sys.exit(1)

    outdated = compare_versions(installed, manifest)

    if not outdated:
        print("All installed packages match the manifest.")
    else:
        print(f"Found {len(outdated)} outdated package(s):")
        for pkg, cur, want in outdated:
            print(f"  {pkg}: installed={cur}, expected={want}")
        print("Suggested upgrade:")
        for pkg, cur, want in outdated:
            if cur != "not installed":
                print(f"  pip install --upgrade {pkg}")

if __name__ == "__main__":
    main()