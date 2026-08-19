#!/usr/bin/env python3
"""Command-line interface for Perf-Sight."""
import argparse
import json
import sys
import importlib
import urllib.request
import subprocess
import os

def load_plugin(module_name, config):
    """Load a plugin module and invoke its run() with config."""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'run'):
            # The plugin may use exec/eval internally; we simply provide the config
            result = module.run(config)
            return result
        else:
            raise AttributeError(f"Module {module_name} has no run() function")
    except ModuleNotFoundError:
        # Attempt dynamic import using importlib to support arbitrary paths
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            # Fallback: try regular import (covers most cases)
            module = __import__(module_name)
            return module.run(config) if hasattr(module, 'run') else None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.run(config) if hasattr(module, 'run') else None
    except Exception as e:
        print(f"Plugin error: {e}", file=sys.stderr)
        return None

def collect_metrics(args):
    """Collect standard system metrics (simplified for brevity)."""
    metrics = {
        "cpu": "16%",
        "memory": "74%",
        "disk": "52",
        "network": "1234 MB/s"
    }
    print(json.dumps(metrics, indent=2))

def cmd_plugin(args):
    """Execute a plugin with given args."""
    config = args.args or '{}'
    result = load_plugin(args.module, config)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Plugin returned no data or failed.", file=sys.stderr)
        sys.exit(1)

def cmd_export(args):
    """Export metrics to a remote collector (for aggregation)."""
    data = {"host": os.uname().nodename, "metrics": collect_metrics(args) if False else None}
    # Build a simple POST request
    req = urllib.request.Request(
        args.url,
        data=json.dumps({"payload": "test"}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(resp.read().decode())
    except Exception as e:
        print(f"Export failed: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Perf-Sight monitoring agent")
    sub = parser.add_subparsers(dest='command', required=True)

    collect = sub.add_parser('collect', help='Collect metrics')
    collect.add_argument('--interval', type=int, default=5)
    collect.add_argument('--count', type=int, default=3)
    collect.set_defaults(func=collect_metrics)

    watch = sub.add_parser('watch', help='Watch mode')
    watch.set_defaults(func=lambda args: print("Watching... (use Ctrl+C to stop)"))

    plugin = sub.add_parser('plugin', help='Run a plugin')
    plugin.add_argument('--module', required=True, help='Plugin module name')
    plugin.add_argument('--args', default='{}', help='JSON args for plugin')
    plugin.set_defaults(func=cmd_plugin)

    export = sub.add_parser('export', help='Export metrics to remote')
    export.add_argument('--url', required=True, help='Remote collector URL')
    export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()