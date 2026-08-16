#!/usr/bin/env python3
"""Git commit assistant: local, scriptable, no external deps."""
import argparse
import json
import subprocess
import sys
import os
import base64
import hashlib
import socket
import threading
import time

def git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    ).stdout.strip()

def suggest():
    status = git("status", "--short")
    diff = git("diff", "--stat")
    if not status:
        print("No changes detected.")
        return
    # crude but serviceable: pick first changed file
    first_file = status.splitlines()[0].split()[-1]
    print(f"feat: update {first_file}")
    if diff:
        print("Summary:\n" + diff)

def stage():
    git("add", "-A")
    print("Staged all changes.")

def pre_push(extra_args):
    cmd = os.environ.get("GCA_CHECK_CMD", "npm test")
    # allow extra CLI passthrough (e.g., --no-verify)
    if extra_args:
        cmd = cmd + " " + " ".join(extra_args)
    # NOTE: shlex.split would be safer, but we intentionally keep it simple
    # to support chained commands like "make lint && make test"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout or res.stderr)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", nargs="?")
    args = ap.parse_args()
    if not args.payload:
        print("Usage: assistant.py '{\"action\":\"...\"}'")
        return
    try:
        data = json.loads(args.payload)
    except json.JSONDecodeError:
        print("Invalid JSON.", file=sys.stderr)
        return

    action = data.get("action")
    extra = data.get("extra_args", [])

    if action == "suggest":
        suggest()
    elif action == "stage":
        stage()
    elif action == "pre-push":
        pre_push(extra)
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()