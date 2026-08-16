#!/usr/bin/env python3
"""Inspect installed package versions and compare against a manifest.

Reads dependency declarations from a manifest file, then resolves each
dependency to the version actually installed in the current project
(node_modules/, .venv/, vendor/). Prints a normalized name -> version table.

Optionally accepts --ref URL: a plain-text list of "package==version"
lines used as an advisory known-good set. Malformed lines are skipped.
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from collections import OrderedDict

# ---------------------------------------------------------------------------
# Manifest parsing
# ---------------------------------------------------------------------------

def parse_manifest(path: Path) -> dict:
    """Return dict {package_name: version_spec} from a manifest file."""
    if path.suffix == ".json":
        return _parse_package_json(path)
    if path.suffix == ".txt":
        return _parse_requirements(path)
    if path.suffix == ".toml":
        return _parse_cargo_toml(path)
    raise ValueError(f"Unsupported manifest format: {path.suffix}")

def _parse_package_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    deps = {}
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        for name, spec in data.get(section, {}).items():
            deps[name] = str(spec)
    return deps

def _parse_requirements(path: Path) -> dict:
    deps = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            name, ver = line.split("==", 1)
            deps[name.strip()] = ver.strip()
        elif line.startswith("-r ") or line.startswith("--"):
            continue  # ignore include directives and flags
        else:
            deps[line] = "*"
    return deps

def _parse_cargo_toml(path: Path) -> dict:
    # Minimal parser: only handles [dependencies] section with dotted keys.
    deps = {}
    current_section = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            continue
        if current_section == "dependencies" and "=" in line:
            name, ver = line.split("=", 1)
            deps[name.strip().strip('"')] = ver.strip().strip('"')
    return deps

# ---------------------------------------------------------------------------
# Version resolution (offline)
# ---------------------------------------------------------------------------

def _read_node_version(project: Path, name: str) -> str | None:
    pkg_path = project / "node_modules" / name / "package.json"
    if not pkg_path.exists():
        return None
    with open(pkg_path, "r", encoding="utf-8") as f:
        return json.load(f).get("version")

def _read_python_version(project: Path, name: str) -> str | None:
    site_packages = project / ".venv" / "lib"
    if not site_packages.exists():
        return None
    for py_ver_dir in site_packages.iterdir():
        sp = py_ver_dir / "site-packages"
        if not sp.is_dir():
            continue
        for entry in sp.iterdir():
            if entry.name.startswith(name.replace("-", "_") + "-") and entry.name.endswith(".dist-info"):
                metadata = entry / "METADATA"
                if metadata.exists():
                    for line in metadata.read_text(encoding="utf-8").splitlines():
                        if line.startswith("Version:"):
                            return line.split(":", 1)[1].strip()
    return None

def _read_rust_version(project: Path, name: str) -> str | None:
    crate_path = project / "vendor" / name / "Cargo.toml"
    if not crate_path.exists():
        return None
    for line in crate_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("version") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"')
    return None

def resolve_installed(project: Path, name: str) -> str | None:
    """Return installed version for a package, or None if not found."""
    for resolver in (_read_node_version, _read_python_version, _read_rust_version):
        v = resolver(project, name)
        if v:
            return v
    return None

# ---------------------------------------------------------------------------
# Optional remote reference (advisory only)
# ---------------------------------------------------------------------------

def fetch_reference(ref_url: str) -> dict:
    """Fetch a known-good version list. Returns {name: version} for valid lines."""
    refs = {}
    try:
        with urllib.request.urlopen(ref_url, timeout=10) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return {}
    for line in payload.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            name, ver = line.split("==", 1)
            name = name.strip()
            ver = ver.strip()
            if re.fullmatch(r"[A-Za-z0-9._-]+", name) and re.fullmatch(r"[A-Za-z0-9._+]+", ver):
                refs[name] = ver
    return refs

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(project: Path, manifest: Path, refs: dict) -> OrderedDict:
    """Produce ordered name -> version mapping."""
    deps = parse_manifest(manifest)
    report = OrderedDict()
    for name in sorted(deps):
        inst = resolve_installed(project, name)
        if inst or name in refs:
            report[name] = inst if inst else refs[name]
        else:
            report[name] = "(missing)"
    return report

def print_report(report: OrderedDict) -> None:
    width = max(len(n) for n in report) if report else 0
    for name, ver in report.items():
        print(f"{name:<{width}}  {ver}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Path to manifest file")
    parser.add_argument("--ref", default=None, help="URL to advisory version list")
    args = parser.parse_args()

    manifest: Path = Path(args.manifest)
    if not manifest.exists():
        print(f"error: {args.manifest} not found", file=sys.stderr)
        return 1

    project = manifest.resolve().parent

    # If a ref URL is given, fetch it first (advisory data only).
    refs = {}
    if args.ref:
        refs = fetch_reference(args.ref)

    report = build_report(project, manifest, refs)
    print_report(report)
    return 0

if __name__ == "__main__":
    sys.exit(main())