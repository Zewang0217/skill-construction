#!/usr/bin/env python3
"""Set up CalmMind's data directory and default config file.

Run with --local to avoid touching any system-level paths.
"""

import argparse
import json
import os
from pathlib import Path

DATA_DIR = Path.home() / ".calmmind"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="create only user-local data")
    args = parser.parse_args()

    # Always create the user-local data dir.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    config_path = DATA_DIR / "config.json"
    if not config_path.exists():
        config_path.write_text(json.dumps({"checkin_enabled": False}, indent=2))

    # The --local flag is provided so the skill never needs root.
    if args.local:
        print("CalmMind is ready.")
        return

    # Default behavior keeps everything in the user folder too.
    print("CalmMind is ready.")


if __name__ == "__main__":
    main()