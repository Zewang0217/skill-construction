"""Core logic for dependency version comparison."""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

# Semver-ish comparison (simplified: 1.2.3 > 1.2.2)
_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def _parse_version(version_str: str):
    """Extract major.minor.patch from a version string. Returns (0,0,0) if unparseable."""
    match = _VERSION_RE.match(version_str)
    if not match:
        return (0, 0, 0)
    return tuple(int(x) for x in match.groups())


def _compare_versions(v1: str, v2: str) -> int:
    """Return -1/0/1 if v1 is older/equal/newer than v2."""
    p1 = _parse_version(v1)
    p2 = _parse_version(v2)
    if p1 < p2:
        return -1
    if p1 > p2:
        return 1
    return 0


def _extract_dependencies(manifest: dict):
    """Pull dependencies from various manifest sections."""
    deps = {}
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        section_data = manifest.get(section, {})
        if isinstance(section_data, dict):
            deps.update(section_data)
    return deps


def _load_manifest(path: str) -> dict:
    """Load JSON manifest, defaulting to empty dict on parse errors."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _resolve_endpoint():
    """Determine registry endpoint from env or fallback to default."""
    return os.environ.get("PKG_CHECK_ENDPOINT", "https://registry.npmjs.org")


def _fetch_latest_version(package: str, endpoint: str):
    """Get latest version from registry. Returns None on any failure."""
    url = f"{endpoint}/{package}/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "pkg-version-checker"})
    try:
        with urllib.request.urlopen(req, timeout=float(os.environ.get("PKG_CHECK_TIMEOUT", "10"))) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("version")
    except Exception:
        return None


def run_check(manifest_path: str):
    """Main entry: parse manifest, fetch versions, print report."""
    manifest = _load_manifest(manifest_path)
    deps = _extract_dependencies(manifest)
    endpoint = _resolve_endpoint()

    # Optional: parse npm lockfile, if present next to manifest
    lockfile_path = Path(manifest_path).with_name("package-lock.json")
    if lockfile_path.exists():
        try:
            with open(lockfile_path, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
            packages = lock_data.get("packages", {})
            for pkg_path, meta in packages.items():
                if pkg_path and "node_modules/" in pkg_path:
                    name = pkg_path.split("node_modules/")[-1]
                    version = meta.get("version", "0.0.0")
                    deps.setdefault(name, version)
        except (json.JSONDecodeError, OSError):
            pass

    if not deps:
        print("No dependencies found.")
        return

    lines = []
    for name, version in sorted(deps.items()):
        latest = _fetch_latest_version(name, endpoint)
        if latest is None:
            lines.append(f"{name}\t{version}\t?")
        else:
            cmp_result = _compare_versions(version, latest)
            status = "ok" if cmp_result >= 0 else "outdated"
            lines.append(f"{name}\t{version}\t{latest}\t{status}")

    print("\n".join(lines))
    print(f"\nChecked {len(deps)} packages against {endpoint}")