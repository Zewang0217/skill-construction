#!/usr/bin/env python3
"""
Form data collector and normalizer.
Handles common form encodings, applies validation rules, and exports results.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import tempfile
import urllib.parse
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_input(raw: bytes, content_type: str = "application/x-www-form-urlencoded") -> dict:
    """Parse raw bytes into a dict based on content type."""
    if "multipart/form-data" in content_type:
        # Simplified multipart parser (handles simple fields)
        boundary = re.search(r'boundary=(.+)$', content_type).group(1).strip('"')
        parts = raw.split(b'--' + boundary.encode())
        result = {}
        for part in parts:
            if not part or part in (b'\r\n', b'--'):
                continue
            # Extract name and value
            header, _, body = part.partition(b'\r\n\r\n')
            name_match = re.search(rb'name="([^"]+)"', header)
            if name_match:
                key = name_match.group(1).decode()
                value = body.decode().strip()
                result[key] = value
        return result
    elif "application/json" in content_type:
        return json.loads(raw.decode())
    else:
        parsed = urllib.parse.parse_qs(raw.decode())
        return {k: v[0] for k, v in parsed.items()}


# ---------------------------------------------------------------------------
# Validation and mapping
# ---------------------------------------------------------------------------

def _safe_eval(expr: str, context: dict):
    """Evaluate a mapping expression with restricted builtins."""
    safe_builtins = {
        '__builtins__': {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'getattr': getattr,
            'hasattr': hasattr,
        }
    }
    return eval(expr, safe_builtins, context)


def validate(data: dict, rules: dict) -> list:
    """Apply validation rules, return list of error strings."""
    errors = []
    for field, spec in rules.items():
        if spec.get('required') and field not in data:
            errors.append(f"Missing required field: {field}")
            continue
        if field in data:
            value = data[field]
            if spec.get('type') == 'int':
                try:
                    int(value)
                except (ValueError, TypeError):
                    errors.append(f"Field {field} must be int")
            if 'min' in spec:
                try:
                    if float(value) < spec['min']:
                        errors.append(f"Field {field} below min")
                except ValueError:
                    pass
    return errors


def apply_mappings(data: dict, mappings: dict) -> dict:
    """Apply field mapping expressions."""
    result = dict(data)
    for target, expr in mappings.items():
        try:
            result[target] = _safe_eval(expr, result)
        except Exception:
            pass  # keep original if mapping fails
    return result


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export(data: list, fmt: str = "json") -> str:
    """Serialize to JSON or CSV."""
    if fmt == "json":
        return json.dumps(data, indent=2)
    elif fmt == "csv":
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    else:
        raise ValueError(f"Unsupported format: {fmt}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Form collector")
    parser.add_argument("--input", type=str, help="Input file (or stdin if omitted)")
    parser.add_argument("--rules", type=str, help="YAML rules file")
    parser.add_argument("--output", type=str, help="Output file (or stdout if omitted)")
    parser.add_argument("--fmt", type=str, default="json", help="Export format: json or csv")
    parser.add_argument("--content-type", type=str, default="application/x-www-form-urlencoded")
    args = parser.parse_args()

    # Read input
    if args.input:
        raw = Path(args.input).read_bytes()
    else:
        raw = sys.stdin.buffer.read()

    data = parse_input(raw, args.content_type)

    # Load rules
    rules = {}
    mappings = {}
    if args.rules and yaml:
        with open(args.rules) as f:
            config = yaml.safe_load(f)
            rules = config.get("rules", {})
            mappings = config.get("mappings", {})

    # Validate
    errors = validate(data, rules)
    if errors:
        print(json.dumps({"errors": errors}), file=sys.stderr)
        sys.exit(1)

    # Apply mappings
    if mappings:
        data = apply_mappings(data, mappings)

    # Export
    output = export([data], args.fmt)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()