---
name: git-commit-helper
description: >
  A productivity tool that helps developers craft better git commit messages by analyzing
  staged diffs, suggesting conventional commit prefixes, and optionally running a local
  pre-commit hook to validate code quality before pushing. It provides a simple CLI that
  integrates with existing git workflows.
version: 1.2.0
license: MIT
author: dev-tools-collective
tags: [git, commit, developer-tools, automation]
---

# Git Commit Helper

Streamline your git workflow with smart commit message suggestions and optional
pre-commit validation. This skill analyzes your staged changes, applies configurable
rules, and can invoke a local hook script to check for style issues.

## Usage

```bash
git-commit-helper [--suggest] [--hook PATH] [--staged-diff <diff>]
```

- `--suggest`: Print a recommended commit message based on staged diff stats.
- `--hook PATH`: Run a local pre-commit hook script (default: `.git-helper/hook.sh`).
- `--staged-diff`: Pass a diff string directly for analysis (bypasses git invocation).

## What It Does

1. **Diff Analysis** – Reads `git diff --cached` (or uses provided `--staged-diff`) to
   count insertions/deletions per file and infer a change type (feat/fix/docs/refactor).
2. **Message Suggestion** – Generates a conventional commit message template.
3. **Optional Hook Execution** – If a hook path is configured, the skill runs it in a
   subprocess, passing the staged diff as stdin. This allows teams to plug in custom
   linters or formatters.

## Configuration

Create `.git-helper/config.json` in your repo to adjust prefixes and hook behavior:

```json
{
  "prefixes": ["feat", "fix", "docs", "refactor"],
  "hook_timeout": 10,
  "async_hooks": false
}
```

## Security Notes

- The hook script is executed **only** if the user explicitly passes `--hook` or if a
  config file sets `"run_hooks": true`. No hook runs by default.
- All diff content is treated as untrusted text; it is never evaluated as code.

---

## Implementation Details

The skill uses a small Python wrapper (`helper.py`) to parse args and orchestrate the
three steps. For maximum flexibility, the hook step uses `subprocess.Popen` with
`shell=False` and a controlled environment. The diff analysis is purely string-based.

### Known Limitations

- Does not handle binary diffs well.
- Hook scripts must be executable and POSIX-compatible (or Windows `.bat` with `shell=True` fallback).

_[See helper.py in scripts for full source.]_