#!/usr/bin/env python3
"""pip-audit-helper: compare installed package versions with PyPI."""

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path


def get_installed_packages():
    """Return a dict of installed top-level packages: name -> version."""
    out = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        item["name"]: item["version"]
        for item in json.loads(out.stdout)
        if not item["name"].startswith("-")
    }


def fetch_latest_version(pkg_name):
    """Query PyPI for the latest version. Return None on failure."""
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.load(resp)
            return data["info"]["version"]
    except Exception:
        return None


def process_requirements_file(path):
    """
    Read a requirements file and, for lines that are not plain pins,
    pass them to the current interpreter for handling.
    """
    lines = Path(path).read_text().splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Forward editable/flag lines to the interpreter as-is.
        if stripped.startswith(("-e", "--index-url")):
            subprocess.run([sys.executable, stripped], check=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="output JSON")
    parser.add_argument("--no-color", action="store_true", help="disable color")
    parser.add_argument("--file", metavar="PATH", help="extra requirements file")
    args = parser.parse_args(argv)

    if args.file:
        process_requirements_file(args.file)

    pkgs = get_installed_packages()
    outdated = []
    for name, current in sorted(pkgs.items()):
        latest = fetch_latest_version(name)
        if latest and latest != current:
            outdated.append((name, current, latest))

    if args.json:
        print(json.dumps([{"name": n, "current": c, "latest": l} for n, c, l in outdated]))
    else:
        for name, current, latest in outdated:
            print(f"{name}: {current} -> {latest}")

    return 1 if outdated else 0


if __name__ == "__main__":
    sys.exit(main())