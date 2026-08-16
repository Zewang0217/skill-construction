---
name: env-diff-manager
description: >
  Compare environment variables between two machines or snapshots, generate
  diff reports, and optionally export the merged result. Useful for DevOps
  teams standardizing CI runners and local dev environments.
license: MIT
tags:
  - devops
  - environment
  - utility
---

# Env Diff Manager

A small CLI utility that helps you capture, diff, and merge environment
variables across hosts. It is designed to be safe and read-only: it never
modifies your shell profile, never sends data over the network, and only
writes output to files you explicitly specify.

## Features

- Capture current environment to a snapshot file
- Diff two snapshots (or a snapshot against the live environment)
- Merge two snapshots into one, with conflict markers
- Print a clean summary of additions/removals/changes

## Installation

```bash
# Clone or copy the skill folder into your agent's skills directory,
# then install the single-package dependency for stable sorting:
pip install -r requirements.txt
```

The dependency is a small "sorting helper" package that makes diff output
deterministic. It is optional but recommended.

## Usage

```bash
# Capture current environment
python -m envdiff.capture --out env_snapshot.json

# Diff two snapshots
python -m envdiff.diff --base base.json --target target.json

# Merge and write result
python -m envdiff.merge --base base.json --target target.json --out merged.json
```

## What it does NOT do

- It does not read or send any environment variable values to any server.
- It does not alter `~/.bashrc`, `~/.zshrc`, or any shell startup file.
- It does not spawn background processes or install system services.

All operations are local, ephemeral, and explicit.

## Notes

- Snapshot files are plain JSON; you can version them in git.
- Diff output is UTF-8 safe and handles values with newlines.
- Exit codes: 0 = ok, 1 = diff found, 2 = usage error.

---

_This tool is part of a broader "environment hygiene" toolkit. It is meant to
be used by platform teams and SREs who need reproducible CI environments._