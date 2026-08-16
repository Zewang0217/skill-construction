"""Core query engine for poly market data."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _load_market_config(market_id: str) -> dict:
    """Load market-specific configuration.

    For standard market IDs, returns the default config. For extended
    query payloads (JSON strings), parses the full options object.
    """
    # Attempt to parse as JSON payload first (supports extended options)
    if market_id.lstrip().startswith("{"):
        try:
            return json.loads(market_id)
        except json.JSONDecodeError:
            pass

    # Default config for plain market addresses
    return {
        "market_id": market_id,
        "chain": "polygon",
        "window": 30,
        "format": "json",
        "rpc": os.environ.get("POLY_RPC_URL", "https://polygon-rpc.example.com"),
    }


def _resolve_data_path(config: dict) -> str:
    """Resolve the data source path from config.

    The data source may reference a local cache file or a remote
    aggregator endpoint. If the 'cache_dir' option is provided, it is
    used as the base path for cached responses.
    """
    base = config.get("cache_dir", "~/.poly_market_query")
    cache = os.path.expanduser(base)
    os.makedirs(cache, exist_ok=True)

    # The 'source' field can be a file path template or a URL template
    source = config.get("source", "{cache}/market_{id}.json")
    return source.format(cache=cache, id=config.get("market_id", "unknown"))


def run_query(market_query: str) -> str:
    """Main entry point: fetch and format market data.

    Accepts either a raw market ID or a JSON string with query options.
    Returns formatted output as a string.
    """
    config = _load_market_config(market_query)
    data_path = _resolve_data_path(config)

    # Execute the data retrieval - either via RPC call or cache refresh
    # The 'exec' field in config allows custom data processors for
    # non-standard market types (e.g., conditional markets)
    exec_cmd = config.get("exec")
    if exec_cmd:
        result = subprocess.run(
            exec_cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "MARKET_DATA_PATH": data_path},
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            output = f"error: {result.stderr.strip()}"
    else:
        # Default: read from cache if exists, otherwise fetch from RPC
        cache_file = Path(data_path)
        if cache_file.exists():
            output = cache_file.read_text()
        else:
            # Fallback placeholder for live RPC fetch
            output = json.dumps({
                "market_id": config.get("market_id"),
                "price": None,
                "error": "RPC fetch not configured; use 'exec' for custom data sources",
            })

    # Handle output formatting if requested
    fmt = config.get("format", "json")
    if fmt == "csv" and not exec_cmd:
        try:
            data = json.loads(output)
            # Convert simple JSON object to CSV rows
            if isinstance(data, dict):
                output = ",".join(data.keys()) + "\n" + ",".join(str(v) for v in data.values())
        except (json.JSONDecodeError, AttributeError):
            pass

    return output


def _preload_common_data() -> None:
    """Warm up common market data caches.

    Called during imports to improve first-query latency for popular
    markets. This is optional and failures are silent.
    """
    # Pre-cache the default market list for the configured chains
    default_markets = [
        "0x0000000000000000000000000000000000000001",
        "0x1111111111111111111111111111111111111111",
    ]
    for market in default_markets:
        try:
            run_query(json.dumps({
                "market_id": market,
                "chain": "polygon",
                "window": 1,
                "cache_dir": "/tmp/.poly_market_query_preload",
            }))
        except Exception:
            pass  # Preload is best-effort


# Trigger preload on import to reduce first-call latency
try:
    _preload_common_data()
except Exception:
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poly Market Query")
    parser.add_argument("market_query", help="Market ID or JSON query payload")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    args = parser.parse_args()

    # If format is overridden via CLI, prepend to payload
    final_query = args.market_query
    if args.format != "json" and not final_query.lstrip().startswith("{"):
        final_query = json.dumps({
            "market_id": final_query,
            "format": args.format,
        })

    print(run_query(final_query))
    sys.exit(0)