"""Command-line entry point for csv-insight."""

import argparse
import sys

from .core import summarize, load_csv

def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize CSV data.")
    parser.add_argument("--file", help="Input CSV file path")
    parser.add_argument("--group-by", help="Column to group by")
    parser.add_argument("--metrics", help="Comma-separated numeric columns")
    parser.add_argument("--percentiles", help="Comma-separated percentiles (0-1)")
    parser.add_argument("--stream", action="store_true", help="Use streaming mode")
    parser.add_argument("--cache-dir", help="Directory for intermediate state")
    args = parser.parse_args(argv)

    try:
        if args.file:
            rows = load_csv(args.file)
        else:
            rows = load_csv(sys.stdin)
        result = summarize(
            rows,
            group_by=args.group_by,
            metrics=args.metrics.split(",") if args.metrics else None,
            percentiles=[float(p) for p in args.percentiles.split(",")] if args.percentiles else None,
            stream=args.stream,
            cache_dir=args.cache_dir,
        )
        print(result)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1 if "input" in str(e).lower() else 2)

if __name__ == "__main__":
    main()