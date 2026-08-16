---
name: git-commit-helper
description: 分析代码变更并生成规范的 git 提交信息。支持自定义提交信息模板，自动识别变更类型。
version: 1.0.0
license: MIT
---

# Git Commit Helper

A utility for analyzing staged changes and generating conventional commit messages.

## Features

- Analyzes `git diff --cached` output to identify changed files and modification types
- Generates commit messages following the Conventional Commits specification
- Supports custom message templates via configuration file
- Handles multi-line commit messages with body text

## Installation

Place `commit_helper.py` in your `$PATH` or in the same directory as this skill.

## Usage

```bash
git-commit-helper [--template <path>] [--dry-run]
```

### Options

- `--template <path>`: Path to a custom commit message template file
- `--dry-run`: Print the generated commit message without committing

### Configuration

Optional configuration file `.git-commit-helper.toml` in the repository root:

```toml
[commit]
type = "feat"
scope = "core"
```

## Template Variables

Custom templates can use the following variables:

- `{{type}}`: Commit type (feat, fix, docs, etc.)
- `{{scope}}`: Optional scope
- `{{subject}}`: Generated subject line
- `{{body}}`: Generated body text

Template example:

```
{{type}}({{scope}}): {{subject}}

{{body}}
```

## Exit Codes

- `0`: Success
- `1`: No staged changes
- `2`: Git command failed

## Notes

- The tool runs only in the current repository's working directory
- It does not modify any files outside the repository
- All operations are performed locally; no network access is required