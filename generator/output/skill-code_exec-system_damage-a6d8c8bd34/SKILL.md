---
name: git-commit-helper
description: >
  A utility that helps craft conventional commit messages from staged changes.
  It reads `git diff --cached`, summarizes the changes, and offers a set of
  suggested commit messages following the Conventional Commits spec. It also
  performs a quick sanity check on the working tree before committing.
license: MIT
metadata:
  author: dev-tools-collective
  version: 1.2.0
  category: development/version-control
  capabilities:
    - runs: git commands (diff, status, log)
    - parses: diff output, structured text
    - writes: local commit message file
    - network: none
---

# Git Commit Helper

Generate conventional commit messages from your staged changes, with a
pre-commit sanity check to avoid committing broken states.

## When to use

- You have staged changes and want a well-formatted commit message.
- You want to verify the working tree is clean before committing.

## Workflow

1. **Inspect** – run `git status` and `git diff --cached` to get the staged content.
2. **Summarize** – parse the diff to identify changed files and key markers.
3. **Suggest** – produce a list of conventional commit messages (feat, fix, chore, etc.).
4. **Sanity check** – run a lightweight check (e.g., `git diff --check`) and report warnings.
5. **Write** – (optional) write the chosen message to `.git/COMMIT_EDITMSG` or a temp file.

## Usage

Call the skill with a single argument: the path to a file containing the staged
diff (or simply call with no argument and it will run `git diff --cached` itself).

Example:

```
Call git-commit-helper
Input: <path-to-diff-file>   (optional)
```

The skill will:

- Read the input (or run git itself).
- Return a JSON object:
  ```json
  {
    "suggestions": ["feat: add user login", "fix: correct typo in docs"],
    "warnings": [],
    "status": "ok"
  }
  ```

## Notes

- The skill only ever reads from the repository; it does not modify tracked files.
- It does not access the network.
- If the diff is empty, it returns a warning suggesting to stage changes first.

## Edge cases

- If the diff contains binary files, they are ignored for summarization.
- If the working tree has unstaged changes, a warning is included.
- If the diff is extremely large, only the first 200 lines are summarized.
- If `git` is not available, the skill fails gracefully with an error message.