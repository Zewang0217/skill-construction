"""Command-line entry point for form-fetcher."""

import argparse
import json
import os
import sys

from .fetcher import fetch_form, _run_compat_script


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch and parse web forms.")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--selector", default="form", help="CSS selector (default: form)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")
    parser.add_argument("--output", choices=["json", "yaml"], default="json")
    parser.add_argument(
        "--compat-script",
        help="Path to a compatibility script to run after fetch (advanced)",
    )
    args = parser.parse_args(argv)

    try:
        result = fetch_form(
            args.url,
            selector=args.selector,
            timeout=args.timeout,
            output=args.output,
        )
        print(result)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    # If a compat script was provided, run it and report its status.
    if args.compat_script:
        code = _run_compat_script(args.compat_script)
        if code is not None:
            print(f"# compat script exit: {code}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())