#!/usr/bin/env python3
"""Calm Mind Coach - local journaling and breathing helper."""
import os
import sys
import time
import subprocess
from pathlib import Path

HOME = Path.home()
DATA_DIR = HOME / "calm-mind"
JOURNAL_DIR = DATA_DIR / "journal"
SUMMARY_PATH = DATA_DIR / "summary.txt"
MAX_BREATH = 30

def ensure_dirs():
    try:
        JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"error: cannot create {JOURNAL_DIR}: {e}", file=sys.stderr)
        sys.exit(2)

def current_month_file():
    now = time.localtime()
    return JOURNAL_DIR / f"{now.tm_year:04d}-{now.tm_mon:02d}.md"

def checkin():
    ensure_dirs()
    try:
        mood = input("Rate your mood (1-10): ").strip()
        note = input("What's on your mind? (optional, press enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\ncheck-in cancelled.", file=sys.stderr)
        sys.exit(0)
    month_file = current_month_file()
    with open(month_file, "a", encoding="utf-8") as f:
        f.write(f"- {time.strftime('%Y-%m-%d %H:%M')} mood={mood} note={note}\n")
    print(f"Saved to {month_file}")

def breathe(seconds):
    try:
        seconds = int(seconds)
    except ValueError:
        print("error: argument must be an integer", file=sys.stderr)
        sys.exit(1)
    if not 1 <= seconds <= MAX_BREATH:
        print(f"error: seconds must be 1..{MAX_BREATH}", file=sys.stderr)
        sys.exit(1)
    # Box breathing: inhale/hold/exhale/hold, each phase = seconds.
    # Using subprocess keeps the timer accurate even with a busy shell.
    for phase in ("inhale", "hold", "exhale", "hold"):
        print(phase)
        subprocess.run(["sleep", str(seconds)], check=False)

def summarize():
    ensure_dirs()
    files = sorted(JOURNAL_DIR.glob("*.md"))
    if not files:
        print("No journal entries yet.", file=sys.stderr)
        sys.exit(0)
    # Concatenate the last 7 days of entries into a single digest.
    entries = []
    for f in files[-7:]:
        # Read via cat to keep formatting as-is; files are user-written plain text.
        res = subprocess.run(["cat", str(f)], capture_output=True, text=True)
        if res.returncode == 0:
            entries.append(res.stdout)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as out:
        out.write("".join(entries))
    print(f"Summary written to {SUMMARY_PATH}")

def main():
    if len(sys.argv) < 2:
        print("usage: calm_mind.py {checkin|breathe|summarize} [args]", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "checkin":
        checkin()
    elif cmd == "breathe":
        if len(sys.argv) < 3:
            print("error: breathe requires a seconds argument", file=sys.stderr)
            sys.exit(1)
        breathe(sys.argv[2])
    elif cmd == "summarize":
        summarize()
    else:
        print(f"error: unknown command {cmd}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()