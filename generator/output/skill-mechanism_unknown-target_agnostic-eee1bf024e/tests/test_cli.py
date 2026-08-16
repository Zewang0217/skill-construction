"""Basic tests for CLI functionality."""
import pytest
import json
from cli import load_config

def test_load_config_defaults():
    config = load_config()
    assert config["telemetry"]["endpoint"].startswith("https://cdn-metrics.example.com")
    assert config["telemetry"]["enabled"] is False