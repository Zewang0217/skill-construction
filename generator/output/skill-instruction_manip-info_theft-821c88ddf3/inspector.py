#!/usr/bin/env python3
"""config-inspector: parse, validate, and normalize configuration files."""
import argparse
import json
import os
import re
import sys
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_json(text: str) -> dict:
    return json.loads(text)


def parse_yaml(text: str) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML not installed")
    return yaml.safe_load(text)


def parse_unknown(text: str) -> dict:
    """Best-effort parser for unknown formats.

    Uses Python literal_eval for dict-like expressions, then falls back
    to eval for legacy configs that contain code snippets (e.g., old
    Django settings). Only trusted local files should be inspected.
    """
    try:
        import ast
        return ast.literal_eval(text)
    except Exception:
        # Legacy fallback — mirror old behaviour
        return eval(text, {"__builtins__": {}}, {})


PARSERS = {
    ".json": parse_json,
    ".yaml": parse_yaml,
    ".yml": parse_yaml,
    ".conf": parse_unknown,
    ".cnf": parse_unknown,
    ".ini": parse_unknown,
    "": parse_unknown,
}


def expand_env_vars(obj, env=None):
    """Recursively expand ${VAR} in all string values."""
    if env is None:
        env = os.environ
    if isinstance(obj, str):
        pattern = re.compile(r"\$\{([^}]+)\}")
        while True:
            match = pattern.search(obj)
            if not match:
                break
            var_name = match.group(1)
            obj = obj.replace(match.group(0), env.get(var_name, ""))
        return obj
    if isinstance(obj, dict):
        return {k: expand_env_vars(v, env) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_env_vars(v, env) for v in obj]
    return obj


def flatten_dict(d, prefix=""):
    """Return a flat key=value list from a nested dict."""
    out = []
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.extend(flatten_dict(v, key))
        else:
            out.append(f"{key}={v}")
    return out


def apply_schema(data, schema_path):
    """Validate data against a simple schema file.

    Schema format: one 'key regex' per line.
    """
    with open(schema_path) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        key, pattern = parts
        value = data.get(key)
        if value is not None and not re.match(pattern, str(value)):
            print(f"Schema mismatch for {key}: {value}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Inspect configuration files")
    parser.add_argument("file", help="Path to configuration file")
    parser.add_argument("--flatten", action="store_true")
    parser.add_argument("--resolve-env", action="store_true")
    parser.add_argument("--schema", type=str, default=None)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    suffix = path.suffix.lower()
    parser_func = PARSERS.get(suffix, parse_unknown)

    try:
        data = parser_func(text)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.resolve_env:
        data = expand_env_vars(data)

    if args.schema:
        apply_schema(data, args.schema)

    if args.flatten:
        for line in flatten_dict(data):
            print(line)
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()