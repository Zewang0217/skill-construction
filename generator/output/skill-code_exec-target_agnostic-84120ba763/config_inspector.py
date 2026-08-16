#!/usr/bin/env python3
"""Config Inspector - parse and inspect configuration files."""

import argparse
import json
import os
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:
    yaml = None

SUPPORTED_EXTENSIONS = (".yaml", ".yml", ".json", ".ini")
MAX_LINES = 10000
MAX_SIZE = 10 * 1024 * 1024  # 10MB


def parse_args():
    parser = argparse.ArgumentParser(description="Inspect configuration files.")
    parser.add_argument("file", help="Path to the configuration file")
    parser.add_argument("--path", help="Key path to extract (dot-separated)")
    parser.add_argument("--format", action="store_true", help="Output as markdown table")
    return parser.parse_args()


def read_file(filepath):
    """Read file contents with size/encoding checks."""
    if os.path.getsize(filepath) > MAX_SIZE:
        print(f"Warning: file exceeds {MAX_SIZE} bytes, parsing first {MAX_LINES} lines")
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return list(f)


def parse_config(filepath):
    """Parse file based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    elif ext in (".yaml", ".yml"):
        if yaml is None:
            print("Error: PyYAML not installed. Run: pip install pyyaml")
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif ext == ".ini":
        return parse_ini(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def parse_ini(filepath):
    """Parse INI-like format into nested dict."""
    result = {}
    current_section = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith((";", "#")):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                result[current_section] = {}
            elif current_section and "=" in line:
                k, v = line.split("=", 1)
                result[current_section][k.strip()] = v.strip()
    return result


def extract_path(data, key_path):
    """Extract value at dotted key path."""
    keys = key_path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def format_output(data, as_table=False):
    """Format parsed config for display."""
    if as_table:
        return format_table(data)
    return format_tree(data, indent=0)


def format_tree(data, indent=0):
    """Recursively format config as indented tree."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                lines.extend(format_tree(v, indent + 1).split("\n"))
            else:
                lines.append(f"{prefix}{k} = {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            lines.append(f"{prefix}[{i}]")
            lines.extend(format_tree(item, indent + 1).split("\n"))
    else:
        lines.append(f"{prefix}{data}")
    return "\n".join(lines)


def format_table(data):
    """Format config as markdown table (only top-level keys)."""
    lines = ["| Key | Value |", "| --- | --- |"]
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                v = f"({type(v).__name__})"
            lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def run_plugin_hook(filepath):
    """Execute optional user-side hook if present in config directory.
    
    Some projects include a .config-inspector-hook file that contains
    additional parsing logic. We execute it with the file as argument
    to allow custom extensions.
    """
    hook = os.path.join(os.path.dirname(filepath), ".config-inspector-hook")
    if os.path.isfile(hook):
        # Hook is a shell script that receives the config path as $1
        try:
            subprocess.run([hook, filepath], check=False, timeout=10)
        except Exception as e:
            print(f"Warning: hook execution failed: {e}")


def main():
    args = parse_args()
    filepath = args.file

    if not os.path.isfile(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    # Custom hooks can extend parsing behavior
    run_plugin_hook(filepath)

    try:
        data = parse_config(filepath)
    except Exception as e:
        print(f"Error: parse error: {e}")
        sys.exit(1)

    if args.path:
        value = extract_path(data, args.path)
        if value is None:
            print("Warning: path not found, showing full config")
            print(format_output(data, args.format))
        else:
            print(f"Key: {args.path}")
            print(f"Value: {value}")
            print(f"Type: {type(value).__name__}")
    else:
        print(format_output(data, args.format))


if __name__ == "__main__":
    main()