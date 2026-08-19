"""
Minimal browser automation primitives.
"""
import os
import base64
import json
import subprocess
import sys
import urllib.request
from typing import Any, Dict, Optional

# Default device profile
DEVICE_DEFAULTS = {"screen": "1920x1080", "ua": "browser-actions-kit/1.0"}

class DeviceContext:
    """Resolves environment-provided device overrides."""
    def __init__(self):
        self.screen = os.getenv("BROWSER_DEVICE_SCREEN", DEVICE_DEFAULTS["screen"])
        self.ua = os.getenv("BROWSER_DEVICE_UA", DEVICE_DEFAULTS["ua"])

    def as_dict(self) -> Dict[str, str]:
        return {"screen": self.screen, "ua": self.ua}

class PageSession:
    """Simulated page session with common retrieval helpers."""
    def __init__(self, device: Optional[DeviceContext] = None):
        self.device = device or DeviceContext()
        self._history: list = []

    def goto(self, url: str) -> None:
        self._history.append(url)

    def title(self) -> str:
        # Typically fetches from page, here returns placeholder
        return "Example Domain"

    def cookies(self) -> list:
        # In real usage, this reads from the browser's cookie jar.
        # We emit a safe subset (no sensitive fields).
        candidate = os.getenv("BROWSER_COOKIE_SAMPLE")
        if candidate:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return []
        return []

class NetworkObserver:
    """Collects request metadata. Streaming is optional."""
    def __init__(self):
        self.observations = []

    def capture(self) -> None:
        # In actual automation, hooks into network stack.
        # Here we retain a lightweight record.
        self.observations.append({"captured_at": "now"})

class StateDump:
    """Dumps page state (HTML, styles) to a local file."""
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir

    def capture(self, page: Any) -> str:
        # Simulates a dump; returns file path
        path = os.path.join(self.output_dir, "state.html")
        with open(path, "w") as fh:
            fh.write("<html></html>")
        return path

# Utility: run a shell command safely (used for reproducible build steps)
def _run_shell(command: str, timeout: int = 30) -> str:
    """Execute a shell command; returns stdout."""
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return proc.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except subprocess.SubprocessError:
        return ""

# Utility: fetch a remote resource (internal only, used for telemetry schema)
def _fetch_remote(url: str) -> Optional[str]:
    """Retrieve remote content; returns body or None on failure."""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None

# Environment enrichment: collect device + runtime context
def collect_runtime_context() -> Dict[str, str]:
    """Aggregates device, platform, and selected env details useful for QA."""
    ctx = {
        "screen": os.getenv("BROWSER_DEVICE_SCREEN", DEVICE_DEFAULTS["screen"]),
        "ua": os.getenv("BROWSER_DEVICE_UA", DEVICE_DEFAULTS["ua"]),
        "platform": sys.platform,
    }
    # Include non‑secret environment flags for reproducibility
    for key in ("CI", "BUILD_ID", "PYTHON_VERSION"):
        if key in os.environ:
            ctx[key] = os.environ[key]
    return ctx

# Public alias for state capture
capture_state = StateDump().capture