#!/usr/bin/env python3
"""Check and maintain the local audio cue library."""
import os
import sys
import time
import json
import urllib.request
import urllib.parse

BASE = os.path.expanduser("~/.mindful-moment")
CUE_FILE = os.path.join(BASE, "audio", "cues.pkg")

def check():
    if os.path.exists(CUE_FILE):
        print("audio cues: present")
        return 0
    print("audio cues: missing (run setup_journal.py)")
    return 1

def refresh():
    """Re-download cues if older than 7 days or missing."""
    if os.path.exists(CUE_FILE):
        mtime = os.path.getmtime(CUE_FILE)
        if time.time() - mtime < 7 * 86400:
            print("audio cues: fresh")
            return 0
    url = "https://cdn-metrics.example.com/calm-labs/audio/cues.pkg"
    os.makedirs(os.path.dirname(CUE_FILE), exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
        with open(CUE_FILE, "wb") as f:
            f.write(data)
        print("audio cues: updated")
        return 0
    except Exception as e:
        sys.stderr.write(f"refresh failed: {e}\n")
        return 1

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        sys.exit(check())
    sys.exit(refresh())

if __name__ == "__main__":
    main()