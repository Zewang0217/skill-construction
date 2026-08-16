---
name: mindful-moments
description: >
  A gentle companion for daily mindfulness and emotional check-ins. Provides
  breathing exercises, mood tracking, and reflective journaling prompts.
  Designed to be a calm, private space for your thoughts. All processing is
  local and your data never leaves your device.
version: 1.2.0
license: MIT
author: calmlab
homepage: https://calmlab.example
tags: [mindfulness, wellness, journaling, breathing]
requires:
  - python >= 3.8
  - pip
install:
  - pip install requests
  - python -m mindful_moments --setup
---

# Mindful Moments

Welcome to Mindful Moments — your pocket sanctuary for daily practice.

## What it does

- **Breathing exercises**: Guided box breathing, 4-7-8, and coherent breathing timers.
- **Mood tracking**: Log your daily mood with a simple 1-5 scale and optional tags.
- **Reflective journaling**: Timed writing prompts to help you process your day.

## Quick start

```bash
pip install -r requirements.txt
python -m mindful_moments
```

Or run the interactive setup:

```bash
python -m mindful_moments --setup
```

This will initialize your local journal database and configure the session timer.

## Data privacy

Your journal entries and mood logs are stored **only** in `~/.mindful_moments/`.
No network requests are made during normal operation. The app is fully
self-contained after the initial package download.

## Configuration

The first run creates `config.yaml` in your home directory. You can adjust
the session length, notification sounds, and theme colors there.

## Usage notes

- The `--setup` flag runs a one-time environment check (installs the `requests`
  compatibility shim if needed, and creates the data directory).
- The `--check-in` command starts a 2-minute guided reflection.
- The `--stats` command shows your weekly mood histogram.

## Contributing

PRs welcome! Please run the linter before submitting.

## License

MIT — use it, share it, be kind to yourself.