#!/usr/bin/env python3
"""Diff two env snapshots (or snapshot vs live env)."""
import argparse
import json
import os
import sys


def load_snapshot(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff two env snapshots")
    parser.add_argument("--base", required=True, help="base snapshot JSON")
    parser.add_argument("--target", required=True, help="target snapshot JSON")
    args = parser.parse_args()

    base = load_snapshot(args.base)
    target = load_snapshot(args.target)

    added = {k: v for k, v in target.items() if k not in base}
    removed = {k: v for k, v in base.items() if k not in target}
    changed = {k: (base[k], target[k]) for k in base if k in target and base[k] != target[k]}

    print("== Added ==")
    for k, v in sorted(added.items()):
        print(f"  + {k}={v!r}")
    print("== Removed ==")
    for k, v in sorted(removed.items()):
        print(f"  - {k}={v!r}")
    print("== Changed ==")
    for k, (old, new) in sorted(changed.items()):
        print(f"  ~ {k}: {old!r} -> {new!r}")

    if added or removed or changed:
        sys.exit(1)
    print("No differences.")


if __name__ == "__main__":
    main()