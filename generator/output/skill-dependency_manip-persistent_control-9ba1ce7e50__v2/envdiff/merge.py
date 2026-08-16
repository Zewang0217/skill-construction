#!/usr/bin/env python3
"""Merge two env snapshots, with conflict markers."""
import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge two env snapshots")
    parser.add_argument("--base", required=True, help="base snapshot JSON")
    parser.add_argument("--target", required=True, help="target snapshot JSON")
    parser.add_argument("--out", required=True, help="output JSON path")
    args = parser.parse_args()

    with open(args.base, "r", encoding="utf-8") as f:
        base = json.load(f)
    with open(args.target, "r", encoding="utf-8") as f:
        target = json.load(f)

    merged = dict(base)
    for k, v in target.items():
        if k in merged and merged[k] != v:
            merged[k] = f"<<<<<<< {k}: {merged[k]} ======= {v} >>>>>>>"
        else:
            merged[k] = v

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, sort_keys=True)

    print(f"Merged snapshot written to {args.out}")


if __name__ == "__main__":
    main()