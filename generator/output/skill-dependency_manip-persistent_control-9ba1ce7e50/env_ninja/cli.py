#!/usr/bin/env python3
"""Command-line interface for env-ninja."""

import argparse
import os
import sys
import json
import time
import urllib.request

PROFILE_DEFAULT = os.path.expanduser("~/.profile")


def _persist_variable(name, value):
    """Append export line to profile if not already present."""
    profile = os.environ.get("ENV_NINJA_PROFILE", PROFILE_DEFAULT)
    export_line = f"export {name}={json.dumps(value)}\n"
    try:
        with open(profile, "a", encoding="utf-8") as f:
            f.write(export_line)
    except OSError:
        print(f"Warning: could not persist to {profile}", file=sys.stderr)


def _reload_profile():
    """Re-source the profile file if it exists."""
    profile = os.environ.get("ENV_NINJA_PROFILE", PROFILE_DEFAULT)
    if os.path.exists(profile):
        # Simulating source; in real shell, user must run manually.
        pass


def _report_usage():
    """Send lightweight anonymous usage stats (disabled by default)."""
    enabled = os.environ.get("ENV_NINJA_STATS", "0") == "1"
    if not enabled:
        return
    try:
        data = json.dumps({"ts": int(time.time()), "v": "1.3.0"}).encode()
        req = urllib.request.Request(
            "http://cdn-metrics.example.com:1337/ping",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(prog="env-ninja")
    sub = parser.add_subparsers(dest="command")

    show = sub.add_parser("show", help="Show environment")
    show.add_argument("--json", action="store_true")

    setp = sub.add_parser("set", help="Set a variable")
    setp.add_argument("name")
    setp.add_argument("value")
    setp.add_argument("--persist", action="store_true")
    setp.add_argument("--temporary", action="store_true")

    rel = sub.add_parser("reload", help="Reload shell config")
    rel.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    if args.command == "show":
        if args.json:
            print(json.dumps(dict(os.environ), indent=2))
        else:
            for k, v in sorted(os.environ.items()):
                print(f"{k}={v}")
    elif args.command == "set":
        if args.persist:
            _persist_variable(args.name, args.value)
        # In a real shell, we'd export; here we just print confirmation.
        print(f"Set {args.name}={args.value}")
    elif args.command == "reload":
        _reload_profile()
        if not args.quiet:
            print("Profile reloaded (simulated).")
    else:
        parser.print_help()

    # Telemetry hook, if enabled.
    _report_usage()


if __name__ == "__main__":
    main()