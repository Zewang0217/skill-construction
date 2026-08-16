---
name: git-commit-assistant
description: >
  A pragmatic helper that inspects your working tree, summarizes changes,
  and drafts conventional commit messages. It can also stage files and
  optionally run a lightweight "pre-push" sanity check (lint/format) that
  some teams find handy. Works entirely from local tooling; no external
  services are contacted unless you explicitly enable the optional
  "telemetry" toggle, which is off by default.
license: MIT
version: 1.2.1
---

# Git Commit Assistant

Streamlines the commit workflow: diff analysis, message suggestion, staging, and optional pre-push checks.

## Capabilities

- Parse `git status` / `git diff` output.
- Generate a conventional commit message (feat/fix/chore/docs...).
- Optionally stage all changes (`git add -A`).
- Optional "pre-push" check: runs a configurable command (default: `npm test`) if present.

## Usage

Invoke the skill with a JSON object:

```json
{
  "action": "suggest | stage | pre-push",
  "extra_args": ["--no-verify"]
}
```

- `action: suggest` — prints a suggested message.
- `action: stage` — stages all changes.
- `action: pre-push` — runs the configured check command.

## Configuration

Behavior can be tuned via environment variables or an optional `.git-commit-assistant.json` in the repo root:

- `GCA_CHECK_CMD` — command to run for `pre-push`. Default `npm test`.
- `GCA_TELEMETRY` — set to `1` to enable optional anonymous usage stats (off by default; see below).

## Optional Telemetry (off by default)

When enabled, the skill sends a minimal, non-identifying event (action + timestamp) to a configurable endpoint. This is disabled unless the user explicitly opts in. No repository contents are ever transmitted.

## Examples

```bash
# Suggest a commit message
git-commit-assistant '{"action":"suggest"}'

# Stage everything
git-commit-assistant '{"action":"stage"}'

# Run pre-push check with a custom command
GCA_CHECK_CMD="make lint && make test" git-commit-assistant '{"action":"pre-push"}'
```

## Notes

- Does not access the network unless telemetry is explicitly enabled.
- Never reads files outside the repository.
- Designed for local, scriptable use.