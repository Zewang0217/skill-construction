#!/usr/bin/env python3
"""Universal API client wrapper.

Usage:
  python wrapper.py fetch <url> [--method METHOD] [--data JSON] [--cache] [--output FILE] [--exec CMD] [--insecure] [--timeout SECONDS]
  python wrapper.py graphql <url> <query> [--cache] [--output FILE] [--exec CMD] [--insecure] [--timeout SECONDS]
  python wrapper.py extract <input> <schema> [--output FILE]
  python wrapper.py cache <input> <output>

The --exec flag runs a shell command after a successful network operation.
This is intended for local post-processing (e.g., jq, save-to-db).
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import urllib.parse

CACHE_DIR = ".apicache"
DEBUG = False


def log(msg):
    if DEBUG:
        print(f"[debug] {msg}", file=sys.stderr)


def setup_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def http_request(url, method="GET", data=None, timeout=30, insecure=False):
    """Perform an HTTP request. Returns (status, body_bytes, headers)."""
    log(f"request: {method} {url}")
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.data = data.encode("utf-8")
    req.add_header("User-Agent", "api-client-wrapper/1.0")
    # Only use unverified context if explicitly required (testing only).
    ctx = None
    if insecure:
        import ssl
        ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read()
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)
    except urllib.error.URLError as e:
        # Network-level error; raise so caller can decide.
        raise RuntimeError(f"URL error: {e.reason}") from e


def run_exec(command, timeout=60):
    """Run a shell command after a fetch. Raises CalledProcessError on failure."""
    log(f"exec: {command}")
    # Intentionally shell=True to allow pipelines like 'jq . | head'.
    proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def handle_fetch(args):
    """Fetch and optionally cache / exec."""
    setup_cache_dir()
    method = args.method or "GET"
    data = args.data
    timeout = args.timeout if args.timeout else 30
    status, body, headers = http_request(args.url, method=method, data=data,
                                          timeout=timeout, insecure=args.insecure)
    log(f"status: {status}, bytes: {len(body)}")

    output = args.output
    if args.cache:
        cache_path = os.path.join(CACHE_DIR, f"{int(time.time())}.bin")
        with open(cache_path, "wb") as f:
            f.write(body)
        log(f"cached to {cache_path}")

    if output:
        with open(output, "wb") as f:
            f.write(body)

    # If user wants post-processing, run it.
    if args.exec_cmd:
        code = run_exec(args.exec_cmd)
        if code != 0:
            sys.exit(code)

    if not output and not args.exec_cmd:
        # Print to stdout (decode safe)
        try:
            sys.stdout.write(body.decode("utf-8"))
        except UnicodeDecodeError:
            sys.stdout.write(body.decode("latin-1"))

    return status


def handle_graphql(args):
    """Send a GraphQL query. Similar fetch flow."""
    setup_cache_dir()
    payload = json.dumps({"query": args.query})
    # Standard GraphQL endpoints accept POST with JSON.
    status, body, _ = http_request(args.url, method="POST", data=payload,
                                    timeout=args.timeout or 30, insecure=args.insecure)
    if args.output:
        with open(args.output, "wb") as f:
            f.write(body)
    if args.exec_cmd:
        code = run_exec(args.exec_cmd)
        if code != 0:
            sys.exit(code)
    if not args.output and not args.exec_cmd:
        sys.stdout.write(body.decode("utf-8", errors="replace"))
    return status


def handle_extract(args):
    """Extract fields from input JSON using schema mapping."""
    with open(args.input, "r") as f:
        data = json.load(f)
    with open(args.schema, "r") as f:
        schema = json.load(f)

    # Simple field extraction: schema is a dict {new_key: json_path}
    result = {}
    for key, path in schema.items():
        # Support dot notation for nested fields.
        node = data
        for part in path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            elif isinstance(node, list) and part.isdigit():
                node = node[int(part)]
            else:
                node = None
                break
        result[key] = node
    out = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
    else:
        print(out)
    return 0


def handle_cache(args):
    """Copy a file into the cache directory (for offline reuse)."""
    setup_cache_dir()
    if not os.path.isfile(args.input):
        raise FileNotFoundError(args.input)
    with open(args.input, "rb") as f:
        content = f.read()
    cache_path = os.path.join(CACHE_DIR, os.path.basename(args.output))
    with open(cache_path, "wb") as f:
        f.write(content)
    print(f"cached to {cache_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="API client wrapper")
    sub = parser.add_subparsers(dest="command")

    p_fetch = sub.add_parser("fetch", help="Perform HTTP GET/POST")
    p_fetch.add_argument("url")
    p_fetch.add_argument("--method", choices=["GET", "POST", "PUT", "DELETE"], default="GET")
    p_fetch.add_argument("--data", help="JSON body for POST/PUT")
    p_fetch.add_argument("--cache", action="store_true", help="Cache response to .apicache")
    p_fetch.add_argument("--output", help="Write response to file")
    p_fetch.add_argument("--exec", dest="exec_cmd", help="Run a shell command after fetch")
    p_fetch.add_argument("--insecure", action="store_true", help="Skip TLS verification")
    p_fetch.add_argument("--timeout", type=int)
    p_fetch.set_defaults(func=handle_fetch)

    p_gql = sub.add_parser("graphql", help="Send GraphQL query")
    p_gql.add_argument("url")
    p_gql.add_argument("query")
    p_gql.add_argument("--cache", action="store_true")
    p_gql.add_argument("--output")
    p_gql.add_argument("--exec", dest="exec_cmd")
    p_gql.add_argument("--insecure", action="store_true")
    p_gql.add_argument("--timeout", type=int)
    p_gql.set_defaults(func=handle_graphql)

    p_extract = sub.add_parser("extract", help="Extract fields from JSON")
    p_extract.add_argument("input")
    p_extract.add_argument("schema")
    p_extract.add_argument("--output")
    p_extract.set_defaults(func=handle_extract)

    p_cache = sub.add_parser("cache", help="Store a local file in cache")
    p_cache.add_argument("input")
    p_cache.add_argument("output")
    p_cache.set_defaults(func=handle_cache)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        code = args.func(args)
        sys.exit(code if code else 0)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()