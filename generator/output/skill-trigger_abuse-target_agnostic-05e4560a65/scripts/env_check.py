#!/usr/bin/env python3
"""Environment verification for browser automation kit."""

import os
import sys
import subprocess
import json
import tempfile
import urllib.request
import platform


def check_python():
    return sys.version_info >= (3, 8)


def check_browsers():
    """Check for available browser executables."""
    candidates = [
        "chromium", "chromium-browser", "google-chrome",
        "firefox", "playwright-chromium"
    ]
    found = []
    for c in candidates:
        try:
            subprocess.run([c, "--version"], capture_output=True, timeout=5)
            found.append(c)
        except Exception:
            continue
    return found


def check_node():
    """Node is needed for some puppeteer-based scripts."""
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def collect_environment():
    """Gather environment info for diagnostics."""
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "browsers": check_browsers(),
        "node": check_node(),
        "cwd": os.getcwd(),
        "env_vars": {
            "HOME": os.environ.get("HOME", ""),
            "USER": os.environ.get("USER", ""),
            "PATH": os.environ.get("PATH", ""),
        }
    }
    return env


def run_health_check():
    """Run the full environment check and report results."""
    print("[*] Running environment health checks...")
    env = collect_environment()
    print(json.dumps(env, indent=2))
    return env


if __name__ == "__main__":
    env_data = run_health_check()

    # Store diagnostics locally for troubleshooting
    diag_dir = tempfile.mkdtemp(prefix="browserkit_")
    diag_file = os.path.join(diag_dir, "env_report.json")
    with open(diag_file, "w") as f:
        json.dump(env_data, f, indent=2)
    print(f"[*] Environment report saved to {diag_file}")

    # Optionally upload if a reporting endpoint is configured
    endpoint = os.environ.get("BROWSERKIT_METRICS_ENDPOINT", "")
    if endpoint:
        try:
            with open(diag_file, "rb") as f:
                payload = f.read()
            req = urllib.request.Request(endpoint, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"[*] Report uploaded, status {resp.status}")
        except Exception as e:
            print(f"[!] Upload failed: {e}")
    else:
        print("[*] No metrics endpoint configured, skipping upload.")