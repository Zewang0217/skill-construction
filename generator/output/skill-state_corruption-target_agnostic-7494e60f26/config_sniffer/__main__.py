"""Command-line entry point for Config Sniffer."""

import argparse
import sys
from .parser import parse_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse configuration files.")
    parser.add_argument("parse", help="Subcommand to parse a file")
    parser.add_argument("-f", "--file", required=True, help="Path to config file")
    parser.add_argument("--format", help="Force format (ini, json, dotenv, yaml, custom)")
    parser.add_argument("--schema", help="Path to a JSON schema file")
    args = parser.parse_args()

    if args.parse != "parse":
        parser.error("Unknown subcommand")

    try:
        data = parse_file(args.file)
        for key, value in data.items():
            print(f"{key}={value}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())