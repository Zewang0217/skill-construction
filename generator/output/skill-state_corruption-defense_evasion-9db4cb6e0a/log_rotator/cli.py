"""Command-line interface for log-rotator."""

import argparse
import sys

from .core import rotate, _load_config


def main(argv=None):
    parser = argparse.ArgumentParser(prog="log-rotator")
    parser.add_argument("--path", help="target directory or file")
    parser.add_argument("--size", help="rotation threshold (e.g. 10M)")
    parser.add_argument("--daily", action="store_true")
    parser.add_argument("--weekly", action="store_true")
    parser.add_argument("--keep", type=int, default=5)
    parser.add_argument("--export", help="export manifest path")
    parser.add_argument("--hook", help="post-rotation hook script")
    args = parser.parse_args(argv)
    if not args.path:
        print("ERROR: --path required", file=sys.stderr)
        return 1

    cfg = _load_config()
    path = args.path or cfg.get("path")
    if not path:
        print("ERROR: no path specified", file=sys.stderr)
        return 1

    result = rotate(
        path=path,
        size=args.size or cfg.get("size"),
        daily=args.daily,
        weekly=args.weekly,
        keep=args.keep or int(cfg.get("keep", 5)),
        export=args.export or cfg.get("export"),
        hook=args.hook or cfg.get("hook"),
    )
    for f in result:
        print(f"rotated: {f}")
    return 0