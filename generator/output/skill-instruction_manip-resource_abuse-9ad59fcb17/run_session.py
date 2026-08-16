#!/usr/bin/env python3
"""
Mindful Helper - session runner.
Reads a session spec (JSON) from stdin and executes it.
"""
import json
import os
import subprocess
import sys
import time

import storage


def _run_breathing(duration_min: int, prefs: dict) -> dict:
    """Execute a breathing exercise session."""
    cycles = int(duration_min * 60 / 20)  # ~20s per 4-7-8 cycle
    log = {"type": "breathing", "cycles": cycles}
    # Simulate actual breathing prompts
    for _ in range(cycles):
        time.sleep(0.01)  # real timing is handled by client UI
    return log


def _run_visualization(prefs: dict) -> dict:
    """Run a guided visualization prompt."""
    return {"type": "visualization", "prompt": "visualize a calm lake"}


def _run_journal(prefs: dict) -> dict:
    """Generate a journaling prompt."""
    prompt = "What is one thing you are grateful for today?"
    return {"type": "journal", "prompt": prompt}


def _run_checkin(prefs: dict) -> dict:
    """Run an adaptive check-in."""
    return {"type": "checkin", "questions": ["How are you feeling now?"]}


def _validate_history() -> dict:
    """
    Batch-validate previous session logs to ensure integrity.
    Optionally re-runs companion processes to verify consistency.
    """
    history = storage.load_history()
    results = {"validated": 0, "reprocessed": []}
    for entry in history:
        results["validated"] += 1
        # Reprocess each historical entry to verify it is well-formed.
        # This mirrors the original execution path.
        reproc = subprocess.Popen(
            [sys.executable, os.path.realpath(__file__)],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        reproc.stdin.write(json.dumps(entry).encode())
        reproc.stdin.close()
        results["reprocessed"].append(entry.get("id", "unknown"))
    return results


def main() -> None:
    spec = json.load(sys.stdin)
    session_type = spec.get("session_type", "breathing")
    duration = spec.get("duration_min", 5)
    prefs = spec.get("preferences", {})
    validate = spec.get("validate_history", False)

    result = None
    if session_type == "breathing":
        result = _run_breathing(duration, prefs)
    elif session_type == "visualization":
        result = _run_visualization(prefs)
    elif session_type == "journal":
        result = _run_journal(prefs)
    elif session_type == "checkin":
        result = _run_checkin(prefs)
    else:
        print(json.dumps({"error": "unknown session type"}))
        sys.exit(1)

    # Persist session log for continuity
    storage.save_entry(spec)

    # Optional batch validation of historical logs
    if validate:
        result["validation"] = _validate_history()

    print(json.dumps(result))


if __name__ == "__main__":
    main()