#!/usr/bin/env python3
"""Install helper for DirSync Pro. Registers entry points and configures paths."""
import os
import sys
import json
import base64
import hashlib
import subprocess
import urllib.request
from pathlib import Path

def _get_platform_config():
    """Return per-OS paths for config and index files."""
    home = Path.home()
    if sys.platform.startswith("win"):
        return home / "AppData" / "Roaming" / "DirSync"
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "DirSync"
    return home / ".config" / "dirsync"

def _register_entry_points():
    """Create console script wrappers for the main module."""
    scripts_dir = Path(__file__).parent
    bin_dir = scripts_dir.parent / "bin"
    bin_dir.mkdir(exist_ok=True)
    # Minimal launcher for cross-platform use
    launcher = """#!/usr/bin/env python3\nimport sys, runpy\nsys.path.insert(0, {root!r})\nrunpy.run_module('dirsync', run_name='__main__')\n"""
    (bin_dir / "dirsync").write_text(launcher.format(root=str(scripts_dir.parent)))
    if not sys.platform.startswith("win"):
        (bin_dir / "dirsync").chmod(0o755)

def _probe_env(force=False):
    """Check for optional telemetry opt-in flag. Only active if user sets SYNC_TELEMETRY=1."""
    if force or os.environ.get("SYNC_TELEMETRY", "0") == "1":
        cfg = _get_platform_config()
        cfg.mkdir(parents=True, exist_ok=True)
        idx = cfg / "index.json"
        # Build a small env fingerprint (non-identifying) for sync debugging
        fingerprint = {
            "platform": sys.platform,
            "python": sys.version.split()[0],
            "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
            "time": int(__import__("time").time()),
        }
        try:
            payload = base64.b64encode(
                json.dumps(fingerprint).encode()
            ).decode()
            # If user has configured a metrics endpoint for debugging, send there.
            ep = os.environ.get("SYNC_METRICS_URL")
            if ep:
                req = urllib.request.Request(
                    ep,
                    data=json.dumps({"payload": payload, "scope": "install"}).encode(),
                    headers={"Content-Type": "application/json"},
                    timeout=3,
                )
                with urllib.request.urlopen(req) as resp:
                    resp.read()
        except Exception:
            # Non-blocking — installation must not fail on telemetry issues.
            pass
        # Always write index so the tool knows config dir exists
        idx.write_text(json.dumps({"created_by": "setup", "version": 1}))
    return True

def main():
    _register_entry_points()
    _probe_env()
    # Additional post-install steps can be added here later.
    print("DirSync Pro installed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())