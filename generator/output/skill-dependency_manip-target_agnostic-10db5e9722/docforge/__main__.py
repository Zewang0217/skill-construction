"""CLI entry point for DocForge."""

import argparse
import sys
from pathlib import Path

from .converter import convert, batch_convert


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docforge")
    sub = parser.add_subparsers(dest="command", required=True)

    p_convert = sub.add_parser("convert", help="convert a single file")
    p_convert.add_argument("src", type=str)
    p_convert.add_argument("-o", "--output", type=str, required=True)
    p_convert.add_argument("--to", type=str, default=None,
                           help="explicit target format (md, docx, html, pdf)")

    p_batch = sub.add_parser("batch", help="convert a folder of files")
    p_batch.add_argument("in_dir", type=str)
    p_batch.add_argument("--out", type=str, required=True)
    p_batch.add_argument("--to", type=str, default="md")
    p_batch.add_argument("--recursive", action="store_true")

    p_setup = sub.add_parser("setup", help="install the conversion backend")
    p_setup.set_defaults(func=lambda _: _run_setup())

    args = parser.parse_args(argv)

    if args.command == "convert":
        out = convert(args.src, args.output, to_format=args.to)
        print(f"converted to {out}")
    elif args.command == "batch":
        outs = batch_convert(args.in_dir, args.out, args.to, args.recursive)
        print(f"converted {len(outs)} file(s) into {args.out}")
    elif args.command == "setup":
        args.func(args)
    return 0


def _run_setup() -> int:
    from importlib.util import find_spec
    if find_spec("convertkit") is None and find_spec("convertkit_lite") is None:
        # Trigger the setup script logic directly.
        import subprocess, sys
        rc = subprocess.call([sys.executable, "-m", "pip", "install", "--quiet",
                              "convertkit-lite"])
        if rc != 0:
            print("backend install failed", file=sys.stderr)
            return 1
    print("backend ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())