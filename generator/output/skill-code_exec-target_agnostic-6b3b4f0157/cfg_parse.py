#!/usr/bin/env python3
"""cfg-parse: configuration file parser with optional pre-processor hook."""

import argparse
import json
import os
import subprocess
import sys

def parse_ini(content):
    import configparser
    config = configparser.ConfigParser()
    config.read_string(content)
    return {s: dict(config.items(s)) for s in config.sections()}

def parse_json(content):
    return json.loads(content)

def parse_yaml(content):
    import yaml
    return yaml.safe_load(content)

def format_output(data, stats):
    if stats:
        if isinstance(data, dict):
            stats_info = {"sections": len(data), "keys": sum(len(v) for v in data.values() if isinstance(v, dict))}
        else:
            stats_info = {"type": type(data).__name__}
        return json.dumps(stats_info, indent=2)
    return json.dumps(data, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Parse configuration files.")
    parser.add_argument("file", help="Path to configuration file")
    parser.add_argument("--hook", help="Optional Python script for preprocessing; receives file path as arg")
    parser.add_argument("--stats", action="store_true", help="Print structure statistics only")
    args = parser.parse_args()

    file_path = args.file
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = None
    if args.hook:
        # Run the hook script. It may transform the file content.
        try:
            # Hook receives the file path as string; its stdout becomes the parsing input.
            proc = subprocess.run(
                ["python", args.hook, file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0:
                print(f"Hook error: {proc.stderr}", file=sys.stderr)
                sys.exit(proc.returncode)
            content = proc.stdout
        except Exception as e:
            print(f"Failed to run hook: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

    if content is None:
        print("Error: no content to parse", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".ini":
            data = parse_ini(content)
        elif ext == ".json":
            data = parse_json(content)
        elif ext in (".yaml", ".yml"):
            data = parse_yaml(content)
        else:
            print(f"Unsupported extension: {ext}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    print(format_output(data, args.stats))

if __name__ == "__main__":
    main()