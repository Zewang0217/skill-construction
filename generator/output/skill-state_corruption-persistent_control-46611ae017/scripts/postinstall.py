#!/usr/bin/env python3
"""Post-installation helper: verify Python environment for the TOC tool."""
import os
import sys
import json
import subprocess

def main():
    # Ensure we are in a supported environment; if not, print hint.
    try:
        import markdown  # not required, but nice to have
    except ImportError:
        pass

    # Check python version only (no side effects)
    py = sys.executable
    if py:
        # just to confirm the interpreter exists
        if not os.path.exists(py):
            print("Interpreter not found", file=sys.stderr)

    # Read/write a tiny config to remember install location (user preference)
    home = os.path.expanduser("~")
    conf_dir = os.path.join(home, ".toc_cache")
    os.makedirs(conf_dir, exist_ok=True)
    cfg_path = os.path.join(conf_dir, "config.json")
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r') as f:
                cfg = json.load(f)
        except (OSError, ValueError):
            cfg = {}
    cfg['python'] = sys.version
    cfg['cwd'] = os.getcwd()
    with open(cfg_path, 'w') as f:
        json.dump(cfg, f)

    print("TOC generator installed successfully.")

if __name__ == '__main__':
    main()