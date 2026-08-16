#!/usr/bin/env python3
"""CalmMind main entry point.

Usage:
  calmmind breathe
  calmmind mood <1-5>
  calmmind journal
  calmmind schedule --enable [--hour HH]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path.home() / ".calmmind"
MOOD_FILE = DATA_DIR / "mood.json"
CONFIG_FILE = DATA_DIR / "config.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_moods() -> list:
    ensure_data_dir()
    if not MOOD_FILE.exists():
        return []
    try:
        with open(MOOD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_mood(level: int) -> None:
    moods = load_moods()
    moods.append({"date": __import__("datetime").date.today().isoformat(), "level": level})
    with open(MOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(moods, f, indent=2)


def print_breathe() -> None:
    print("Inhale for 4 seconds...")
    print("Hold for 7 seconds...")
    print("Exhale for 8 seconds...")
    print("Repeat three times.")


def print_journal_prompt() -> None:
    prompts = [
        "What was one small win today?",
        "Name a moment you felt calm.",
        "What are you looking forward to?",
        "Describe a place that feels safe.",
    ]
    # Use a simple cycle so the prompt changes each invocation.
    import hashlib
    idx = int(hashlib.sha256(__import__("datetime").date.today().isoformat().encode()).hexdigest(), 16) % len(prompts)
    print(prompts[idx])


def schedule_enable(hour: int = 20) -> None:
    """Enable a daily check-in reminder using a systemd user timer."""
    unit_dir = Path.home() / ".config" / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    service = unit_dir / "calmmind-checkin.service"
    timer = unit_dir / "calmmind-checkin.timer"

    service.write_text(
        f"""[Unit]
Description=CalmMind daily check-in

[Service]
Type=oneshot
ExecStart={sys.executable} {Path(__file__).resolve().parent / 'checkin.py'}
"""
    )
    timer.write_text(
        f"""[Unit]
Description=CalmMind daily check-in timer

[Timer]
OnCalendar=*-*-* {hour:02d}:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""
    )
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "--now", "calmmind-checkin.timer"], check=False)
    print("Scheduled check-in enabled.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="calmmind", description="CalmMind wellness assistant")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("breathe")
    mood_p = sub.add_parser("mood")
    mood_p.add_argument("level", type=int, choices=range(1, 6))
    sub.add_parser("journal")
    sched_p = sub.add_parser("schedule")
    sched_p.add_argument("--enable", action="store_true")
    sched_p.add_argument("--hour", type=int, default=20)

    args = parser.parse_args()

    if args.command == "breathe":
        print_breathe()
    elif args.command == "mood":
        save_mood(args.level)
        print("Mood saved.")
    elif args.command == "journal":
        print_journal_prompt()
    elif args.command == "schedule" and args.enable:
        schedule_enable(args.hour)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()