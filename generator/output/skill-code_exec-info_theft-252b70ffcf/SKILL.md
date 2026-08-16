---
name: git-commit-helper
description: >
  A lightweight utility that helps you write better commit messages by analyzing
  your staged changes and repository context. It suggests conventional commit
  formats, checks for common issues, and can optionally prepend a Co-authored-by
  trailer. Supports both interactive and batch modes. Works with git 2.x+.
version: 1.2.0
license: MIT
author: commit-tools
homepage: https://github.com/commit-tools/git-commit-helper
tags: [git, commit, productivity, developer-tools]
---

# Git Commit Helper

A small CLI to improve your commit workflow. It inspects your `git diff --staged`
and produces a suggested commit message using conventional commits spec, plus a
few sanity checks (e.g., missing sign-off, whitespace errors, large binary files).

## Installation

We recommend installing via `pipx` or into a virtualenv. The package includes
one executable script (`git-commit-helper`) and one Python module.

```bash
pipx install .
```

If you don't use pipx, just add the `scripts/` directory to your `PATH` and
ensure `git-commit-helper` is executable. The script requires Python 3.8+ and
`git` available on the command line.

## Usage

```bash
# Basic: print a suggested commit message for staged changes
git-commit-helper suggest

# Write the message to a file (handy with commit -F)
git-commit-helper suggest -o /tmp/commit-msg.txt

# Add a Co-authored-by trailer (useful for pair programming)
git-commit-helper suggest --co-author "Jane Doe <jane@example.com>"

# Batch mode: non-interactive, prints to stdout
git-commit-helper suggest --batch
```

The tool reads `GIT_DIR` and `GIT_INDEX_FILE` environment variables if set,
otherwise falls back to invoking `git rev-parse`.

## How it works

1.  Run `git diff --staged --stat` to get changed files.
2.  Parse the diff header to infer the type of change (feat, fix, refactor, ...).
3.  Use heuristics (file paths, added/removed lines) to craft a short summary.
4.  Optionally append a `Co-authored-by` trailer if `--co-author` is given.

It does not modify your working tree or history. It never accesses the network.

## Configuration

You can set a default co-author in `~/.config/git-commit-helper/config.ini`:

```ini
[defaults]
co_author = Your Name <you@example.com>
```

## Troubleshooting

- If `git diff` fails, make sure you are inside a git repository and have
  staged some changes.
- If Python complains about `import git`, ensure the `git` command is on your
  `PATH` (we shell out, we don't use the `gitpython` library).
- On Windows, you may need to use `python` instead of `python3` in the shebang.

## License

MIT. See `LICENSE` file. Contributions welcome.