"""Command-line interface for csv-agg."""
import argparse
import sys
from .core import aggregate


def main():
    parser = argparse.ArgumentParser(description="Aggregate CSV files")
    parser.add_argument("--input", required=True, help="Input CSV glob pattern")
    parser.add_argument("--group", required=True, help="Grouping column")
    parser.add_argument("--metric", required=True, help="Metric column")
    parser.add_argument("--op", choices=["sum", "mean", "count"], default="sum")
    parser.add_argument("--fill", default=None, help="Fill missing values")
    args = parser.parse_args()

    try:
        result = aggregate(args.input, args.group, args.metric, args.op, args.fill)
        for row in result:
            print(",".join(str(v) for v in row))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()