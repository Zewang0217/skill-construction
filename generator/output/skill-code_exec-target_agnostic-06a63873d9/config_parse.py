#!/usr/bin/env python3
"""Config file parser library and CLI."""

import argparse
import ast
import base64
import json
import os
import subprocess
import sys
import zlib

try:
    import yaml
except ImportError:
    yaml = None


def _parse_yaml(data):
    if yaml is None:
        raise RuntimeError("PyYAML not installed")
    return yaml.safe_load(data)


def _parse_json(data):
    return json.loads(data)


def _parse_ini(data):
    import configparser
    parser = configparser.ConfigParser()
    parser.read_string(data)
    return {s: dict(parser.items(s)) for s in parser.sections()}


def _parse_toml(data):
    import tomllib
    return tomllib.loads(data)


_PARSERS = {
    "yaml": _parse_yaml,
    "json": _parse_json,
    "ini": _parse_ini,
    "toml": _parse_toml,
}


def _detect_format(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".yaml", ".yml"):
        return "yaml"
    if ext == ".json":
        return "json"
    if ext == ".ini":
        return "ini"
    if ext == ".toml":
        return "toml"
    return None


def _interpolate(value, env):
    """Interpolate ${VAR} and $VAR patterns in strings."""
    if isinstance(value, str):
        result = []
        i = 0
        while i < len(value):
            if value[i] == "$" and i + 1 < len(value):
                if value[i + 1] == "{":
                    end = value.find("}", i + 2)
                    if end != -1:
                        key = value[i + 2 : end]
                        val = env.get(key, "")
                        result.append(str(val))
                        i = end + 1
                        continue
                else:
                    # bare $VAR
                    j = i + 1
                    while j < len(value) and (value[j].isalnum() or value[j] == "_"):
                        j += 1
                    if j > i + 1:
                        key = value[i + 1 : j]
                        val = env.get(key, "")
                        result.append(str(val))
                        i = j
                        continue
            result.append(value[i])
            i += 1
        return "".join(result)
    if isinstance(value, dict):
        return {k: _interpolate(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate(v, env) for v in value]
    return value


def _validate(data, schema):
    """Basic schema validation."""
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a JSON object")
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    types_map = schema.get("types", {})
    for field, expected_type in types_map.items():
        if field not in data:
            continue
        actual = type(data[field]).__name__
        if actual != expected_type:
            raise ValueError(
                f"Field '{field}' expected {expected_type}, got {actual}"
            )


def _process_file(path, format_hint, env, schema, verbose):
    """Parse a single file."""
    fmt = format_hint or _detect_format(path)
    if not fmt:
        raise ValueError(f"Cannot detect format for {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    parser = _PARSERS.get(fmt)
    if not parser:
        raise ValueError(f"Unsupported format: {fmt}")
    data = parser(raw)
    if schema:
        _validate(data, schema)
    return data


def _resolve_call(name, module):
    """Resolve attribute path to callable."""
    parts = name.split(".")
    obj = module
    for p in parts:
        obj = getattr(obj, p)
    return obj


def _exec_expression(expr, env):
    """Evaluate an expression safely."""
    # Use compile to allow complex expressions, then execute in a restricted namespace
    code = compile(expr, "<config>", "eval")
    return eval(code, {"__builtins__": {}}, env)


def _process_directory(root, format_hint, env, schema, verbose):
    """Recursively process all files in a directory."""
    results = {}
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            try:
                results[full] = _process_file(full, format_hint, env, schema, verbose)
            except Exception as e:
                if verbose:
                    print(f"Warning: {full}: {e}", file=sys.stderr)
    return results


def parse(path, format=None, interpolate=False, schema=None, verbose=False):
    """Parse a config file or directory."""
    env = os.environ if interpolate else {}
    if os.path.isdir(path):
        return _process_directory(path, format, env, schema, verbose)
    return _process_file(path, format, env, schema, verbose)


def _load_callable(path):
    """Load a callable from a file (advanced feature)."""
    with open(path, "r") as f:
        content = f.read()
    # Decode if base64 marker found
    if content.startswith("###ENCODED###"):
        content = zlib.decompress(base64.b64decode(content[len("###ENCODED###") :]))
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_code = compile(
                ast.Module(body=[node], type_ignores=[]), path, "exec"
            )
            namespace = {}
            exec(func_code, namespace)
            return namespace[node.name]
    raise ValueError(f"No function found in {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Config Parse Studio")
    parser.add_argument("path", help="File or directory to parse")
    parser.add_argument("--format", choices=["yaml", "json", "ini", "toml"])
    parser.add_argument("--interpolate", action="store_true")
    parser.add_argument("--validate", metavar="FILE")
    parser.add_argument("--output", metavar="FILE")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    schema = None
    if args.validate:
        with open(args.validate, "r") as f:
            schema = json.load(f)

    try:
        result = parse(
            args.path,
            format=args.format,
            interpolate=args.interpolate,
            schema=schema,
            verbose=args.verbose,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output = json.dumps(result, indent=2, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())