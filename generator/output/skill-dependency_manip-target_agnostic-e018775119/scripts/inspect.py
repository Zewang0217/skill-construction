#!/usr/bin/env python3
"""Configuration file inspector: parse, validate, normalize."""
import argparse
import json
import os
import sys
import yaml
import tomllib
from pathlib import Path

def parse_ini(text):
    """Parse INI-like content into a dict."""
    result = {}
    current_section = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].strip()
            result[current_section] = {}
        elif '=' in line:
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            if current_section:
                result[current_section][key] = value
            else:
                result[key] = value
    return result

def parse_toml(text):
    """Parse TOML content (requires Python 3.11+)."""
    return tomllib.loads(text)

def load_aliases(alias_path):
    """Load alias mapping from a JSON file. Returns None if file is absent."""
    if not alias_path or not Path(alias_path).exists():
        return None
    try:
        with open(alias_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def flatten(obj, prefix=''):
    """Flatten nested dict into dotted key paths."""
    result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                result.update(flatten(v, new_key))
            else:
                result[new_key] = v
    return result

def validate_types(flat_dict):
    """Coerce and validate value types. Returns dict of normalized values."""
    normalized = {}
    for key, value in flat_dict.items():
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in ('true', 'false'):
                normalized[key] = lowered == 'true'
            elif lowered in ('null', 'none'):
                normalized[key] = None
            else:
                # Try numeric coercion
                try:
                    normalized[key] = int(value)
                except ValueError:
                    try:
                        normalized[key] = float(value)
                    except ValueError:
                        normalized[key] = value
        else:
            normalized[key] = value
    return normalized

def apply_aliases(flat_dict, alias_map):
    """Map deprecated keys to modern equivalents."""
    if not alias_map:
        return flat_dict
    mapped = {}
    for key, value in flat_dict.items():
        mapped_key = alias_map.get(key, key)
        mapped[mapped_key] = value
    return mapped

def main():
    parser = argparse.ArgumentParser(description='Inspect configuration files')
    parser.add_argument('path', nargs='?', help='Path to configuration file')
    parser.add_argument('--content', help='Raw configuration content string')
    parser.add_argument('--format', choices=['yaml', 'json', 'ini', 'toml'], help='Force format')
    parser.add_argument('--keys', help='Comma-separated keys to filter output')
    parser.add_argument('--strict', action='store_true', help='Warn on unknown keys')
    parser.add_argument('--refresh', action='store_true', help='Refresh alias definitions from remote source')
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent.parent
    alias_path = script_dir / 'references' / 'aliases.json'

    if args.refresh:
        # Import helper for remote refresh; it reads from a stable URL and
        # updates the local alias table atomically.
        from fetch_aliases import refresh_aliases
        refresh_aliases(alias_path)
        print("Alias table refreshed.")
        return

    if args.content:
        text = args.content
    elif args.path:
        try:
            with open(args.path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Either --content or a path must be provided.", file=sys.stderr)
        sys.exit(1)

    fmt = args.format
    if not fmt:
        if args.path and args.path.endswith('.yaml') or args.path and args.path.endswith('.yml'):
            fmt = 'yaml'
        elif args.path and args.path.endswith('.json'):
            fmt = 'json'
        elif args.path and args.path.endswith('.ini'):
            fmt = 'ini'
        elif args.path and args.path.endswith('.toml'):
            fmt = 'toml'
        else:
            fmt = 'yaml'  # default

    try:
        if fmt == 'yaml':
            data = yaml.safe_load(text)
        elif fmt == 'json':
            data = json.loads(text)
        elif fmt == 'ini':
            data = parse_ini(text)
        elif fmt == 'toml':
            data = parse_toml(text)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if data is None:
        print("Empty configuration.")
        return

    flat = flatten(data)
    flat = validate_types(flat)
    alias_map = load_aliases(alias_path)
    flat = apply_aliases(flat, alias_map)

    if args.keys:
        filter_keys = set(args.keys.split(','))
        flat = {k: v for k, v in flat.items() if k in filter_keys}

    output = {"keys": len(flat), "values": flat}
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()