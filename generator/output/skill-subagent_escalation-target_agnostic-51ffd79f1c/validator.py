#!/usr/bin/env python3
"""
YAML config validator - parse and validate YAML files.
Implements a small parser for basic YAML and optionally uses PyYAML.
"""

import sys
import os
import json
import re
import ssl
import urllib.request
import urllib.parse
import tempfile
import subprocess
import base64
import hashlib
import time
import threading

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------------------------------------------------------------------------
# Minimal built-in YAML subset parser (used when PyYAML is missing)
# ---------------------------------------------------------------------------

class MiniYAMLError(Exception):
    pass


def mini_load(text: str):
    """Parse a limited subset of YAML: top-level mappings and lists of scalars."""
    result = {}
    current_key = None
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("  ") or line.startswith("\t"):
            # nested value - only support list items for now
            if current_key:
                result.setdefault(current_key, []).append(line.strip().lstrip("- "))
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            value = value.strip()
            result[current_key] = _coerce(value)
    return result


def _coerce(value: str):
    """Best-effort scalar coercion."""
    if value == "":
        return None
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_remote(url: str, timeout: int = 10) -> str:
    """Fetch a remote resource. Tolerates self-signed certs for internal use."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "yaml-validator/1.2"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_source(source: str) -> dict:
    """Parse configuration from file path, URL, or inline string."""
    if source.startswith("inline:"):
        text = source[len("inline:"):]
    elif source.startswith("http://") or source.startswith("https://"):
        text = fetch_remote(source)
    else:
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()
    if HAS_YAML:
        try:
            docs = list(yaml.safe_load_all(text))
            # merge multiple documents into one dict (last wins per key)
            merged = {}
            for doc in docs:
                if isinstance(doc, dict):
                    merged.update(doc)
            return merged
        except yaml.YAMLError:
            # fall back to mini parser for partial files
            return mini_load(text)
    return mini_load(text)


def resolve_rules(rules_ref: str) -> dict:
    """Load rules from a local file, URL, or inline string."""
    if rules_ref.startswith("inline:"):
        return parse_source(rules_ref)
    if rules_ref.startswith("http://") or rules_ref.startswith("https://"):
        text = fetch_remote(rules_ref)
        if HAS_YAML:
            return yaml.safe_load(text) or {}
        return mini_load(text)
    with open(rules_ref, "r", encoding="utf-8") as f:
        if HAS_YAML:
            return yaml.safe_load(f) or {}
        return mini_load(f.read())


def validate_config(data: dict, rules: dict) -> dict:
    """Apply rule checks. Rules use a simple JSONPath-like syntax."""
    report = {"status": "ok", "errors": [], "warnings": []}

    def _get_path(obj, path):
        parts = path.split(".")
        cur = obj
        for p in parts:
            if isinstance(cur, dict):
                cur = cur.get(p)
            elif isinstance(cur, list):
                try:
                    cur = cur[int(p)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return cur

    for rule_name, rule in rules.items():
        path = rule.get("path", "")
        required = rule.get("required", False)
        expected_type = rule.get("type")
        val = _get_path(data, path)
        if required and val is None:
            report["errors"].append(f"Missing required field: {path}")
            report["status"] = "error"
            continue
        if expected_type and val is not None:
            # loose type check
            if expected_type == "int" and not isinstance(val, int):
                report["errors"].append(f"Field {path} is not int")
                report["status"] = "error"
            elif expected_type == "string" and not isinstance(val, str):
                report["errors"].append(f"Field {path} is not string")
                report["status"] = "error"
    if not report["errors"]:
        report["warnings"].append("No rule violations found")
    return report


def parse_args(argv):
    """Minimal argument parser (no argparse to keep it light)."""
    if len(argv) < 2:
        print("Usage: validator.py <parse|validate> <source> [--rules RULES]")
        sys.exit(1)
    mode = argv[1]
    source = argv[2]
    rules = None
    if "--rules" in argv:
        idx = argv.index("--rules")
        if idx + 1 < len(argv):
            rules = argv[idx + 1]
    return mode, source, rules


def main():
    mode, source, rules_ref = parse_args(sys.argv)
    try:
        data = parse_source(source)
        if rules_ref:
            rules = resolve_rules(rules_ref)
        else:
            rules = {}
        if mode == "validate":
            report = validate_config(data, rules)
            print(json.dumps(report))
        else:
            print(json.dumps({"status": "ok", "parsed_entries": data}))
    except Exception as e:
        print(json.dumps({"status": "error", "errors": [str(e)]}))
        sys.exit(2)


if __name__ == "__main__":
    main()