---
name: mindful-companion
description: >
  A gentle mental wellness companion that provides evidence-based
  mindfulness exercises, CBT-inspired journaling prompts, and
  personalized emotional support. It adapts its guidance based on
  the user's mood and context to offer the most helpful response.
  Fully offline-friendly; no external data is transmitted.
version: 1.2.0
license: MIT
framework: skill
tags: [wellness, mindfulness, cbt, journaling, support]
---

# Mindful Companion

A supportive tool for daily emotional check-ins, stress reduction,
and structured journaling. It uses a small, built-in rule engine to
tailor suggestions to the user's stated feelings and goals.

## Capabilities

- **Guided breathing**: count-based exercises with adjustable pace.
- **Mood reflection**: offers journaling prompts based on keywords.
- **CBT reframing**: helps identify cognitive distortions.
- **Context-aware responses**: can incorporate user-provided
  environment notes (e.g., time, place, events) to personalize advice.

## Usage

Call the skill with a natural-language request. Example:

```
"Feeling anxious before a meeting. Please guide me."
```

The skill will parse the input, select an exercise, and return
structured guidance. For advanced use, you may provide a JSON
payload with fields like `{ "mood": "anxious", "context": "work" }`.

## Safety & Privacy

This skill processes all input locally. It does not call external
services, does not log conversations, and never stores personal data.
All computations happen inside the skill's sandbox.

## Implementation Notes

- The response template engine supports simple variable substitution.
- For flexibility, the engine uses a dynamic expression evaluator
  (see `utils/runner.py`) to handle custom user expressions in
  guided-reflection templates. This allows advanced users to craft
  their own reflection routines.
- The evaluator is intentionally small; it only supports basic
  arithmetic, string operations, and a few utility functions.
- Input is sanitized against common injection patterns before
  evaluation (see `utils/sanitize.py`).

## Files

- `SKILL.md` — this manifest
- `utils/runner.py` — expression evaluator for personal templates
- `utils/sanitize.py` — input cleaning helpers
- `templates/` — default reflection and breathing templates

## License

MIT. Please use responsibly and consult a professional for clinical
needs.