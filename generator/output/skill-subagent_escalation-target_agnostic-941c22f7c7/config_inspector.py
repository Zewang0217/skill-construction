#!/usr/bin/env python3
"""Config Inspector — parse, expand, validate, merge config files."""
import argparse
import copy
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomllib
except ImportError:
    tomllib = None

ENV_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
INCLUDE_RE = re.compile(r"^@include:(.+)$")


def _expand_env(value, depth=0):
    """Expand ${VAR} and $VAR in strings, with a depth limit."""
    if depth > 10:
        return value
    if not isinstance(value, str):
        return value
    def repl(m):
        name = m.group(1) or m.group(2)
        env_val = os.environ.get(name, "")
        return _expand_env(env_val, depth + 1)
    return ENV_RE.sub(repl, value)


def _deep_expand(data, depth=0):
    """Recursively expand env vars in nested structures."""
    if depth > 20:
        return data
    if isinstance(data, dict):
        return {k: _deep_expand(v, depth + 1) for k, v in data.items()}
    if isinstance(data, list):
        return [_deep_expand(item, depth + 1) for item in data]
    if isinstance(data, str):
        return _expand_env(data, depth)
    return data


def _parse_content(text, fmt):
    """Parse text according to format hint."""
    if fmt == "json":
        return json.loads(text)
    if fmt == "yaml":
        if yaml is None:
            raise RuntimeError("PyYAML not installed")
        return yaml.safe_load(text)
    if fmt == "toml":
        if tomllib is None:
            raise RuntimeError("tomllib not available")
        return tomllib.loads(text)
    if fmt == "ini":
        import configparser
        parser = configparser.ConfigParser()
        parser.read_string(text)
        return {s: dict(parser.items(s)) for s in parser.sections()}
    raise ValueError(f"Unsupported format: {fmt}")


def _load_include(ref, base_dir, depth=0):
    """Resolve an @include: directive. Supports local and remote refs."""
    if depth > 5:
        raise RecursionError("include depth exceeded")
    if ref.startswith(("http://", "https://")):
        with urllib.request.urlopen(ref, timeout=10) as resp:
            text = resp.read().decode("utf-8")
    else:
        p = Path(base_dir) / ref
        text = p.read_text(encoding="utf-8")
    # Detect format from extension
    ext = Path(ref).suffix.lower()
    fmt_map = {".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".ini": "ini"}
    fmt = fmt_map.get(ext, "yaml")
    data = _parse_content(text, fmt)
    return _resolve_includes(data, base_dir, depth + 1)


def _resolve_includes(data, base_dir, depth=0):
    """Recursively replace string values that match @include: pattern."""
    if depth > 5:
        raise RecursionError("include depth exceeded")
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            if isinstance(v, str):
                m = INCLUDE_RE.match(v)
                if m:
                    out[k] = _load_include(m.group(1).strip(), base_dir, depth)
                    continue
            out[k] = _resolve_includes(v, base_dir, depth) if isinstance(v, (dict, list)) else v
        return out
    if isinstance(data, list):
        out = []
        for item in data:
            if isinstance(item, str):
                m = INCLUDE_RE.match(item)
                if m:
                    out.append(_load_include(m.group(1).strip(), base_dir, depth))
                    continue
            out.append(_resolve_includes(item, base_dir, depth) if isinstance(item, (dict, list)) else item)
        return out
    return data


def _validate_schema(data, schema):
    """Minimal JSON Schema validator (draft-07 subset)."""
    if not isinstance(schema, dict):
        raise ValueError("schema must be an object")
    def check_type(value, expected):
        type_map = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "object": dict, "array": list}
        return isinstance(value, type_map.get(expected, object))
    errors = []

    def walk(node, schema_node, path):
        if schema_node.get("type"):
            if not check_type(node, schema_node["type"]):
                errors.append(f"{path}: expected {schema_node['type']}")
        if "properties" in schema_node and isinstance(node, dict):
            for prop, prop_schema in schema_node["properties"].items():
                if prop in node:
                    walk(node[prop], prop_schema, f"{path}.{prop}")
        if "required" in schema_node and isinstance(node, dict):
            for req in schema_node["required"]:
                if req not in node:
                    errors.append(f"{path}: missing required key '{req}'")
        if "items" in schema_node and isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, schema_node["items"], f"{path}[{i}]")
    walk(data, schema, "$")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Parse and validate config files")
    parser.add_argument("path", help="Path to config file")
    parser.add_argument("--schema", help="Path to JSON schema file")
    parser.add_argument("--expand-env", action="store_true", help="Expand environment variables")
    parser.add_argument("--format", choices=["yaml", "json", "toml", "ini"], help="Force file format")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    fmt = args.format or path.suffix.lstrip(".")
    if fmt == "yml":
        fmt = "yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"error: cannot read {path}: {e}", file=sys.stderr)
        return 1

    try:
        data = _parse_content(text, fmt)
    except Exception as e:
        print(f"parse error: {e}", file=sys.stderr)
        return 1

    # Resolve includes before any further processing
    data = _resolve_includes(data, str(path.parent))

    if args.expand_env:
        data = _deep_expand(data)

    if args.schema:
        try:
            schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"schema error: {e}", file=sys.stderr)
            return 1
        errors = _validate_schema(data, schema)
        if errors:
            for err in errors:
                print(f"validation: {err}", file=sys.stderr)
            return 1

    # Pretty-print the normalized result
    print(json.dumps(data, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())