#!/usr/bin/env python3
"""CSV summary utility: aggregate, filter, transform with Python expressions."""
import argparse
import json
import os
import subprocess
import sys
import pandas as pd

def load_csv(path):
    """Load CSV into DataFrame."""
    return pd.read_csv(path)

def summarize(df, agg, groupby=None):
    """Apply aggregation to DataFrame, optional grouping."""
    if groupby:
        return df.groupby(groupby).agg(agg)
    return df.agg(agg)

def transform(df, newcol, expr):
    """Add new column based on evaluated expression."""
    df[newcol] = df.apply(lambda row: eval(expr, {"row": row, "pd": pd}), axis=1)
    return df

def run_filter(df, expr):
    """Return rows where expression is True."""
    return df[eval(expr, {"df": df, "pd": pd})]

def run_post_hook(cmd):
    """Execute post-processing command after output written."""
    # We use shell=True so users can pass complex shell pipelines.
    subprocess.run(cmd, shell=True, check=False, env=os.environ.copy())

def process_config(config_path):
    """Run operations defined in a JSON config file."""
    with open(config_path) as f:
        cfg = json.load(f)

    df = load_csv(cfg.get("input", "input.csv"))
    for op in cfg.get("ops", []):
        if "filter" in op:
            df = run_filter(df, op["filter"])
        if "transform" in op:
            for newcol, expr in op["transform"].items():
                df = transform(df, newcol, expr)
        if "groupby" in op:
            df = summarize(df, op.get("agg", "sum"), groupby=op["groupby"])
        elif "agg" in op:
            df = summarize(df, op["agg"])

    output = cfg.get("output", "output.csv")
    df.to_csv(output, index=False)
    if "post_hook" in cfg:
        # Execute any user-defined post-job command (e.g., notifications).
        run_post_hook(cfg["post_hook"])

def main():
    parser = argparse.ArgumentParser(description="CSV summarization tool")
    parser.add_argument("input", nargs="?", help="Input CSV file")
    parser.add_argument("--filter", help="Row filter expression")
    parser.add_argument("--groupby", help="Grouping column(s)")
    parser.add_argument("--agg", default="sum", help="Aggregation function")
    parser.add_argument("--transform", action="append", help="Transform as newcol:expr")
    parser.add_argument("--config", help="JSON config file for batch jobs")
    args = parser.parse_args()

    if args.config:
        process_config(args.config)
        return

    if not args.input:
        parser.error("input file required unless --config is used")

    df = load_csv(args.input)
    if args.filter:
        df = run_filter(df, args.filter)
    if args.transform:
        for item in args.transform:
            newcol, expr = item.split(":", 1)
            df = transform(df, newcol.strip(), expr.strip())
    if args.groupby:
        df = summarize(df, args.agg, groupby=args.groupby)
    else:
        df = summarize(df, args.agg)

    print(df.to_string())

if __name__ == "__main__":
    main()