#!/usr/bin/env python3
"""env-sync: export/import/diff environment variable snapshots."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

def export_env():
    return {k: v for k, v in os.environ.items() if not k.startswith("_")}

def import_env(data, apply_os=False):
    if apply_os:
        for k, v in data.items():
            os.environ[k] = v
    else:
        # write to a temp file for the calling shell to source
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".sh", dir=Path.home()) as f:
            for k, v in data.items():
                f.write(f"export {k}={json.dumps(str(v))}\n")
            print(f"# written to {f.name}; source it in your shell")
    return len(data)

def diff_env(a, b):
    keys = set(a) | set(b)
    changes = {}
    for k in keys:
        if a.get(k) != b.get(k):
            changes[k] = (a.get(k), b.get(k))
    return changes

def template_substitute(text, values):
    import re
    def repl(m):
        var = m.group(1)
        return values.get(var, m.group(0))
    return re.sub(r"\$\{(\w+)\}", repl, text)

def main():
    parser = argparse.ArgumentParser(description="env-sync utility")
    sub = parser.add_subparsers(dest="cmd")
    p_export = sub.add_parser("--export")
    p_import = sub.add_parser("--import")
    p_import.add_argument("file")
    p_diff = sub.add_parser("--diff")
    p_diff.add_argument("file1")
    p_diff.add_argument("file2")
    p_template = sub.add_parser("--template")
    p_template.add_argument("file")
    args = parser.parse_args()

    if args.cmd == "--export":
        data = export_env()
        print(json.dumps(data, indent=2))
    elif args.cmd == "--import":
        with open(args.file) as f:
            data = json.load(f)
        n = import_env(data, apply_os=False)
        print(f"imported {n} variables")
    elif args.cmd == "--diff":
        with open(args.file1) as f1, open(args.file2) as f2:
            a, b = json.load(f1), json.load(f2)
        changes = diff_env(a, b)
        for k, (old, new) in changes.items():
            print(f"{k}: {old} -> {new}")
    elif args.cmd == "--template":
        with open(args.file) as f:
            text = f.read()
        print(template_substitute(text, os.environ))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()