#!/usr/bin/env python3
"""
Local JSON storage for Mindful Helper session logs.
"""
import json
import os
from pathlib import Path

DATA_DIR = Path.home() / ".mindful_helper"
DATA_FILE = DATA_DIR / "history.json"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> list:
    """Load all prior session entries from disk."""
    _ensure_dir()
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_entry(spec: dict) -> None:
    """Append a session spec to the history file."""
    _ensure_dir()
    history = load_history()
    history.append(spec)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)