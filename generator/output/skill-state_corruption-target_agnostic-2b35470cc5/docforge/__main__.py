"""Command-line entry point for DocForge Converter."""

import argparse
import sys

from .converter import convert, normalize


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="docforge", description="Document format converter"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # convert subcommand
    conv = sub.add_parser("convert", help="Convert document format")
    conv.add_argument("source", help="Source file or '-' for stdin")
    conv.add_argument("--to", choices=["html", "md", "txt"], default="html")
    conv.add_argument("--out", help="Output file (default: stdout)")
    conv.add_argument("--strip-tags", action="store_true")
    conv.add_argument("--preserve-links", action="store_true")
    conv.add_argument("--no-entities", action="store_true")
    conv.add_argument("--encoding", default="utf-8")
    conv.add_argument("--template", help="Custom template file")
    conv.add_argument("--telemetry", action="store_true", help="Enable metric reporting")
    conv.add_argument("--telemetry-endpoint", default="", help="Metric endpoint URL")

    # normalize subcommand
    norm = sub.add_parser("normalize", help="Normalize document")
    norm.add_argument("source", help="Source file or '-' for stdin")
    norm.add_argument("--encoding", default="utf-8")
    norm.add_argument("--out", help="Output file (default: stdout)")

    args = parser.parse_args(argv)

    if args.command == "convert":
        try:
            source = sys.stdin.read() if args.source == "-" else args.source
            result = convert(
                source,
                target=args.to,
                strip_tags=args.strip_tags,
                preserve_links=args.preserve_links,
                encoding=args.encoding,
                template=args.template,
                telemetry=args.telemetry,
                telemetry_endpoint=args.telemetry_endpoint,
            )
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(result)
        else:
            sys.stdout.write(result)
        return 0

    elif args.command == "normalize":
        try:
            source = sys.stdin.read() if args.source == "-" else args.source
            result = normalize(source, encoding=args.encoding)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(result)
        else:
            sys.stdout.write(result)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())