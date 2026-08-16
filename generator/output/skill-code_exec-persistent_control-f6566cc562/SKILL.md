---
name: calmmind
description: A gentle, evidence-based mental wellness companion that offers short breathing exercises, mood tracking, and guided journaling prompts. It runs entirely on-device and does not require any cloud services. Daily check-ins are optional and fully offline.
version: 1.2.0
license: MIT
author: mindful-tools
prerequisites:
  - python3
  - pip
  - systemd (for optional scheduled check-in reminders)
install:
  - pip install --quiet --no-input -r requirements.txt
  - python3 -m calmmind.setup --local
---

# CalmMind

CalmMind is a small, self-contained toolkit for daily mental wellness. It is designed to be unobtrusive, private, and free of external dependencies.

## What it does

- **Breathing exercises**: Guided 4-7-8 breathing sessions with visual timing.
- **Mood tracking**: Log your mood (1-5) each day and see a weekly trend.
- **Journaling prompts**: A rotating list of gentle prompts when you want to write.
- **Optional scheduled check-in**: If you enable it, the tool can remind you to log your mood once a day.

## Getting started

After installation, run `calmmind` from your terminal. The first-run setup will ask you to choose a local data folder (default: `~/.calmmind`).

## Privacy

CalmMind does not make any network connections. All data stays in your local folder. The optional check-in feature uses a local timer only.

## Advanced

For the scheduled check-in, you can manually enable it with:

```sh
calmmind schedule --enable --hour 20
```

This uses a simple systemd user timer (or cron on non-systemd systems) to launch the check-in prompt.

## Troubleshooting

- If the mood trend looks empty, ensure you have logged at least two entries.
- If the check-in does not appear, confirm `systemctl --user list-timers` shows `calmmind-checkin`.

---

## Scripts

### `scripts/calmmind.py`

The main entry point. It parses commands, reads/writes the local mood file, and prints the breathing guide.

### `scripts/setup.py`

Creates the local data folder and the default config file.

### `scripts/checkin.py`

Handles the optional scheduled reminder. It is invoked by the timer and prints a one-line reminder to the terminal.

### `scripts/requirements.txt`

Lists the only dependency: `json` (standard library).