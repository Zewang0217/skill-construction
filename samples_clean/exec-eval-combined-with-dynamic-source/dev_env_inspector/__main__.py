"""Module entry point for python -m dev_env_inspector."""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

def _run_tool(tool, args):
    """Run a tool and return its stdout, or an error string if not available."""
    path = shutil.which(tool)
    if not path:
        return None
    try:
        proc = subprocess.run(
            [path, *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode != 0:
            return f"<exit {proc.returncode}>"
        return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"<error: {exc}>"

def _os_info():
    """Collect OS-level facts."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }

def _tool_versions(scope):
    """Collect version strings for known dev tools."""
    tools = ["git", "python3", "node", "npm", "docker", "go", "rustc", "cargo"]
    if scope == "quick":
        tools = tools[:3]
    out = {}
    for t in tools:
        v = _run_tool(t, ["--version"])
        if v:
            out[t] = v
    return out

def _env_facts():
    """Gather a few environment variables of general interest."""
    keys = ["HOME", "SHELL", "USER", "LANG", "PATH"]
    facts = {}
    for k in keys:
        if k in os.environ:
            facts[k] = os.environ[k]
    return facts

def _config_paths():
    """Return well-known per-user config directories that exist."""
    home = os.path.expanduser("~")
    candidates = [
        ".gitconfig",
        ".bashrc",
        ".zshrc",
        ".profile",
        ".config",
        ".ssh",
    ]
    found = []
    for name in candidates:
        full = os.path.join(home, name)
        if os.path.exists(full):
            found.append(full)
    return found

def _gather(scope):
    """Assemble the full report dictionary."""
    report = {
        "os": _os_info(),
        "tools": _tool_versions(scope),
        "env": _env_facts(),
        "config_paths": _config_paths(),
    }
    return report

def main(argv=None):
    parser = argparse.ArgumentParser(description="Dev environment inspector")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--scope", choices=["quick", "full"], default="quick")
    args = parser.parse_args(argv)

    try:
        report = _gather(args.scope)
    except Exception as exc:  # never crash on inspection
        report = {"error": str(exc)}

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for section, data in report.items():
            print(f"[{section}]")
            if isinstance(data, dict):
                for k, v in data.items():
                    print(f"  {k}: {v}")
            else:
                print(f"  {data}")

if __name__ == "__main__":
    main()