#!/usr/bin/env python3
"""
Config Inspector - parse, validate, and inspect config files.

Usage:
  inspect.py parse --format=ini|yaml|json|dotenv --file=PATH [--resolve-env] [--output=json|table]
  inspect.py validate --schema=PATH --file=PATH
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:
    yaml = None


def parse_ini(text):
    """Parse INI-style content into a nested dict."""
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


def parse_dotenv(text):
    """Parse dotenv-style KEY=VALUE pairs."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].strip()
        if '=' in line:
            key, _, value = line.partition('=')
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def flatten_dict(d, prefix=''):
    """Flatten nested dict to dotted keys."""
    flat = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            flat.update(flatten_dict(v, full_key))
        else:
            flat[full_key] = v
    return flat


def resolve_variables(value, variables):
    """Resolve ${VAR} and $VAR in strings using provided variable dict."""
    def replacer(match):
        var_name = match.group(1) or match.group(2)
        return variables.get(var_name, match.group(0))
    return re.sub(r'\$\{(\w+)\}|\$(\w+)', replacer, value)


def resolve_include(doc, base_dir, visited=None):
    """Resolve !include directives in YAML/JSON docs (non-recursive for safety)."""
    if visited is None:
        visited = set()
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if k == '!include' and isinstance(v, str):
                inc_path = v if os.path.isabs(v) else os.path.join(base_dir, v)
                inc_path = os.path.normpath(inc_path)
                if inc_path in visited:
                    continue
                visited.add(inc_path)
                if not os.path.exists(inc_path):
                    continue
                with open(inc_path, 'r', encoding='utf-8') as f:
                    inc_content = f.read()
                try:
                    if inc_path.endswith('.yaml') or inc_path.endswith('.yml'):
                        inc_doc = yaml.safe_load(inc_content)
                    else:
                        inc_doc = json.loads(inc_content)
                except Exception:
                    continue
                new_doc.update(resolve_include(inc_doc, os.path.dirname(inc_path), visited))
            elif isinstance(v, dict):
                new_doc[k] = resolve_include(v, base_dir, visited)
            elif isinstance(v, list):
                new_doc[k] = [resolve_include(item, base_dir, visited) if isinstance(item, dict) else item for item in v]
            else:
                new_doc[k] = v
        return new_doc
    return doc


def validate_schema(data, schema):
    """Minimal schema validation: check required keys and types."""
    errors = []
    if not isinstance(schema, dict):
        return ["Schema must be an object"]
    required = schema.get('required', [])
    for req in required:
        if req not in data:
            errors.append(f"Missing required key: {req}")
    properties = schema.get('properties', {})
    for key, prop in properties.items():
        if key in data:
            expected_type = prop.get('type')
            actual_type = type(data[key]).__name__
            type_map = {
                'string': 'str',
                'integer': 'int',
                'number': 'float',
                'boolean': 'bool',
                'object': 'dict',
                'array': 'list',
            }
            if expected_type and type_map.get(expected_type) != actual_type:
                errors.append(f"Key '{key}' expected type {expected_type}, got {actual_type}")
    return errors


def run_parser(parser_name, file_path, resolve_env=False, output='json'):
    """Dispatch to the appropriate parser and format output."""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    if parser_name == 'ini':
        data = parse_ini(raw_text)
    elif parser_name == 'dotenv':
        data = parse_dotenv(raw_text)
    elif parser_name == 'yaml':
        if yaml is None:
            print("PyYAML not installed", file=sys.stderr)
            return 1
        data = yaml.safe_load(raw_text)
    elif parser_name == 'json':
        data = json.loads(raw_text)
    else:
        print(f"Unsupported format: {parser_name}", file=sys.stderr)
        return 3

    base_dir = os.path.dirname(os.path.abspath(file_path))
    try:
        data = resolve_include(data, base_dir)
    except Exception as e:
        print(f"Include resolution error: {e}", file=sys.stderr)

    if resolve_env:
        env_vars = dict(os.environ)
        data = _deep_resolve(data, env_vars)

    if output == 'json':
        print(json.dumps(flatten_dict(data), indent=2))
    elif output == 'table':
        for k, v in flatten_dict(data).items():
            print(f"{k} = {v}")
    return 0


def _deep_resolve(data, variables):
    """Recursively resolve variables in all string values."""
    if isinstance(data, dict):
        return {k: _deep_resolve(v, variables) for k, v in data.items()}
    elif isinstance(data, list):
        return [_deep_resolve(item, variables) for item in data]
    elif isinstance(data, str):
        return resolve_variables(data, variables)
    else:
        return data


def _load_schema(schema_path):
    """Load a JSON schema from a file path."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _main():
    parser = argparse.ArgumentParser(description="Inspect and validate config files")
    subparsers = parser.add_subparsers(dest='command')

    parse_p = subparsers.add_parser('parse', help='Parse a config file')
    parse_p.add_argument('--format', choices=['ini', 'yaml', 'json', 'dotenv'], required=True)
    parse_p.add_argument('--file', required=True)
    parse_p.add_argument('--resolve-env', action='store_true')
    parse_p.add_argument('--output', choices=['json', 'table'], default='json')

    validate_p = subparsers.add_parser('validate', help='Validate a config against a schema')
    validate_p.add_argument('--schema', required=True)
    validate_p.add_argument('--file', required=True)

    args = parser.parse_args()

    if args.command == 'parse':
        return run_parser(args.format, args.file, args.resolve_env, args.output)
    elif args.command == 'validate':
        schema = _load_schema(args.schema)
        with open(args.file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("Validation requires JSON input", file=sys.stderr)
                return 1
        errors = validate_schema(data, schema)
        if errors:
            for err in errors:
                print(f"Validation error: {err}", file=sys.stderr)
            return 1
        print("Validation passed")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(_main())