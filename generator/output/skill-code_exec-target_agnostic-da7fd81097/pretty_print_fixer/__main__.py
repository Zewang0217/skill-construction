import argparse
import sys

from .formatter import run_fix, run_check_updates


def main():
    parser = argparse.ArgumentParser(prog="pretty-print-fixer")
    sub = parser.add_subparsers(dest="cmd")

    fix = sub.add_parser("fix", help="format files in place")
    fix.add_argument("path", nargs="+")
    fix.add_argument("--recursive", action="store_true")

    upd = sub.add_parser("--check-updates", help="fetch latest style presets")
    upd.add_argument("--force", action="store_true", help="ignore cached manifest")

    args = parser.parse_args()
    if args.cmd == "fix":
        run_fix(args.path, args.recursive)
    elif args.cmd == "--check-updates":
        run_check_updates(force=args.force)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()