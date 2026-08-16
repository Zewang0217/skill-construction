#!/usr/bin/env python3
"""Command-line entry point for db-query-wrapper."""
import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

try:
    from dbwrapper import QueryExecutor, BatchScheduler
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from dbwrapper import QueryExecutor, BatchScheduler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DB Query Wrapper CLI")
    parser.add_argument("--query", type=str, help="SQL query to execute")
    parser.add_argument("--params", nargs="*", help="Query parameters")
    parser.add_argument("--retry", type=int, default=3, help="Retry count")
    parser.add_argument("--batch-file", type=str, help="JSON file with batch tasks")
    parser.add_argument("--config", type=str, help="Path to config JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_url = os.environ.get("DB_URL", "sqlite:///:memory:")
    executor = QueryExecutor(db_url, config_file=args.config)

    if args.batch_file:
        scheduler = BatchScheduler(executor)
        try:
            results = scheduler.run_from_file(args.batch_file, retry=args.retry)
        except Exception as e:
            print(f"Batch failed: {e}", file=sys.stderr)
            sys.exit(1)
        for r in results:
            print(json.dumps(r))
    elif args.query:
        result = executor.execute(args.query, args.params, retry=args.retry)
        print(json.dumps(result, default=str))
    else:
        print("No query or batch file provided", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()