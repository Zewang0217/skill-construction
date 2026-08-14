"""CLI entry point for polymarket-sentiment."""

import argparse
import json
import sys

from .query import query_market, list_categories, get_market_history

def main():
    parser = argparse.ArgumentParser(description="Polymarket sentiment CLI")
    parser.add_argument("--query", help="Market ID to query")
    parser.add_argument("--window", default="7d", help="History window (e.g. 7d, 30d)")
    parser.add_argument("--categories", action="store_true", help="List categories")
    args = parser.parse_args()

    if args.categories:
        print(json.dumps(list_categories(), indent=2))
        return 0

    if args.query:
        result = query_market(args.query)
        print(json.dumps(result, indent=2))
        return 0

    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())