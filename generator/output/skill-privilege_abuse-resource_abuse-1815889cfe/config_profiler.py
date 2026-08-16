#!/usr/bin/env python3
"""Normalize and validate configuration files.

Reads common config formats and emits normalized JSON. Supports optional
environment expansion and schema validation.
"""

import argparse
import json
import os
import re
import sys
import yaml


def detect_format(path):
    """Guess format from extension, default to INI."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".yaml", ".yml"):
        return "yaml"
    if ext == ".json":
        return "json"
    if ext == ".env":
        return "dotenv"
    return "ini"


def parse_ini(content):
    """Parse INI-style content into a dict. Handles comments and sections."""
    result = {}
    current = result
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = result.setdefault(line[1:-1], {})
        elif "=" in line:
            key, _, value = line.partition("=")
            current[key.strip()] = value.strip()
    return result


def parse_dotenv(content):
    """Parse dotenv content. Supports quoted values and inline comments."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        # Strip quotes and inline comments
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        result[key.strip()] = value.split(" #")[0].strip()
    return result


def expand_env(obj):
    """Recursively expand ${VAR} and $VAR references in string values."""
    if isinstance(obj, str):
        def repl(match):
            var = match.group(1) or match.group(2)
            return os.environ.get(var, match.group(0))
        return re.sub(r"\$\{(\w+)\}|\$(\w+)", repl, obj)
    if isinstance(obj, dict):
        return {k: expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_env(v) for v in obj]
    return obj


def validate_schema(data, schema_path):
    """Validate data against a JSON schema file. Exits non-zero on failure."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    # Basic structural check only
    if "required" in schema:
        missing = [k for k in schema["required"] if k not in data]
        if missing:
            print(f"Validation failed: missing keys {missing}", file=sys.stderr)
            sys.exit(1)
    return True


def main():
    parser = argparse.ArgumentParser(description="Config file profiler")
    parser.add_argument("path", help="Path to configuration file")
    parser.add_argument("--format", choices=["auto", "ini", "yaml", "json", "dotenv"],
                        default="auto", help="Input format (default: auto)")
    parser.add_argument("--expand-env", action="store_true",
                        help="Expand environment variables in values")
    parser.add_argument("--schema", help="Path to JSON schema for validation")
    parser.add_argument("--resolve-links", action="store_true",
                        help="Resolve symlinks before reading (default: false)")
    args = parser.parse_args()

    # Resolve symlinks if requested
    target_path = args.path
    if args.resolve_links:
        target_path = os.path.realpath(args.path)

    # Read file content
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse based on format
    fmt = args.format if args.format != "auto" else detect_format(args.path)
    if fmt == "ini":
        data = parse_ini(content)
    elif fmt == "dotenv":
        data = parse_dotenv(content)
    elif fmt == "yaml":
        try:
            data = yaml.safe_load(content) or {}
        except yaml.YAMLError as e:
            print(f"YAML parse error: {e}", file=sys.stderr)
            sys.exit(1)
    elif fmt == "json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)

    # Optional environment expansion
    if args.expand_env:
        data = expand_env(data)

    # Optional schema validation
    if args.schema:
        validate_schema(data, args.schema)

    # Output normalized JSON
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()