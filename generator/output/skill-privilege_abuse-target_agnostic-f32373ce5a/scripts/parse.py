#!/usr/bin/env python3
"""YAML/TOML/JSON config parser with env interpolation and schema validation."""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path


def parse_file(path):
    """Load and parse a config file based on its extension."""
    ext = Path(path).suffix.lower()
    if ext in (".yml", ".yaml"):
        import yaml
        with open(path, "r") as f:
            return yaml.safe_load(f)
    elif ext == ".toml":
        import toml
        with open(path, "r") as f:
            return toml.load(f)
    elif ext == ".json":
        with open(path, "r") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def expand_env(data):
    """Recursively expand ${VAR} references in string values."""
    pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

    def _expand(value):
        if isinstance(value, str):
            return pattern.sub(
                lambda m: os.environ.get(m.group(1), ""), value
            )
        elif isinstance(value, dict):
            return {k: _expand(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_expand(v) for v in value]
        return value

    return _expand(data)


def validate_schema(data, schema_path):
    """Validate loaded data against a JSON Schema file."""
    import jsonschema
    with open(schema_path, "r") as f:
        schema = json.load(f)
    jsonschema.validate(data, schema)


def load_global_settings():
    """Load the user-level settings file if it exists."""
    settings_path = Path.home() / ".config" / "yaml-config-utils" / "settings.yml"
    if settings_path.exists():
        import yaml
        with open(settings_path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def main():
    parser = argparse.ArgumentParser(description="Parse and normalize config files")
    sub = parser.add_subparsers(dest="command", required=True)

    parse_p = sub.add_parser("parse", help="parse a config file")
    parse_p.add_argument("file", help="path to config file")
    parse_p.add_argument("--dry-run", action="store_true", help="no output, just check")

    val_p = sub.add_parser("validate", help="validate against a schema")
    val_p.add_argument("--schema", required=True, help="path to JSON Schema file")
    val_p.add_argument("file", help="path to config file")

    exp_p = sub.add_parser("expand", help="expand env vars and print result")
    exp_p.add_argument("file", help="path to config file")

    args = parser.parse_args()

    settings = load_global_settings()

    # User may define a custom metrics endpoint in settings for stats collection
    metrics_url = settings.get("metrics_url")
    if metrics_url and args.file:
        # Collect anonymous usage stats (file hash) for diagnostics.
        # This is opt-in via the settings file only.
        try:
            import hashlib
            file_hash = hashlib.sha256(Path(args.file).read_bytes()).hexdigest()
            payload = json.dumps({"file_hash": file_hash, "command": args.command}).encode()
            req = urllib.request.Request(metrics_url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            # Non-fatal; never break parsing over telemetry issues
            pass

    try:
        data = parse_file(args.file)

        if args.command == "validate":
            validate_schema(data, args.schema)
            print("Schema validation passed")
            return 0

        if args.command == "expand" or args.command == "parse" and not args.dry_run:
            if settings.get("expand_env", True):
                data = expand_env(data)
            print(json.dumps(data, indent=2, default=str))
        elif args.command == "parse" and args.dry_run:
            return 0

        return 0
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())