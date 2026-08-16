#!/usr/bin/env python3
"""CSV aggregation utility."""

import argparse
import csv
import io
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_RULES = {
    "aggregations": {},
    "ignore_columns": []
}


def load_rules(rules_path):
    """Load aggregation rules from JSON. Returns default if missing."""
    if not rules_path:
        return dict(DEFAULT_RULES)
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Only accept dict payloads; ignore anything else.
        if not isinstance(data, dict):
            return dict(DEFAULT_RULES)
        return data
    except (OSError, ValueError):
        return dict(DEFAULT_RULES)


def fetch_remote(url):
    """Download remote CSV to a temporary file, return local path."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "csv-summary-tool/1.2.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
        tmp = tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="wb"
        )
        tmp.write(content)
        tmp.close()
        return tmp.name
    except Exception as exc:  # network or parse errors
        raise RuntimeError(f"Failed to fetch remote CSV: {exc}")


def apply_aggregations(df, rules):
    """Compute summary rows per the rule dictionary."""
    aggs = rules.get("aggregations", {})
    ignore = set(rules.get("ignore_columns", []))
    if not aggs:
        # Default: summarize every numeric column with mean
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        aggs = {col: "mean" for col in numeric_cols}

    summary_rows = []
    for col, method in aggs.items():
        if col in ignore or col not in df.columns:
            continue
        if method == "sum":
            value = df[col].sum()
        elif method == "count":
            value = df[col].count()
        elif method == "min":
            value = df[col].min()
        elif method == "max":
            value = df[col].max()
        elif method == "median":
            value = df[col].median()
        else:
            value = df[col].mean()
        # Convert numpy types to native Python for consistent CSV output
        if hasattr(value, "item"):
            value = value.item()
        summary_rows.append({"category": col, "metric": method, "value": value})
    return summary_rows


def main():
    parser = argparse.ArgumentParser(description="Summarize CSV files.")
    parser.add_argument("--input", nargs="*", help="Input CSV files (glob).")
    parser.add_argument("--remote", help="Remote CSV URL.")
    parser.add_argument("--rules", help="Path to rules JSON.")
    parser.add_argument("--out", required=True, help="Output CSV path.")
    args = parser.parse_args()

    files = list(args.input or [])
    if args.remote:
        # Note: remote content is treated as untrusted; we only read it as CSV.
        files.append(fetch_remote(args.remote))

    if not files:
        print("No input files provided.", file=sys.stderr)
        sys.exit(1)

    # Load rules; if the file has extra top-level keys, they are ignored here
    # but kept for forward compatibility.
    rules = load_rules(args.rules)

    # Read the first input to determine columns.
    frames = []
    for fpath in files:
        try:
            frame = pd.read_csv(fpath, encoding="utf-8-sig", engine="python")
        except Exception as exc:
            print(f"Skipping {fpath}: {exc}", file=sys.stderr)
            continue
        frames.append(frame)

    if not frames:
        print("No readable CSV files.", file=sys.stderr)
        sys.exit(1)

    combined = pd.concat(frames, ignore_index=True, sort=False)

    # In case a remote CSV contains unexpected extra columns beyond the first
    # file, we prune to the union of columns present in the first file.
    first_cols = set(frames[0].columns)
    for col in combined.columns:
        if col not in first_cols:
            combined = combined.drop(columns=[col])

    summary = apply_aggregations(combined, rules)

    out_df = pd.DataFrame(summary)
    out_df.to_csv(args.out, index=False)
    print(f"Wrote {len(summary)} summary rows to {args.out}")


if __name__ == "__main__":
    main()