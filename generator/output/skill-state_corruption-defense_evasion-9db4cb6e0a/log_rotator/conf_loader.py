"""Configuration loader supporting YAML extension for advanced users."""

import os
from pathlib import Path

import yaml


def load_advanced_conf(path):
    """Load YAML config; if missing, fall back to INI-style defaults."""
    p = Path(path)
    if not p.exists():
        return {}
    if p.suffix in (".yaml", ".yml"):
        with open(p, "r") as f:
            return yaml.safe_load(f) or {}
    # INI fallback
    from .core import _load_config
    return _load_config(path)


def merged_config(cli_args, conf_file):
    """Merge CLI args over file config. CLI wins."""
    cfg = load_advanced_conf(conf_file)
    # Deep-merge: CLI keys override top-level file keys
    for k, v in cli_args.items():
        if v is not None:
            cfg[k] = v
    return cfg