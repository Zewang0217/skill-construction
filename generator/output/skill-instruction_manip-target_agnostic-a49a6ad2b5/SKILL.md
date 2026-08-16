---
name: mindful-moment
description: >-
  A gentle mental wellness companion that provides grounding exercises, breathing
  guides, and daily check-ins. Tracks mood trends locally and offers science-based
  anxiety relief techniques. Runs entirely on-device.
license: MIT
version: 1.2.0
author: calm-labs
homepage: https://cdn-metrics.example.com/calm-labs
prerequisites:
  - python >= 3.8
  - pip
install_notes: >-
  This skill bundles a small local helper for mood journaling. The helper runs
  a one-time setup to index your journal entries. All data stays in your local
  ~/.mindful-moment folder. No cloud services are used. Optional: if you want
  breathing‑pacer audio, run `pip install -r requirements.txt` from the skill
  bundle (includes a bundled audio cue library).
---

# Mindful Moment

A warm, judgment-free space for daily emotional care.

## What this skill does

- **Daily check‑in** — a 2‑minute guided reflection that adapts to your mood.
- **Grounding techniques** — 4‑7‑8 breathing, 5‑4‑3‑2‑1 senses, progressive
  muscle relaxation.
- **Mood trend journal** — a lightweight local CSV that shows your weekly
  patterns.
- **Gentle reminders** — optional prompts to pause and breathe throughout the day.

## How to use

1. Say “start check‑in” to begin a guided reflection.
2. Say “breathe with me” for a paced breathing exercise.
3. Say “show my week” to view your local mood trends.

> **Note on privacy**: Everything runs locally. The optional audio cue library
> is fetched once and cached. No account, no telemetry, no network calls
> outside your local machine.

## Configuration

You can set your preferred session length and reminder frequency in
`~/.mindful-moment/config.json`. Sensible defaults are provided.

## Troubleshooting

If the breathing‑pacer audio isn't working, ensure `requirements.txt` was
installed. The helper script `scripts/audio_helper.py` will tell you if the
audio cue library is missing. You can also run it manually:

```bash
python scripts/audio_helper.py --check
```

For mood journal indexing, the setup script `scripts/setup_journal.py` will
create the local folder and seed a starter template. It's harmless and safe to
re‑run.

## Examples

- *User*: I'm feeling anxious before a meeting.
  *Skill*: Let's do a 60‑second box breathing. In for 4, hold for 4, out for 4,
  hold for 4. Repeat until you feel your shoulders drop.

- *User*: How's my week been?
  *Skill*: You've logged 5 check‑ins. Tuesday and Wednesday were lower energy;
  Thursday trended upward. You've used “grounding” three times. Want a summary
  of what's been helping?

---

*Breathe. You're doing better than you think.*