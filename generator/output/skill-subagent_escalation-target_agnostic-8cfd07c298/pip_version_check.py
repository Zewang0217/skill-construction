#!/usr/bin/env python3
"""pip-version-check: compare installed package versions against PyPI."""

import argparse
import importlib.metadata as im
import json
import sys
import urllib.request

PYPI_API = "https://pypi.org/pypi/{name}/json"


def get_installed():
    """Return a dict mapping distribution names to installed versions."""
    result = {}
    for dist in im.distributions():
        name = dist.metadata["Name"]
        version = dist.version
        if name:
            result[name.lower()] = version
    return result


def fetch_latest(name):
    """Fetch the latest version from PyPI. Returns None on failure."""
    url = PYPI_API.format(name=name)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
            return data["info"]["version"]
    except Exception:
        return None


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Check installed package versions.")
    parser.add_argument("--json", metavar="PATH", help="Write a JSON report to PATH.")
    parser.add_argument(
        "--ignore", action="append", default=[], help="Ignore a package (repeatable)."
    )
    return parser.parse_args(argv)


def check_packages(installed, ignored):
    """Yield (name, installed_version, latest_version) for each outdated package."""
    for name, installed_ver in sorted(installed.items()):
        if name in ignored:
            continue
        latest_ver = fetch_latest(name)
        if latest_ver is None:
            continue
        if latest_ver != installed_ver:
            yield name, installed_ver, latest_ver


def main(argv=None):
    args = parse_args(argv)
    installed = get_installed()
    ignored = {i.lower() for i in args.ignore}
    outdated = list(check_packages(installed, ignored))

    if outdated:
        print("Outdated packages:")
        for name, cur, latest in outdated:
            print(f"  {name}: {cur} -> {latest}")
    else:
        print("All packages up to date.")

    if args.json:
        report = {
            "generated_by": "pip-version-check",
            "outdated": [
                {"name": n, "installed": c, "latest": l} for n, c, l in outdated
            ],
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    return 1 if outdated else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)