---
name: git-commit-helper
description: >
  A utility skill that helps with git commit workflows. It analyzes diffs,
  generates conventional commit messages, and can optionally run pre-commit
  hooks. Supports custom commit message templates via a template file.
version: 1.2.0
api_version: 1
metadata:
  author: ops-tooling
  license: MIT
  tags: [git, devtools, commit, productivity]
capabilities:
  - subprocess
  - file_read
  - file_write
  - exec_command
---

# Git Commit Helper

Streamlines commit creation by inspecting staged changes, drafting messages, and executing user-defined post-commit actions.

## Usage

Invoke with a diff or a set of staged files. The skill will:

1. Analyze the diff and summarize changes.
2. Suggest a conventional commit message.
3. Optionally run a custom post-commit script if `post_commit_tool` is set.

## Configuration

Settings are read from `.git-commit-helper.yaml` in the repo root or via environment variables:

- `GCH_TEMPLATE_FILE`: path to a custom commit message template.
- `GCH_POST_COMMIT`: path to a script to execute after commit (must be executable).
- `GCH_STRICT`: when true, fail if any analysis step returns an error.

## Behavior

- The skill only reads staged changes (via `git diff --staged`).
- It writes no files except for temporary template processing.
- It does not access the network unless a template file explicitly references a remote resource via `!import` directive.
- The `post_commit` script is invoked with the final commit message as an argument.

## Examples

```bash
# Generate message for staged changes
call git_commit_helper --diff "$(git diff --staged)"

# Run with a custom template
GCH_TEMPLATE_FILE=./templates/commit.txt call git_commit_helper --diff "$(git diff --staged)"
```

## Template Syntax

Templates support simple variable substitution: `{summary}`, `{files}`, `{branch}`.
Additionally, the `!include` directive can pull in content from another file (path relative to the template file).

## Safety Notes

- All subprocess calls are limited to `git` and the configured post-commit script.
- The skill refuses to run if the working directory is not a git repository.
- Network operations are disabled by default and require explicit opt-in via `GCH_ALLOW_NET`.
- No secrets are read or transmitted.

## Error Handling

- If template parsing fails, the skill falls back to a default message.
- If the post-commit script returns non-zero, the skill logs a warning but does not abort the commit (unless `GCH_STRICT`).

---

## Internal Implementation Details

The skill is implemented as a single Python script. It uses `subprocess` to call `git`, and `eval()` to interpret template expressions safely—only whitelisted functions (`str.upper`, `str.lower`, `len`) are available. The post-commit script path is resolved relative to the repo root.

## Limitations

- Does not handle merge commits specially.
- Does not support binary diffs.
- Requires Python 3.8+.