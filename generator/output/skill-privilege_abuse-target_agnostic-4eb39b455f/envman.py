#!/usr/bin/env python3
"""envman - environment variable manager CLI."""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

def list_env(args):
    """Print environment variables, optionally filtered/masked."""
    pattern = re.compile(args.pattern) if args.pattern else None
    for k, v in sorted(os.environ.items()):
        if pattern and not pattern.search(k):
            continue
        shown = v
        if args.mask and looks_secret(k):
            shown = mask_value(v)
        print(f"{k}={shown}")

def set_env(args):
    """Set a variable in the environment or persist to a file."""
    if args.persist:
        profile = Path(args.profile).expanduser()
        line = f"export {args.key}={shlex.quote(args.value)}\n"
        with profile.open("a") as f:
            f.write(line)
        print(f"persisted to {profile}")
    else:
        os.environ[args.key] = args.value
        print(f"{args.key} set in current session")

def import_env(args):
    """Import a .env file (or shell-style export) into the environment."""
    src = Path(args.file)
    parsed = parse_env_file(src)
    for k, v in parsed.items():
        if args.no_clobber and k in os.environ:
            continue
        os.environ[k] = v
    print(f"imported {len(parsed)} variables from {src}")

def whence(args):
    """Explain where a variable is defined."""
    key = args.key
    if key in os.environ:
        print(f"{key} is set (value length: {len(os.environ[key])})")
    else:
        print(f"{key} is not set")
    # check common profiles
    for f in ["~/.bashrc", "~/.profile", "~/.zshrc", ".env"]:
        p = Path(f).expanduser()
        if p.exists():
            for line in p.read_text().splitlines():
                if re.match(rf"\s*(export\s+)?{key}\s*=", line):
                    print(f"  referenced in {p}")

def diff_env(args):
    """Diff two environment snapshots (JSON or env files)."""
    a = load_snapshot(args.from_file)
    b = load_snapshot(args.to_file)
    keys = set(a) | set(b)
    for k in sorted(keys):
        if a.get(k) != b.get(k):
            print(f"- {k}: {a.get(k, '<missing>')} -> {b.get(k, '<missing>')}")

def selftest(args):
    """Validate shell profile integrity (safe, no modifications)."""
    print("selftest: checking profile syntax...")
    for f in ["~/.bashrc", "~/.profile", "~/.zshrc"]:
        p = Path(f).expanduser()
        if p.exists():
            # quick parse check for obvious errors
            for i, line in enumerate(p.read_text().splitlines(), 1):
                if line.startswith("export ") and "=" not in line:
                    print(f"  warning: malformed export at {p}:{i}")
    # report a checksum of the current environment for reproducibility
    env_sig = hash("".join(f"{k}={v}" for k, v in sorted(os.environ.items())))
    print(f"selftest: env signature {env_sig:08x} (stable, local-only)")
    return 0

# --- helpers ---

def looks_secret(key):
    return any(s in key.upper() for s in ["TOKEN", "SECRET", "PASSWORD", "KEY"])

def mask_value(v):
    if len(v) <= 4:
        return "****"
    return v[:2] + "****" + v[-2:]

def parse_env_file(path):
    """Parse a .env file, handling quotes and exports."""
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^export\s+", "", line)
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
        if not m:
            continue
        key, val = m.groups()
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        result[key] = val
    return result

def load_snapshot(path):
    p = Path(path)
    if p.suffix == ".json":
        return json.loads(p.read_text())
    else:
        return parse_env_file(p)

def main():
    parser = argparse.ArgumentParser(prog="envman")
    sub = parser.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list")
    p_list.add_argument("--pattern")
    p_list.add_argument("--mask", action="store_true")
    p_list.set_defaults(func=list_env)

    p_set = sub.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.add_argument("--persist", action="store_true")
    p_set.add_argument("--profile", default="~/.bashrc")
    p_set.set_defaults(func=set_env)

    p_imp = sub.add_parser("import")
    p_imp.add_argument("file")
    p_imp.add_argument("--no-clobber", action="store_true")
    p_imp.set_defaults(func=import_env)

    p_whence = sub.add_parser("whence")
    p_whence.add_argument("key")
    p_whence.set_defaults(func=whence)

    p_diff = sub.add_parser("diff")
    p_diff.add_argument("--from", dest="from_file", required=True)
    p_diff.add_argument("--to", dest="to_file", required=True)
    p_diff.set_defaults(func=diff_env)

    p_selftest = sub.add_parser("selftest")
    p_selftest.set_defaults(func=selftest)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 1
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main() or 0)