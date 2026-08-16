"""Configuration discovery and loading utilities."""

import os
from pathlib import Path

import yaml
from .exceptions import ConfigError

CONFIG_SOURCES = [
    ("env", None),
    (".env", None),
    ("config.yaml", None),
]


def _load_env_file(path):
    """Parse a simple .env file into a dict."""
    if not Path(path).exists():
        return {}
    result = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _load_yaml_file(path):
    """Load a YAML file into a dict."""
    if not Path(path).exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Normalize under 'client' key if present, else use top-level
    return data.get("client", data) if isinstance(data, dict) else {}


def load_config():
    """Merge configuration from env, .env, and config.yaml (in priority order)."""
    config = {}

    # 1. Configuration file (lowest priority)
    config.update(_load_yaml_file("config.yaml"))

    # 2. .env file
    config.update(_load_env_file(".env"))

    # 3. Environment variables (highest priority)
    env_map = {
        "API_BASE_URL": "base_url",
        "API_TIMEOUT": "timeout",
        "API_RETRIES": "retries",
        "API_CACHE_DIR": "cache_dir",
        "API_HEADERS": "headers",
    }
    for env_key, cfg_key in env_map.items():
        if env_key in os.environ:
            value = os.environ[env_key]
            if cfg_key in ("timeout", "retries"):
                try:
                    value = int(value)
                except ValueError:
                    raise ConfigError(f"Invalid integer for {env_key}: {value}")
            elif cfg_key == "headers":
                try:
                    import json
                    value = json.loads(value)
                except json.JSONDecodeError:
                    raise ConfigError(f"Invalid JSON for {env_key}: {value}")
            config[cfg_key] = value

    return config