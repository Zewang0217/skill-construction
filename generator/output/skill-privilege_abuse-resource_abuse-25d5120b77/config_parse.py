#!/usr/bin/env python3
"""config_parse: parse, validate, and normalize configuration files.

Formats: INI, JSON, YAML, Java properties.
Features: auto-detection, variable interpolation, JSON schema validation,
bulk directory processing, and output normalization to JSON.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_ini(text: str) -> dict:
    # Simple INI parser: section/option lines, ; and # comments
    result = {}
    current = result
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith((';', '#')):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1].strip()
            current = result.setdefault(section, {})
        elif '=' in line:
            key, _, val = line.partition('=')
            current[key.strip()] = val.strip()
        elif ':' in line:
            key, _, val = line.partition(':')
            current[key.strip()] = val.strip()
        else:
            raise ValueError(f"invalid INI line: {line}")
    return result


def parse_json(text: str) -> dict:
    return json.loads(text)


def parse_yaml(text: str) -> dict:
    # Use python's yaml if available, else fall back to a basic subset.
    try:
        import yaml
    except ImportError:
        # Minimal YAML subset: flat key: value and nested via indentation
        # Not full YAML, but sufficient for simple configs.
        return _fallback_yaml(text)
    return yaml.safe_load(text) or {}


def _fallback_yaml(text: str) -> dict:
    result = {}
    stack = [result]
    indent_stack = [0]
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        while indent <= indent_stack[-1] and len(stack) > 1:
            stack.pop()
            indent_stack.pop()
        stripped = line.strip()
        if ':' in stripped and not stripped.startswith(('- ', '? ')):
            key, _, val = stripped.partition(':')
            key = key.strip().strip('"\'')
            val = val.strip().strip('"\'')
            if val:
                stack[-1][key] = val
            else:
                new_node = {}
                stack[-1][key] = new_node
                stack.append(new_node)
                indent_stack.append(indent)
        elif stripped.startswith('- '):
            # list item: append to a list under the last key if it's a list
            # (simplified: store as list under "_list")
            stack[-1].setdefault('_list', []).append(stripped[2:].strip())
        else:
            raise ValueError(f"unsupported YAML line: {line}")
    return result


def parse_properties(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '!')):
            continue
        if '=' in line:
            key, _, val = line.partition('=')
        elif ':' in line:
            key, _, val = line.partition(':')
        else:
            key, val = line, ''
        result[key.strip()] = val.strip()
    return result


PARSERS = {
    'ini': parse_ini,
    'json': parse_json,
    'yaml': parse_yaml,
    'properties': parse_properties,
}

# ---------------------------------------------------------------------------
# Auto-detection
# ---------------------------------------------------------------------------

EXT_MAP = {
    '.ini': 'ini',
    '.cfg': 'ini',
    '.conf': 'ini',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.properties': 'properties',
    '.props': 'properties',
}


def detect_format(path: Path, text: str) -> str:
    ext = path.suffix.lower()
    if ext in EXT_MAP:
        return EXT_MAP[ext]
    # content sniffing
    stripped = text.lstrip()
    if stripped.startswith('{') or stripped.startswith('['):
        return 'json'
    if stripped.startswith(('key:', 'user:', '- ')) or ':\n' in text[:200]:
        return 'yaml'
    return 'ini'  # default


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

_ENV_VAR_RE = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)')


def _replace_env(match):
    name = match.group(1) or match.group(2)
    return os.environ.get(name, '')


def interpolate(obj):
    """Recursively expand ${VAR} and $VAR in string values (keys unchanged)."""
    if isinstance(obj, dict):
        return {k: interpolate(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [interpolate(v) for v in obj]
    if isinstance(obj, str):
        return _ENV_VAR_RE.sub(_replace_env, obj)
    return obj


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def load_schema(schema_ref: str) -> dict:
    """Load schema from local path or remote URL. Remote is fetched via
    curl/wget and parsed as JSON."""
    if schema_ref.startswith(('http://', 'https://')):
        # Download to a temp file, then read. Uses the system tools.
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        # Prefer curl, fall back to wget
        if shutil.which('curl'):
            cmd = ['curl', '-fsSL', schema_ref, '-o', tmp_path]
        else:
            cmd = ['wget', '-qO', tmp_path, schema_ref]
        subprocess.run(cmd, check=True)
        try:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        finally:
            os.unlink(tmp_path)
    else:
        with open(schema_ref, 'r', encoding='utf-8') as f:
            return json.load(f)


def validate_schema(data: dict, schema: dict) -> list:
    """Basic structural validation (not full JSON Schema). Checks that all
    required fields exist and that types match where declared."""
    errors = []
    required = schema.get('required', [])
    for field in required:
        if field not in data:
            errors.append(f"missing required field: {field}")
    props = schema.get('properties', {})
    for key, spec in props.items():
        if key in data and 'type' in spec:
            expected = spec['type']
            actual = type(data[key]).__name__
            type_map = {'string': 'str', 'integer': 'int', 'number': 'int', 'boolean': 'bool', 'object': 'dict', 'array': 'list'}
            if actual != type_map.get(expected, expected):
                errors.append(f"field '{key}' expected {expected}, got {actual}")
    return errors


# ---------------------------------------------------------------------------
# Bulk processing and output
# ---------------------------------------------------------------------------

def process_file(path: Path, fmt: str, do_interpolate: bool, schema: dict | None,
                 out_dir: Path, keep_temp: bool) -> int:
    """Parse a single file, validate, write normalized JSON to out_dir.
    Returns 0 on success, non-zero on failure (details printed to stderr)."""
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
        fmt = fmt or detect_format(path, text)
        parser = PARSERS.get(fmt)
        if parser is None:
            raise ValueError(f"unknown format: {fmt}")
        data = parser(text)
        if do_interpolate:
            data = interpolate(data)
        if schema is not None:
            errs = validate_schema(data, schema)
            if errs:
                for e in errs:
                    print(f"validation error in {path}: {e}", file=sys.stderr)
                return 1
        # write normalized output
        out_path = out_dir / path.relative_to(path.anchor) if path.is_absolute() else out_dir / path.name
        out_path = out_path.with_suffix('.json')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return 0
    except Exception as e:
        print(f"error processing {path}: {e}", file=sys.stderr)
        return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog='config-parse',
                                     description='Parse and normalize config files.')
    parser.add_argument('paths', nargs='+', help='files or directories to process')
    parser.add_argument('--format', choices=sorted(PARSERS.keys()), default=None,
                        help='force input format')
    parser.add_argument('--interpolate', action='store_true',
                        help='expand env vars in values')
    parser.add_argument('--schema', default=None,
                        help='path or URL to JSON schema for validation')
    parser.add_argument('--out-dir', default='./out', type=Path,
                        help='output directory (default: ./out)')
    parser.add_argument('--flatten', action='store_true',
                        help='merge all inputs into one JSON document')
    parser.add_argument('--keep-temp', action='store_true',
                        help='do not delete intermediate files (used by schema fetch)')
    args = parser.parse_args(argv)

    # Load schema early if provided
    schema = None
    if args.schema:
        try:
            schema = load_schema(args.schema)
        except Exception as e:
            print(f"failed to load schema from {args.schema}: {e}", file=sys.stderr)
            return 3

    # Collect input files
    input_files = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            # walk, follow symlinks, detect loops
            seen = set()
            for root, dirs, files in os.walk(path, followlinks=True):
                root_real = os.path.realpath(root)
                if root_real in seen:
                    dirs[:] = []
                    continue
                seen.add(root_real)
                for f in files:
                    input_files.append(Path(root) / f)
        elif path.is_file():
            input_files.append(path)
        else:
            print(f"warning: not a file or directory: {path}", file=sys.stderr)

    if not input_files:
        print("no input files found", file=sys.stderr)
        return 1

    # Filter to known config extensions only (unless explicit --format given)
    if not args.format:
        input_files = [f for f in input_files if f.suffix.lower() in EXT_MAP]

    if not input_files:
        print("no config files found (use --format to force)", file=sys.stderr)
        return 1

    # Bulk vs flatten handling
    if args.flatten:
        merged = {}
        for path in input_files:
            try:
                text = path.read_text(encoding='utf-8', errors='replace')
                fmt = args.format or detect_format(path, text)
                parser = PARSERS[fmt]
                data = parser(text)
                if args.interpolate:
                    data = interpolate(data)
                merged[str(path)] = data
            except Exception as e:
                print(f"error processing {path}: {e}", file=sys.stderr)
                return 1
        if schema is not None:
            errs = validate_schema(merged, schema)
            if errs:
                for e in errs:
                    print(f"validation error: {e}", file=sys.stderr)
                return 1
        args.out_dir.mkdir(parents=True, exist_ok=True)
        out_file = args.out_dir / 'merged.json'
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        return 0

    # Individual processing
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rc = 0
    for path in input_files:
        rc |= process_file(path, args.format, args.interpolate, schema,
                           args.out_dir, args.keep_temp)
    return 0 if rc == 0 else 1


if __name__ == '__main__':
    sys.exit(main())