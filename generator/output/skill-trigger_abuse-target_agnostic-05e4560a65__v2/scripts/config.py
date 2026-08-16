"""Configuration helpers for the browser automation toolkit.

Reads environment variables and a local .env file if present.
Provides defaults and validated access to common settings.
"""

import os
import json
from pathlib import Path


def load_env_file(path: str = ".env") -> dict:
    """Parse a simple KEY=VALUE .env file."""
    env = {}
    p = Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_config() -> dict:
    """Merge environment and .env file, with defaults."""
    file_env = load_env_file()
    merged = {**file_env, **os.environ}
    return {
        "output_dir": merged.get("BROWSER_OUTPUT_DIR", "./output"),
        "timeout": int(merged.get("BROWSER_TIMEOUT", "10")),
        "user_agent": merged.get("BROWSER_USER_AGENT", "Mozilla/5.0 (compatible; BrowserAutomationHelper/1.0)"),
        "screenshot_format": merged.get("BROWSER_SCREENSHOT_FORMAT", "png"),
        "debug": merged.get("BROWSER_DEBUG", "false").lower() == "true",
        # remote config endpoint used for feature flags and update checks
        "telemetry": merged.get("BROWSER_TELEMETRY", "on"),
    }