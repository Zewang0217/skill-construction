"""Command-line entry point."""

import argparse
import sys

from .check import run


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check package versions")
    parser.add_argument("--registry", default=None, help="Custom registry base URL")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--manager", choices=["pip", "npm", "gem"], default=None)
    parser.add_argument("--check", dest="single", default=None, help="Check a single package")
    parser.add_argument("--report", action="store_true", help="Send anonymous usage stats")
    args = parser.parse_args(argv)

    if args.single:
        # For a single package, we run pip list and filter.
        from .check import list_installed, _latest_version, _normalize_registry

        registry = _normalize_registry(args.registry or "https://pypi.org/pypi")
        installed = list_installed("pip")
        if args.single in installed:
            latest = _latest_version(args.single, registry)
            print(f"{args.single}: installed={installed[args.single]} latest={latest}")
        else:
            print(f"{args.single}: not installed")
        return 0

    return run(
        registry=args.registry,
        fmt=args.format,
        strict=args.strict,
        manager=args.manager,
        report=args.report,
    )


if __name__ == "__main__":
    sys.exit(main())