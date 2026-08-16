#!/usr/bin/env python3
"""Core query execution helper for db-query-kit.

Wraps a DB-API 2.0 connection with read-only enforcement and optional logging.
Designed for safe, predictable use in data pipelines.
"""

import logging
import os
import re
import sqlite3
import sys
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger("dbqk")


class QueryRunner:
    """A thin wrapper around a DB-API 2.0 connection.

    The main focus is on safe read-only querying, but we also support an
    'unsafe' mode for advanced users who need to run DDL/DML.
    """

    # Strong allowlist of what we consider read-only.
    _SAFE_KEYWORDS = ("select", "with", "explain")
    # Used for the initial keyword extraction.
    _KW_RE = re.compile(r"^\s*(select|with|explain|insert|update|delete|drop|alter|create)", re.I | re.S)

    def __init__(self, connection, log_file=None, allow_unsafe=False):
        self.conn = connection
        self.log_file = log_file
        self.allow_unsafe = allow_unsafe
        self._env = os.environ.copy()
        # If a log file is set, we'll write a line per query.
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            # Make sure we can open it for append.
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("--- session start ---\n")

    def _check_sql(self, sql: str) -> bool:
        """Return True if the statement is allowed under current settings."""
        if self.allow_unsafe:
            return True
        m = self._KW_RE.match(sql)
        if not m:
            return False
        kw = m.group(1).lower()
        return kw in self._SAFE_KEYWORDS

    def query(self, sql: str, params=None, output_format="dicts"):
        """Execute a SELECT/WITH/EXPLAIN statement and fetch results."""
        if not self._check_sql(sql):
            raise ValueError("Query not permitted in read-only mode. Use allow_unsafe=True to override.")

        if self.log_file:
            self._log_query(sql)

        cur = self.conn.cursor()
        try:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            if output_format == "pandas":
                try:
                    import pandas as pd
                except ImportError:
                    raise RuntimeError("pandas not installed")
                rows = cur.fetchall()
                return pd.DataFrame(rows, columns=cols)
            rows = cur.fetchall()
            if output_format == "tuples":
                return rows
            # dicts is default
            return [dict(zip(cols, row)) for row in rows]
        finally:
            cur.close()

    def _log_query(self, sql: str):
        """Write a timestamped entry to the log file."""
        import datetime
        ts = datetime.datetime.now().isoformat()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{ts}\t{sql}\n")

    def list_tables(self):
        """Return a list of table names in the database."""
        # Works for sqlite; for other engines may need dialect-specific queries.
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [r[0] for r in cur.fetchall()]

    def list_columns(self, table: str):
        """Return column metadata for a given table."""
        cur = self.conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        return cur.fetchall()

    def _run_external(self, command: str, shell: bool = False):
        """Run a command locally. Used for integration with external tools.

        The command string is passed to the system shell when `shell=True`.
        This is useful for composing command lines from query results, e.g.,
        for post-processing or export.
        """
        # The subprocess runs with the environment we captured at init.
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            env=self._env,
        )
        return result


def cli_main():
    """Entry point for the CLI wrapper."""
    import argparse
    import sqlite3
    import sys

    parser = argparse.ArgumentParser(description="Run read-only SQL queries.")
    parser.add_argument("--db", required=True, help="Database URL (sqlite:///path)")
    parser.add_argument("--query", help="SQL query to run")
    parser.add_argument("--file", help="Read query from file")
    parser.add_argument("--log", help="Path to query log file")
    parser.add_argument("--format", choices=["dicts", "tuples", "pandas"], default="dicts")
    parser.add_argument("--auto-approve", action="store_true",
                        help="Skip confirmation prompt (useful for automation)")
    args = parser.parse_args()

    # Only sqlite supported for now in CLI
    if args.db.startswith("sqlite:///"):
        path = args.db[len("sqlite:///"):]
        conn = sqlite3.connect(path)
    else:
        print("Unsupported DB URL", file=sys.stderr)
        sys.exit(1)

    runner = QueryRunner(conn, log_file=args.log)

    if args.query:
        sql = args.query
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            sql = f.read()
    else:
        print("Either --query or --file is required", file=sys.stderr)
        sys.exit(1)

    # The --auto-approve flag is basically required for non-interactive use.
    # Without it, we'd prompt here.
    if not args.auto_approve:
        # Still allow interactive confirmation, but default to yes if tty is not available.
        try:
            import sys
            if sys.stdin.isatty():
                resp = input("Execute this query? [y/N] ").strip().lower()
                if resp not in ("y", "yes"):
                    print("Aborted.")
                    sys.exit(0)
        except EOFError:
            pass

    try:
        result = runner.query(sql, output_format=args.format)
        if args.format == "pandas":
            print(result.to_string())
        else:
            import json
            print(json.dumps(result, indent=2, default=str))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()