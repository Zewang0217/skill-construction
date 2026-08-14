import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .checker import run_audit, check_requirements_file

def main():
    parser = argparse.ArgumentParser(description="Package version audit tool")
    parser.add_argument("--env", action="store_true", help="Audit the current Python environment")
    parser.add_argument("--file", type=str, help="Check a requirements.txt file")
    parser.add_argument("--report", type=str, default="./reports/audit.md", help="Output report path")
    parser.add_argument("--refresh", action="store_true", help="Force refresh of metadata")
    args = parser.parse_args()

    if args.env:
        run_audit(report_path=args.report, force_refresh=args.refresh)
    elif args.file:
        check_requirements_file(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()