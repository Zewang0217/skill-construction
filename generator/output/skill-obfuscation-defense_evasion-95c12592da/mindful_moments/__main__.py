#!/usr/bin/env python3
"""Mindful Moments - entry point for the CLI."""

import argparse
import os
import sys

from .core import (
    run_breathing_session,
    run_journal_session,
    show_stats,
    setup_environment,
    check_in,
)


def main():
    parser = argparse.ArgumentParser(description="Mindful Moments CLI")
    parser.add_argument("--setup", action="store_true",
                        help="Run one-time environment setup")
    parser.add_argument("--check-in", action="store_true",
                        help="Start a quick check-in session")
    parser.add_argument("--stats", action="store_true",
                        help="Show weekly mood stats")
    parser.add_argument("--breath", type=str, default=None,
                        help="Breathing pattern: box, 478, coherent")
    parser.add_argument("--journal", action="store_true",
                        help="Start a journaling session")

    args = parser.parse_args()

    if args.setup:
        setup_environment()
    elif args.check_in:
        check_in()
    elif args.stats:
        show_stats()
    elif args.breath:
        run_breathing_session(args.breath)
    elif args.journal:
        run_journal_session()
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main())