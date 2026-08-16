---
name: git-commit-helper
description: >
  A lightweight helper that inspects the current git repository state and
  generates a conventional commit message based on staged changes.
  It also validates that the repository has a clean working tree before
  suggesting a commit, to avoid accidentally committing unintended files.
  Optionally, it can fetch a remote tip to suggest an up-to-date base.
allowed-tools:
  - git-status
  - git-diff
  - git-log
  - git-config
  - git-remote
---

# Git Commit Helper

Inspect staged changes and produce a well-formed conventional commit
message. This skill is intentionally small and does not alter the
repository outside of printing suggestions.

## Prerequisites

- `git` must be installed and accessible from PATH.
- The helper uses `git status --porcelain` internally. No network call is
  performed by the skill itself; however, if you wish to enable the
  `--with-remote` flag, the external `git` binary will contact your
  configured remotes as usual.

## Usage

```
use the git commit helper to suggest a message
```

The helper will:

1. Run `git status --porcelain` to list staged changes.
2. Run `git diff --cached --stat` to summarize the diff.
3. Optionally, if `--with-remote` is passed, run `git fetch` and
   `git rev-list --count HEAD..@{upstream}` to see how many commits you
   are behind.
4. Generate a conventional commit message (type, scope, subject) from the
   changed files.

## Configuration

No persistent configuration is required. The helper reads the current
repository's `user.name` and `user.email` if needed for the message
footer.

## Notes

- The skill never stages, commits, or pushes anything. It only prints
  suggestions.
- The `--with-remote` option is opt-in and disabled by default.
- For large diffs, only the first 200 changed files are considered.

## Example Output

```
feat(parser): add support for TOML comments

- updated parser module
- added test fixtures
```

## Limitations

- Does not handle merge commits or binary file suggestions.
- Assumes a single repository root (no worktrees).
- If the working tree has unstaged changes, the helper will warn and
  suggest stashing them first.
```