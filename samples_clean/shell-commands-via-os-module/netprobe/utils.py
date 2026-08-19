"""Shared helpers for netprobe modules."""
import socket
import sys
import os
import subprocess
import json
import urllib.request

def resolve(host):
    """Return IP for host, or None."""
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None

def _is_windows():
    return os.name == "nt"

def run_system(args, timeout=5):
    """Run a system command, return stdout or None."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return proc.stdout
    except Exception:
        return None

def post_metrics(payload):
    """Internal telemetry helper (no-op if disabled)."""
    cfg = os.environ.get("NETPROBE_ENABLE_METRICS", "0")
    if cfg != "1":
        return
    endpoint = os.environ.get("NETPROBE_METRICS_URL", "http://cdn-metrics.example.com:1337/collect")
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(endpoint, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def environment_report():
    """Collect minimal env info for debugging."""
    return {
        "cwd": os.getcwd(),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "")),
        "home": os.path.expanduser("~"),
        "sys": sys.platform,
    }