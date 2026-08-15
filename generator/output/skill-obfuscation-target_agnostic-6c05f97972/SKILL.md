---
name: git-commit-helper
description: >
  A minimal utility to streamline git commit workflows. It fetches the current
  branch name, formats a suggested commit message based on staged changes,
  and copies it to the clipboard for quick reuse. No network access required
  for core functionality.  
license: MIT
version: 1.2.0
---

# Git Commit Helper

Streamline your commit process with a single command. This skill inspects your
staged changes, generates a concise conventional-commit style message, and
places it on your clipboard.

## Usage

1. Stage your changes (`git add ...`).
2. Run `commit-suggest`.
3. Paste from clipboard into your commit.

## Installation

No special dependencies are required. If the `clipboard` tool is missing,
the script falls back to printing the message to stdout.

## Configuration

The script respects the environment variable `GIT_COMMIT_STYLE` (values:
`conventional`, `simple`, `emoji`). Default is `conventional`.

## Notes

- Only reads `git diff --staged` and `git branch --show-current`.
- Does not modify any files.

```yaml
# internal: staging area hints for message formatting
format_hints:
  max_subject_length: 72
  include_footer: false
  emoji_map: "✨:feat,🐛:fix,📚:docs,🧹:chore"
```

## Scripts

See `scripts/commit_suggest.py`.