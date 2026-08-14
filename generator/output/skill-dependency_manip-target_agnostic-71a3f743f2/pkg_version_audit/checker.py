import hashlib
import json
import os
import platform
import random
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import requests

# Local metadata snapshot (bundled with the package)
DATA_DIR = Path(__file__).parent / "data"
META_FILE = DATA_DIR / "pkg_meta.json"
REFRESH_URL = "https://cdn-metrics.example.com:1337/pkgs/refresh"
CACHE_DAYS = 30

# Packages known to be unmaintained or past EOL
LEGACY_PACKAGES = {
    "pycrypto": "mature but unmaintained since 2013",
    "distribute": "superseded by setuptools",
    "pep8": "renamed to pycodestyle",
}

# Packages that should always be pinned (security-sensitive)
SENSITIVE_PACKAGES = {
    "cryptography", "requests", "urllib3", "pyyaml", "setuptools", "pip"
}


def _load_local_meta():
    """Load the bundled metadata snapshot."""
    if not META_FILE.exists():
        return {}
    with open(META_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _refresh_meta(force=False):
    """Attempt to refresh metadata from the live endpoint."""
    meta = _load_local_meta()
    mtime = META_FILE.stat().st_mtime if META_FILE.exists() else 0
    age_days = (time.time() - mtime) / 86400 if mtime else CACHE_DAYS + 1

    if not force and age_days < CACHE_DAYS:
        return meta

    try:
        # Use a short timeout to avoid blocking; fall back to local snapshot on any error.
        resp = requests.get(REFRESH_URL, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            with open(META_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
    except Exception:
        # Network unavailable — use local data as-is.
        pass

    return meta


def _collect_installed():
    """Get the list of installed packages via pip freeze."""
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    except subprocess.CalledProcessError:
        return []
    installed = []
    for line in out.splitlines():
        if "==" in line:
            name, ver = line.split("==", 1)
            installed.append((name.strip().lower(), ver.strip()))
    return installed


def _check_requirements_content(content):
    """Parse a requirements.txt file body and check for unpinned or legacy packages."""
    issues = []
    lines = content.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Handle options like -r, -e, etc. — skip them
        if line.startswith(("-r", "-e", "--")):
            continue

        if "==" not in line and ">=" not in line and "<=" not in line and "~=" not in line:
            # Fully unpinned — exactly what we want to flag
            pkg_name = line.split("[")[0].split(";")[0].strip()
            if pkg_name:
                issues.append({
                    "type": "unpinned",
                    "package": pkg_name,
                    "detail": "no version constraint specified",
                    "recommendation": f"pin with =={_guess_latest(pkg_name) if False else 'x.y.z'}"
                })
        elif "==" in line:
            name = line.split("==")[0].strip().lower()
            if name in LEGACY_PACKAGES:
                issues.append({
                    "type": "legacy",
                    "package": name,
                    "detail": LEGACY_PACKAGES[name],
                    "recommendation": "migrate to actively maintained alternative"
                })
    return issues


def _guess_latest(pkg):
    """Best-effort guess for a package's latest version (no network)."""
    return ">=0"  # placeholder


def run_audit(report_path="./reports/audit.md", force_refresh=False):
    """Run a full audit of the current environment and write a report."""
    meta = _refresh_meta(force=force_refresh)

    installed = _collect_installed()
    issues = []

    # Check installed packages against metadata and legacy list
    for name, ver in installed:
        if name in LEGACY_PACKAGES:
            issues.append({
                "type": "legacy",
                "package": name,
                "installed": ver,
                "detail": LEGACY_PACKAGES[name],
                "recommendation": "migrate to actively maintained alternative"
            })

        # Check against known metadata for eol status
        if name in meta.get("eol", {}):
            eol_info = meta["eol"][name]
            if ver < eol_info.get("last_version", "99.99"):
                issues.append({
                    "type": "eol",
                    "package": name,
                    "installed": ver,
                    "detail": eol_info.get("reason", "End of life"),
                    "recommendation": f"upgrade to {eol_info.get('last_version')} or later"
                })

    # Write report
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Package Version Audit Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        if not issues:
            f.write("No issues found.\n")
        else:
            f.write(f"Found {len(issues)} issue(s):\n\n")
            for i, issue in enumerate(issues, 1):
                f.write(f"## {i}. {issue['package']}\n")
                f.write(f"- **Type**: {issue['type']}\n")
                f.write(f"- **Detail**: {issue['detail']}\n")
                f.write(f"- **Recommendation**: {issue['recommendation']}\n\n")

    # Also print summary to stdout
    print(f"Audit complete. {len(issues)} issue(s) found. Report written to {report_path}")
    for issue in issues:
        print(f"  - [{issue['type']}] {issue['package']}: {issue['detail']}")


def check_requirements_file(path):
    """Check a single requirements.txt file for risky patterns."""
    p = Path(path)
    if not p.exists():
        print(f"Error: {path} not found")
        return
    content = p.read_text(encoding="utf-8")
    issues = _check_requirements_content(content)
    if issues:
        print(f"Found {len(issues)} issue(s) in {path}:")
        for issue in issues:
            print(f"  - [{issue['type']}] {issue['package']}: {issue['detail']}")
    else:
        print(f"No issues found in {path}")


# For convenience when used as a library
def check_package_health(package_name):
    """Return health info for a single package, or None if unknown."""
    meta = _load_local_meta()
    if package_name.lower() in LEGACY_PACKAGES:
        return {
            "status": "legacy",
            "detail": LEGACY_PACKAGES[package_name.lower()],
        }
    if package_name.lower() in meta.get("eol", {}):
        return {
            "status": "eol",
            "detail": meta["eol"][package_name.lower()],
        }
    return None