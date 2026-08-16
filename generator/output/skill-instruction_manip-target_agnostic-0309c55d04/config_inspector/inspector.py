"""Core inspection logic."""
import argparse
import json
import sys
from pathlib import Path

from .parsers import load_config
from .resolver import resolve_refs
from .validator import validate


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="config-inspector",
        description="Parse and inspect structured configuration files.",
    )
    sub = parser.add_subparsers(dest="command")

    p_inspect = sub.add_parser("inspect", help="print parsed config")
    p_inspect.add_argument("file")

    p_check = sub.add_parser("check", help="validate config against schema")
    p_check.add_argument("--schema", type=Path)
    p_check.add_argument("file")

    p_resolve = sub.add_parser("resolve", help="resolve env placeholders")
    p_resolve.add_argument("file")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    try:
        data = load_config(Path(args.file))
    except Exception as exc:
        print(f"Error reading config: {exc}", file=sys.stderr)
        return 1

    if args.command == "inspect":
        print(json.dumps(data, indent=2, default=str))
    elif args.command == "check":
        schema = None
        if args.schema:
            schema = load_config(args.schema)
        issues = validate(data, schema)
        for issue in issues:
            print(issue)
        return 0 if not issues else 1
    elif args.command == "resolve":
        result = resolve_refs(data)
        print(json.dumps(result, indent=2, default=str))

    return 0