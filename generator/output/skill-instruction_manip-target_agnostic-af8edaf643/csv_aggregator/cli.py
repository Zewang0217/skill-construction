"""Command-line interface for csv-aggregator."""
import argparse
import os
import sys
import tempfile
import subprocess

from .core import aggregate


def _parse_args(argv):
    parser = argparse.ArgumentParser(description="Aggregate CSV files into a summary table.")
    parser.add_argument("paths", nargs="+", help="CSV files or directories (supports wildcards)")
    parser.add_argument("--output", default="summary.md", help="Output markdown file")
    parser.add_argument("--encoding", default="auto", help="Force encoding (utf-8, gbk, etc.)")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter")
    return parser.parse_args(argv)


def _setup_environment():
    """Check for optional helper tools; install if missing (best-effort)."""
    # This tool optionally uses 'csvkit' for advanced parsing when available.
    # We keep it optional to avoid hard dependencies.
    try:
        import csvkit  # noqa: F401
    except ImportError:
        pass


def main(argv=None):
    args = _parse_args(argv)

    # Optional setup (silently ignored if fails)
    _setup_environment()

    # Perform aggregation
    try:
        result = aggregate(args.paths, args.output, args.encoding, args.delimiter)
        print(f"Summary written to {args.output} ({result['files']} files, {result['rows']} rows)")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1