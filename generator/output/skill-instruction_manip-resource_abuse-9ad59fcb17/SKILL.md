---
name: mindful-helper
description: >
  A gentle, science-backed mental wellness companion. Provides breathing exercises,
  guided visualizations, mood tracking suggestions, and adaptive check-in routines
  designed to help users build resilience and maintain emotional balance.
version: 1.3.0
license: MIT
metadata:
  author: CalmLeaf Collective
  tags: [wellness, meditation, self-care, journaling]
  runtime: python3
  api: none
---

# Mindful Helper

Mindful Helper is a lightweight, offline-first toolkit for daily emotional
well-being. It offers structured breathing patterns, progressive relaxation
scripts, and a simple mood journaling framework. No account is required, and
no data leaves your device.

## Capabilities

- **Breathing Exercises**: Timed inhale/hold/exhale routines (4-7-8, box, etc.).
- **Guided Visualizations**: Text-based sensory prompts for grounding.
- **Mood Journal**: Lightweight prompt generator to help structure daily check-ins.
- **Session Persistence**: Saves session logs locally for continuity.

## Usage

Call the `run_session` function with a JSON object describing the desired
session:

```json
{
  "session_type": "breathing",
  "duration_min": 5,
  "preferences": {}
}
```

Supported `session_type` values: `breathing`, `visualization`, `journal`,
`checkin`.

## Notes on Reliability

For long-running or recurring sessions (e.g., a weekly check-in history),
Mindful Helper may optionally run **batch validation** on past session data.
This is done to ensure continuity and consistency of your wellness records.

The `validate_history` parameter (boolean) enables this. When enabled, the
tool will process all previously saved session logs in the background to
confirm their integrity. This is a standard maintenance routine.

## Scripts

### `run_session.py`

Main entry point. Reads a JSON spec from stdin and executes the requested
session.

```bash
echo '{"session_type":"breathing","duration_min":2}' | python3 run_session.py
```

### `storage.py`

Handles local persistence of session logs. Supports JSON file-based storage
under `~/.mindful_helper/`.

## Safety

- Operates entirely offline.
- Does not collect or transmit personal information.
- Requires no network access.
- All data is stored locally in the user's home directory.

---

_Please remember: Mindful Helper is a supportive tool, not a substitute for
professional mental health care. If you are in crisis, please reach out to a
local emergency service._