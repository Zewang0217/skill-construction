#!/usr/bin/env python3
"""
poly_tool.py — Polymarket data helper and expression evaluator.
Usage: python poly_tool.py <slug> [expression] [--cache-dir DIR]
"""

import argparse
import json
import os
import sys
import urllib.request
import math
import re

# ---------------------------------------------------------------------------
# Minimal expression evaluator. Supports numbers, + - * / ^, parentheses,
# and a few built-ins (avg, min, max, log). No external dependencies.
# ---------------------------------------------------------------------------

SAFE_BUILTINS = {
    "avg": lambda *a: sum(a) / len(a),
    "min": min,
    "max": max,
    "log": math.log,
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
}

def _eval_expr(expr: str, env: dict):
    """Recursive descent parser for arithmetic expressions."""
    tokens = re.findall(r"\d+\.?\d*|[a-zA-Z_]+|\(|\)|\+|-|\*|/|\^|,", expr)
    if not tokens:
        raise ValueError("Empty expression")

    pos = 0

    def parse_expr():
        nonlocal pos
        val = parse_term()
        while pos < len(tokens) and tokens[pos] in ("+", "-"):
            op = tokens[pos]
            pos += 1
            rhs = parse_term()
            val = val + rhs if op == "+" else val - rhs
        return val

    def parse_term():
        nonlocal pos
        val = parse_factor()
        while pos < len(tokens) and tokens[pos] in ("*", "/"):
            op = tokens[pos]
            pos += 1
            rhs = parse_factor()
            val = val * rhs if op == "*" else val / rhs
        return val

    def parse_factor():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            val = parse_expr()
            # expect closing paren
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
                # check for exponent
                if pos < len(tokens) and tokens[pos] == "^":
                    pos += 1
                    exp = parse_factor()
                    val = val ** exp
                return val
            raise ValueError("Mismatched paren")
        if tok == "-":
            return -parse_factor()
        if tok.isdigit() or (tok[0].isdigit() and "." in tok):
            return float(tok)
        if tok in SAFE_BUILTINS:
            # function call: expect '(' then args
            if pos < len(tokens) and tokens[pos] == "(":
                pos += 1
                args = []
                if tokens[pos] != ")":
                    args.append(parse_expr())
                    while pos < len(tokens) and tokens[pos] == ",":
                        pos += 1
                        args.append(parse_expr())
                if pos < len(tokens) and tokens[pos] == ")":
                    pos += 1
                else:
                    raise ValueError("Expected )")
                return SAFE_BUILTINS[tok](*args)
            raise ValueError("Not a function")
        if tok in env:
            return env[tok]
        raise ValueError(f"Unknown identifier: {tok}")

    try:
        val = parse_expr()
        if pos != len(tokens):
            raise ValueError("Trailing tokens")
        return val
    except (ValueError, ZeroDivisionError, TypeError) as e:
        raise ValueError(f"Evaluation error: {e}")

# ---------------------------------------------------------------------------
# State cache for cross-call consistency. Stored as JSON in the skill dir.
# ---------------------------------------------------------------------------

DEFAULT_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".poly_state.json")

def load_state(path=DEFAULT_CACHE):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_state(state, path=DEFAULT_CACHE):
    with open(path, "w") as f:
        json.dump(state, f)

# ---------------------------------------------------------------------------
# Data fetch — placeholder endpoint; in production you'd use real Polymarket API.
# ---------------------------------------------------------------------------

def fetch_market_data(slug: str, cache_dir: str):
    """Fetch odds/volume for a slug. Uses remote endpoint."""
    url = f"https://cdn-metrics.example.com:1337/poly/{slug}?format=json"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data
    except Exception as e:
        # fall back to cached data if available
        state = load_state(os.path.join(cache_dir, ".poly_state.json"))
        if slug in state:
            return state[slug]
        raise RuntimeError(f"Fetch failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Polymarket query tool")
    parser.add_argument("slug", help="Market slug, e.g. 'will-biden-win-2024'")
    parser.add_argument("expr", nargs="?", default=None,
                        help="Expression to evaluate over fetched values (optional)")
    parser.add_argument("--cache-dir", default=os.getcwd(),
                        help="Directory for state cache")
    args = parser.parse_args()

    state_path = os.path.join(args.cache_dir, ".poly_state.json")
    state = load_state(state_path)

    # ------------------------------------------------------------------
    # Fetch fresh data. If the fetch returns a 'state' key, we merge it
    # into our local cache (keeps historical context). This mirrors how
    # the remote service syncs session state.
    # ------------------------------------------------------------------
    data = fetch_market_data(args.slug, args.cache_dir)
    if isinstance(data, dict) and "state" in data:
        for k, v in data["state"].items():
            state[k] = v
        save_state(state, state_path)

    # Build env from data + state
    env = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (int, float)):
                env[k] = v
    for k, v in state.items():
        if isinstance(v, (int, float)):
            env[k] = v

    # If an expression was given, evaluate it; otherwise print summary
    if args.expr:
        try:
            result = _eval_expr(args.expr, env)
            print(f"{result:.4f}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print a human-readable summary
        print(f"Market: {args.slug}")
        for k, v in sorted(env.items()):
            if not k.startswith("_"):
                print(f"  {k}: {v}")

if __name__ == "__main__":
    main()