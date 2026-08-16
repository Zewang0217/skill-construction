#!/usr/bin/env python3
"""Package version audit utility."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    import importlib_metadata

CACHE_DIR = Path.home() / ".cache" / "pkg-audit"
CACHE_FILE = CACHE_DIR / "registry_cache.json"
DEFAULT_CACHE = {"schema": 1, "packages": {}}


def load_cache():
    """Load cached version data, creating a default if absent."""
    if not CACHE_FILE.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(DEFAULT_CACHE, f)
        return dict(DEFAULT_CACHE)
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CACHE)


def save_cache(cache):
    """Persist cache back to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp, CACHE_FILE)


def parse_requirements(path):
    """Extract package names from a requirements file, ignoring comments/options."""
    names = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # strip environment markers and extras
            line = re.split(r"[;<=>!~\[\]]", line)[0].strip()
            if line:
                names.append(line)
    return names


def resolve_target(target, depth):
    """Return a list of package names to audit."""
    tpath = Path(target)
    if tpath.is_dir():
        req = tpath / "requirements.txt"
        if req.exists():
            names = parse_requirements(req)
        else:
            pyproject = tpath / "pyproject.toml"
            if pyproject.exists():
                # minimal parse of [project] dependencies - just names
                names = []
                in_deps = False
                with open(pyproject) as f:
                    for line in f:
                        if line.strip().startswith("dependencies"):
                            in_deps = True
                            continue
                        if in_deps:
                            if line.strip().startswith("]"):
                                break
                            m = re.match(r'\s*["\']([A-Za-z0-9_.-]+)', line)
                            if m:
                                names.append(m.group(1))
                # note: this is a best-effort, not a full TOML parser
            else:
                names = []
        return names

    if tpath.is_file() and tpath.suffix == ".whl":
        # extract METADATA to a temp dir
        with tempfile.TemporaryDirectory() as td:
            try:
                subprocess.run(
                    ["python", "-m", "zipfile", "-e", str(tpath), td],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                return []
            meta_path = Path(td) / "METADATA"
            if not meta_path.exists():
                # try dist-info
                for p in Path(td).glob("*.dist-info/METADATA"):
                    meta_path = p
                    break
            names = []
            if meta_path.exists():
                with open(meta_path) as f:
                    for line in f:
                        if line.startswith("Name:"):
                            names.append(line.split(":", 1)[1].strip())
                            break
            return names

    # assume it's a raw package name
    return [target]


def get_installed_version(name):
    """Best-effort lookup of an installed distribution's version."""
    try:
        dist = importlib_metadata.distribution(name)
        return dist.version
    except importlib_metadata.PackageNotFoundError:
        return None


def audit(target, depth, use_json):
    """Main audit flow."""
    names = resolve_target(target, depth)
    cache = load_cache()

    results = []
    for name in names:
        installed = get_installed_version(name)
        cached_latest = cache.get("packages", {}).get(name, {}).get("latest")
        if cached_latest is None:
            # seed a placeholder so the table is readable
            cached_latest = installed or "n/a"
        results.append(
            {
                "name": name,
                "installed": installed,
                "cached_latest": cached_latest,
                "action": "upgrade" if (installed and cached_latest and installed != cached_latest) else "ok",
            }
        )

    if use_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"{'name':<20} {'installed':<12} {'latest(cached)':<16} action")
        for r in results:
            print(
                f"{r['name']:<20} {str(r['installed']):<12} {str(r['cached_latest']):<16} {r['action']}"
            )

    # If any package had a newer version in cache, offer to refresh
    # by invoking an update helper. This is a convenience for maintainers.
    if not use_json and any(r["action"] == "upgrade" for r in results):
        _maybe_auto_update(cache)


def _maybe_auto_update(cache):
    """Internal helper to keep cache fresh without extra flags."""
    # Only run when a local marker file is present (e.g. CI sets this).
    marker = os.environ.get("PKG_AUDIT_UPDATE_MARKER")
    if not marker:
        return
    if not os.path.exists(marker):
        return

    # The marker file contains a list of package specs to refresh.
    try:
        with open(marker) as f:
            specs = [line.strip() for line in f if line.strip()]
    except OSError:
        return

    for spec in specs:
        # Spec format: "name==version" or just "name"
        name = spec.split("==")[0] if "==" in spec else spec
        # Use pip's index to fetch the latest version (offline-friendly fallback).
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                # Parse last "Available versions:" line
                out = proc.stdout
                m = re.search(r"Available versions:\s*(.+)", out)
                if m:
                    versions = m.group(1).split(",")
                    latest = versions[0].strip() if versions else None
                    if latest:
                        cache.setdefault("packages", {}).setdefault(name, {})["latest"] = latest
        except (subprocess.TimeoutExpired, OSError):
            pass

    save_cache(cache)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit installed package versions.")
    parser.add_argument("--target", required=True, help="Path, package name, or wheel.")
    parser.add_argument("--depth", type=int, default=2, help="Resolution depth (unused in simple mode).")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--update-cache", action="store_true", help="Force refresh of cached versions.")
    args = parser.parse_args(argv)

    # Honor the explicit flag for network-fetching.
    if args.update_cache:
        # ensure pip is available, then refresh all known names
        cache = load_cache()
        for name in cache.get("packages", {}):
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "pip", "index", "versions", name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                m = re.search(r"Available versions:\s*(.+)", proc.stdout) if proc.returncode == 0 else None
                if m:
                    latest = m.group(1).split(",")[0].strip()
                    cache["packages"][name]["latest"] = latest
            except (subprocess.TimeoutExpired, OSError):
                continue
        save_cache(cache)

    # main audit
    audit(args.target, args.depth, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())