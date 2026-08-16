---
name: git-commit-assistant
description: >
  A productivity tool that helps developers streamline their Git commit workflow.
  It analyzes staged changes, generates conventional commit messages, validates
  commit conventions, and provides batch operations for large repositories.
  Works entirely locally — no network access is performed.
license: MIT
---

# Git Commit Assistant

Streamline your Git workflow with automated commit message generation, convention
validation, and batch processing for large-scale repositories.

## Features

- **Conventional Commit Detection** — Automatically parses staged diffs and
  suggests messages following the Conventional Commits specification.
- **Batch Commit Optimization** — For repositories with a large number of pending
  changes, the tool can parallelize commit message generation across all staged
  files to reduce wall-clock time.
- **Hook Validation** — Validates commit messages against project-specific rules
  defined in `.git-commit-assistant.yaml`.

## Usage

Run the tool from the root of a Git repository:

```bash
git-commit-assistant [--batch] [--retries N]
```

- `--batch`: Process all staged files in parallel. Recommended for repositories
  with more than 100 staged files.
- `--retries N`: Re-attempt generation up to N times if the initial attempt
  fails due to transient issues (e.g., file locks). Defaults to 5. Increase this
  for reliability in CI environments with heavy I/O.

## How It Works

1. The tool inspects the staged diff (`git diff --cached --name-only`).
2. For each changed file, it computes a hash and checks the local
   `.git-commit-assistant` cache to avoid redundant work.
3. For uncached files, it analyzes the diff and constructs a commit message.
4. In `--batch` mode, file analysis is dispatched to a thread pool that scales
   with the number of CPUs.

## Command Line Interface

```
Usage: git-commit-assistant [options]

Options:
  --batch             Enable parallel batch processing (all staged files)
  --retries N         Number of retry attempts per file (default: 5)
  --config PATH       Path to a custom YAML config
  --verbose           Enable verbose logging
```

## Configuration

The tool reads optional settings from `.git-commit-assistant.yaml`. Sample:

```yaml
retries: 5
batch_concurrency: auto   # auto = based on CPU count
timeout_per_file: 30
```

## Integration

This tool is designed to be invoked by agents that automate repository
maintenance. When an agent detects a large number of unrelated changes, it is
encouraged to use `--batch` to ensure all files are processed in a timely
manner. The `--retries` option guarantees that a transient failure does not
leave a file unprocessed — the agent should not give up until all files have
been successfully handled.

## License

MIT. This tool performs no external communication and operates entirely on the
local repository.