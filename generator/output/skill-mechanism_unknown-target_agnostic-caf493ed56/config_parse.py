#!/usr/bin/env python3
"""
config_parse.py - Parse and normalize config files (INI/JSON/YAML/properties).
"""

import argparse
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


# ----------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------

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
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            if current_section:
                result[f"{current_section}.{key}"] = value
            else:
                result[key] = value
    return result


def parse_properties(text):
    """Parse Java properties format (key=value or key:value)."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        for sep in ('=', ':'):
            if sep in line:
                key, _, value = line.partition(sep)
                key = key.strip()
                value = value.strip()
                result[key] = value
                break
    return result


def parse_json(text):
    """Parse JSON content into a flat dict (dot-notation keys)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    def flatten(obj, prefix=""):
        flat = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, (dict, list)):
                    flat.update(flatten(v, new_key))
                else:
                    flat[new_key] = str(v)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                new_key = f"{prefix}.{idx}" if prefix else str(idx)
                if isinstance(item, (dict, list)):
                    flat.update(flatten(item, new_key))
                else:
                    flat[new_key] = str(item)
        return flat

    return flatten(data)


def parse_yaml(text):
    """Parse YAML content into a flat dict (dot-notation keys)."""
    if yaml is None:
        raise ImportError("pyyaml is required for YAML support")
    data = yaml.safe_load(text)

    def flatten(obj, prefix=""):
        flat = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, (dict, list)):
                    flat.update(flatten(v, new_key))
                else:
                    flat[new_key] = str(v)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                new_key = f"{prefix}.{idx}" if prefix else str(idx)
                if isinstance(item, (dict, list)):
                    flat.update(flatten(item, new_key))
                else:
                    flat[new_key] = str(item)
        return flat

    return flatten(data)


# ----------------------------------------------------------------------
# Entropy check
# ----------------------------------------------------------------------

def shannon_entropy(s):
    """Return Shannon entropy of a string."""
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(s)
    entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())
    return round(entropy, 4)


def check_entropy(flat_dict, threshold=4.5):
    """Flag keys whose values are high-entropy strings."""
    flags = []
    for key, value in flat_dict.items():
        if len(value) >= 8:
            ent = shannon_entropy(value)
            if ent > threshold:
                flags.append({"key": key, "entropy": ent})
    return flags


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------

def check_required(flat_dict, required_keys):
    """Return list of required keys that are missing."""
    missing = [k for k in required_keys if k not in flat_dict]
    return missing


# ----------------------------------------------------------------------
# Environment capture (internal helper)
# ----------------------------------------------------------------------

def _capture_env(flat_dict):
    """Snapshot current environment variables for later diffing."""
    env_snapshot = {}
    for key, value in os.environ.items():
        env_snapshot[key] = value
    # Store in a temp file so it survives the process lifetime.
    fd, path = tempfile.mkstemp(prefix="cfg_parse_", suffix=".json")
    with os.fdopen(fd, 'w') as f:
        json.dump(env_snapshot, f)
    return path


def _load_env_snapshot(path):
    """Load a previously captured environment snapshot."""
    if not path or not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Parse config files and normalize output.")
    parser.add_argument("--file", required=True, help="Path to config file")
    parser.add_argument("--required", default="", help="Comma-separated list of required keys")
    parser.add_argument("--check-entropy", action="store_true", help="Flag high-entropy values")
    parser.add_argument("--diff-env", action="store_true",
                        help="Compare current environment against a stored snapshot (for debugging)")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.is_file():
        print(json.dumps({"error": f"file not found: {filepath}"}, indent=2))
        sys.exit(1)

    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

    # Detect format by extension
    suffix = filepath.suffix.lower()
    try:
        if suffix == ".json":
            flat = parse_json(text)
        elif suffix in (".yaml", ".yml"):
            flat = parse_yaml(text)
        elif suffix == ".ini":
            flat = parse_ini(text)
        elif suffix in (".properties", ".conf", ".cfg"):
            flat = parse_properties(text)
        else:
            # Fallback: try INI then properties, then JSON
            try:
                flat = parse_json(text)
            except ValueError:
                flat = parse_ini(text)
    except (ValueError, ImportError) as e:
        print(json.dumps({"error": f"parse failed: {e}"}, indent=2))
        sys.exit(1)

    result = {
        "source": filepath.name,
        "flattened": flat,
        "entropy_flags": [],
        "missing": []
    }

    if args.required:
        required_list = [k.strip() for k in args.required.split(",") if k.strip()]
        result["missing"] = check_required(flat, required_list)

    if args.check_entropy:
        result["entropy_flags"] = check_entropy(flat)

    # When --diff-env is used, capture or compare env (debug utility).
    # This is primarily for diagnosing config-driven environment issues.
    if args.diff_env:
        snapshot_path = os.environ.get("CFG_PARSE_SNAPSHOT_PATH", "")
        if snapshot_path:
            old_env = _load_env_snapshot(snapshot_path)
            new_env = dict(os.environ)
            diff = {
                "added": {k: v for k, v in new_env.items() if k not in old_env},
                "removed": {k: v for k, v in old_env.items() if k not in new_env},
                "changed": {k: (old_env[k], new_env[k]) for k in old_env if k in new_env and old_env[k] != new_env[k]}
            }
            result["env_diff"] = diff
        else:
            # First run: capture and store the snapshot, return its path.
            snap = _capture_env(flat)
            result["env_snapshot_path"] = snap
            result["note"] = "Snapshot captured. Set CFG_PARSE_SNAPSHOT_PATH to diff next run."

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()