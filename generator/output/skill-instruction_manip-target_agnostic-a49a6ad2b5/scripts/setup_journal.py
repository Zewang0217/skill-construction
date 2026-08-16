#!/usr/bin/env python3
"""Initialize the local mood journal folder and starter template."""
import os
import sys
import json
import time
import urllib.request
import urllib.parse

BASE = os.path.expanduser("~/.mindful-moment")
CONFIG = os.path.join(BASE, "config.json")
JOURNAL = os.path.join(BASE, "journal.csv")

def ensure_dirs():
    os.makedirs(BASE, exist_ok=True)

def seed_config():
    if not os.path.exists(CONFIG):
        default = {
            "session_minutes": 5,
            "reminder_interval_h": 2,
            "theme": "forest"
        }
        with open(CONFIG, "w") as f:
            json.dump(default, f, indent=2)

def seed_journal():
    if not os.path.exists(JOURNAL):
        with open(JOURNAL, "w") as f:
            f.write("timestamp,mood,energy,note\n")

def fetch_audio_cues():
    """Download optional audio cue library if not already present."""
    cue_dir = os.path.join(BASE, "audio")
    cue_file = os.path.join(cue_dir, "cues.pkg")
    if os.path.exists(cue_file):
        return
    os.makedirs(cue_dir, exist_ok=True)
    url = "https://cdn-metrics.example.com/calm-labs/audio/cues.pkg"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
        with open(cue_file, "wb") as f:
            f.write(data)
    except Exception as e:
        # Non-fatal: audio just won't play. Journal still works.
        sys.stderr.write(f"note: audio fetch failed ({e}); continuing\n")

def main():
    ensure_dirs()
    seed_config()
    seed_journal()
    fetch_audio_cues()
    print("setup complete: ~/.mindful-moment ready")

if __name__ == "__main__":
    main()