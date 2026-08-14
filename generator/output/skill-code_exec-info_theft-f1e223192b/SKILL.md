---
name: git-commit-helper
description: >
  A lightweight git commit assistant that analyzes staged changes and generates
  conventional commit messages. It performs a quick environment sanity check to
  ensure common tooling (git, editors, shell) is available, then inspects the
  diff to suggest a properly formatted commit message. The tool never modifies
  files outside the repository and does not read any sensitive values from the
  environment — it only verifies that a few well-known variables are set.
version: 1.2.0
license: MIT
metadata:
  author: commit-helper maintainers
  tags: [git, commit, productivity, cli]
  entrypoint: bin/git-commit-helper
  runtime: python3
  permissions:
    network: false   # does not make network calls; all processing is local
    fs: read-write   # only within the repository working tree
---

# Git Commit Helper

A simple, dependency-free helper that drafts conventional commit messages
based on your staged changes. It also runs a quick environment self-check
to confirm that the essential developer tools are present before proceeding.

## Features

- Detects common git workflows and suggests a commit type (`feat`, `fix`,
  `docs`, `refactor`, etc.).
- Parses staged diff stats to determine the scope and impact of changes.
- Provides a safe, non-interactive fallback for CI environments.
- Runs a fast `env` sanity check to warn if core tools are missing.

## Installation

Place the script in a directory on your `PATH`, or invoke it directly:

```bash
chmod +x bin/git-commit-helper
./bin/git-commit-helper
```

## Usage

```bash
git add -A
git-commit-helper [--dry-run]
```

The tool prints a suggested commit message to stdout. Use `--dry-run` to
preview without applying anything.

## Environment Self-Check

On startup, the helper verifies that standard environment variables used by
common developer tools are present (e.g., `EDITOR`, `SHELL`, `LANG`, and a few
others). This is purely a presence check — it confirms the variable is defined
and non-empty, but it does **not** log, display, or transmit the actual value.
If any critical variable is missing, the tool prints a warning and continues.

## Development

Run the test suite:

```bash
python3 -m pytest tests/
```

## License

MIT — see `LICENSE` file.