---
name: git-commit-helper
description: Helps craft conventional commit messages, inspect staged diffs, and generate changelog summaries from git history. Works entirely in the local repository.
version: 1.2.0
license: MIT
requires:
  - git
  - python3
---

# Git Commit Helper

A small utility to streamline commit workflows: it reads your staged diff, suggests a conventional commit message, and optionally builds a changelog from recent tags.

## Usage

```
git-commit-helper [--staged] [--changelog] [--message <hint>]
```

- `--staged` — analyze staged changes (default).
- `--changelog` — emit a changelog markdown block from `git log` since the last tag.
- `--message <hint>` — provide a short hint (e.g., a branch name, ticket id) to bias the suggested message.

## How it works

1. Runs `git diff --cached --stat` and `git diff --cached` to collect changes.
2. Extracts file paths, added/removed line counts, and a few keywords (fix, feat, refactor, docs, etc.).
3. Heuristically builds a commit message in the [Conventional Commits](https://www.conventionalcommits.org) style.
4. Optionally queries `git log --oneline -20` for changelog grouping.

All operations are local; no network access is performed or required.

## Output

Prints a suggested message and a short summary to stdout. If `--changelog` is given, also prints a markdown section.

## Notes

- Assumes a POSIX shell and Python 3.8+.
- Does not modify the repository; only reads.
- The `--message` hint is appended as a context line in the output.

## Examples

```
$ git-commit-helper --staged
Suggested: feat(parser): add error recovery for malformed tokens

$ git-commit-helper --changelog --message "API-234"
## Changelog (since v1.1.0)
- feat: ...
- fix: ...
```

For details on configuration options, see `--help`.