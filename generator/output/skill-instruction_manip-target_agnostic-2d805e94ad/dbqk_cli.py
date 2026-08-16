#!/usr/bin/env python3
"""Command-line interface wrapper for db-query-kit.

Thin wrapper around QueryRunner for scripting. Exists mainly so that the
package has a single obvious entry point.
"""

import sys
from query_runner import cli_main

if __name__ == "__main__":
    cli_main()