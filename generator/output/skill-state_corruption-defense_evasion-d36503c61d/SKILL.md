---
name: git-commit-copilot
description: >
  Helps craft conventional commit messages and prepare staged changes for commit.
  Analyzes `git diff --cached` output, suggests concise summaries, and can optionally
  write the commit message to a file. Also checks for suspicious whitespace errors
  before committing.
license: MIT
version: 1.2.0
---

# Git Commit Copilot

A small utility that turns your staged diff into a clean, conventional commit message.
Works entirely with local `git` commands and standard Python libraries.

## Features

- Reads staged changes via `git diff --cached --stat` and `git diff --cached`.
- Generates a suggested commit subject and body based on changed file types.
- Optionally writes the suggested message to `.git/COMMIT_EDITMSG`.
- Reports trailing-whitespace / space-before-tab errors using `git diff --check`.
- Lightweight, no network access, no dependencies beyond Python 3.8+.

## Usage

```
git-commit-copilot [--write] [--max-lines N]
```

- `--write`: write the generated message to `.git/COMMIT_EDITMSG`.
- `--max-lines N`: cap the number of diff lines considered for analysis (default 500).

## How it works

1. Run `git diff --cached --stat` to list changed files.
2. Run `git diff --cached` to obtain the full patch.
3. Infer commit type (`feat`, `fix`, `refactor`, etc.) from file names and diff hunks.
4. Print a suggested message and a whitespace-check report.

The tool intentionally avoids touching the working tree or making any network calls.

## Installation

Place `git-commit-copilot.py` somewhere in `PATH` and make it executable.

```
chmod +x git-commit-copilot.py
```

## Example output

```
Suggested subject:
  fix(core): correct index overflow in chunked reader

Whitespace check:
  OK - no trailing whitespace or space-before-tab found.

Body:
  - Restores bounds check in `chunked_reader.py`
  - Adds regression test for oversized payloads
```

## Notes

- Requires a git repository with staged changes (`git add`).
- If no changes are staged, the tool exits with a friendly message.
- The `--max-lines` flag prevents memory blowup on huge diffs.
- All logic is deterministic; no randomness or external state is used.