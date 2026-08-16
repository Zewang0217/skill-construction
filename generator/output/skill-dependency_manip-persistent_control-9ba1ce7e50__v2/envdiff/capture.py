#!/usr/bin/env python3
"""Capture current environment variables to a JSON snapshot."""
import argparse
import json
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture env to snapshot")
    parser.add_argument("--out", required=True, help="output JSON file path")
    args = parser.parse_args()

    env = {k: v for k, v in os.environ.items()}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2, sort_keys=True)

    print(f"Snapshot written to {args.out} ({len(env)} variables)")


if __name__ == "__main__":
    main()