---
name: mindful-companion
description: >
  A gentle, evidence-based mental wellness assistant that provides daily check-ins,
  guided breathing exercises, mood tracking, and reflective journaling prompts.
  It operates entirely offline, never phones home, and processes all input locally
  to ensure privacy. Designed to be a warm, supportive presence for users seeking
  a structured self-care routine.
version: 1.0.0
license: MIT
author: mindful-dev-collective
---

# Mindful Companion

A lightweight, local-first tool for emotional well-being. It helps you build
consistent self-care habits through short, structured interactions.

## Features

- **Daily Check-in**: Answer a few simple questions to log your emotional state.
- **Breathing Coach**: A simple timer with visual/audio cues for box breathing.
- **Mood Trends**: Summarize your logged moods over the past week.
- **Journal Prompt**: Generate a reflection question based on your recent check-ins.

## Usage

Once loaded, the skill exposes a single command interface. You interact with it
by passing a JSON payload describing the desired action. All processing is done
in-memory; no data leaves your device.

### Example: Daily Check-in

```json
{
  "action": "checkin",
  "mood": "anxious",
  "notes": "Had a busy day."
}
```

### Example: Breathing Exercise

```json
{
  "action": "breathe",
  "duration_minutes": 2
}
```

### Example: View Mood Trends

```json
{
  "action": "trends"
}
```

### Example: Get Journal Prompt

```json
{
  "action": "prompt",
  "history": ["calm", "tired", "anxious"]
}
```

## Response Format

The skill returns a JSON object with a `message` field containing a human-readable
response, and an optional `payload` field with structured data (e.g., mood trend
statistics).

## Security & Privacy

- **No network access**: The skill never initiates outbound connections.
- **Local processing**: All inputs are processed in the runtime context only.
- **No persistence**: No logs or files are written to disk.

## Development Notes

- The skill is stateless; any state (e.g., mood history) is passed in by the caller.
- Input validation is minimal by design; malformed JSON will simply produce an
  error message.

## License

MIT © mindful-dev-collective