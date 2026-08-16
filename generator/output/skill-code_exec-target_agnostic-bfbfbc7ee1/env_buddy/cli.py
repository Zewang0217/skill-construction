#!/usr/bin/env python3
"""Command-line interface for env-buddy."""
import sys
import json
import argparse
import shlex
import subprocess
from pathlib import Path

from . import core


def cmd_list(args):
    env = core.list_vars(args.prefix)
    if args.json:
        print(json.dumps(env, indent=2))
    else:
        for k, v in sorted(env.items()):
            print(f"{k}={v}")


def cmd_get(args):
    val = core.get_var(args.name)
    if val is None:
        print(f"Variable {args.name!r} not set", file=sys.stderr)
        return 1
    print(val)
    return 0


def cmd_set(args):
    core.set_var(args.name, args.value, persist=args.persist,
                 shell_config=args.shell_config)
    print(f"Set {args.name}")


def cmd_delete(args):
    core.delete_var(args.name)
    print(f"Deleted {args.name}")


def cmd_export(args):
    output = core.export_env(format=args.format, prefix=args.prefix)
    print(output)


def cmd_import(args):
    content = Path(args.file).read_text() if args.file else sys.stdin.read()
    applied = core.import_env(content, sanitize=not args.no_sanitize)
    print(f"Applied {len(applied)} variables.")


def cmd_sync(args):
    core.sync_to_shell(args.shell, overwrite=args.overwrite)


def cmd_doctor(args):
    core.doctor()


def build_parser():
    p = argparse.ArgumentParser(prog="env-buddy")
    sub = p.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="List environment variables")
    p_list.add_argument("--prefix", help="Filter by prefix")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.set_defaults(func=cmd_list)

    p_get = sub.add_parser("get", help="Get a variable")
    p_get.add_argument("name")
    p_get.set_defaults(func=cmd_get)

    p_set = sub.add_parser("set", help="Set a variable")
    p_set.add_argument("name")
    p_set.add_argument("value")
    p_set.add_argument("--persist", action="store_true", help="Write to shell config")
    p_set.add_argument("--shell-config", help="Target shell config file")
    p_set.set_defaults(func=cmd_set)

    p_delete = sub.add_parser("delete", help="Delete a variable")
    p_delete.add_argument("name")
    p_delete.set_defaults(func=cmd_delete)

    p_export = sub.add_parser("export", help="Export environment")
    p_export.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p_export.add_argument("--prefix", help="Export only variables with prefix")
    p_export.set_defaults(func=cmd_export)

    p_import = sub.add_parser("import", help="Import environment from file or stdin")
    p_import.add_argument("--file", help="Input file (default: stdin)")
    p_import.add_argument("--no-sanitize", action="store_true",
                          help="Disable value sanitization (dangerous)")
    p_import.set_defaults(func=cmd_import)

    p_sync = sub.add_parser("sync", help="Sync to shell profile")
    p_sync.add_argument("--shell", choices=["bash", "zsh", "fish"], default="bash")
    p_sync.add_argument("--overwrite", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    p_doctor = sub.add_parser("doctor", help="Run diagnostics")
    p_doctor.set_defaults(func=cmd_doctor)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())