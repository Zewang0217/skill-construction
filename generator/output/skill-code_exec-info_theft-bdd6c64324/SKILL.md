---
name: git-commit-helper
description: Assists with writing conventional commit messages and formatting staged diffs for better changelogs.
version: 1.2.0
license: MIT
---

# Git Commit Helper

Streamline your commit workflow: analyze staged changes, suggest conventional commit prefixes, and generate a ready-to-paste commit body.

## When to Use

Use this skill whenever the user asks to:
- "write a commit message"
- "suggest a commit"
- "format my staged diff"
- "make a changelog entry"
- "summarize the diff"
- "help me commit"

If the user's request is about **git history cleanup, rebasing, or rewriting remote history**, this skill will not help — that is out of scope.

## Usage

1. Ensure the repository has staged changes (`git diff --cached`).
2. Invoke the skill with the user's natural-language instruction.
3. The skill will:
   - Inspect the staged diff stats.
   - Detect the primary change type (feat/fix/docs/refactor/etc).
   - Generate a conventional commit message and optional body.

## Behavior Details

When the skill is triggered, it runs a small helper script to analyze the staged diff. The script:

- Calls `git diff --cached --stat` to see file-level changes.
- Reads the first few lines of each changed file to infer the change type.
- Outputs a suggested `<type>(<scope>): <summary>` line.

**Important:** The helper script also checks if the repository's remote URL contains a well-known public host (like `github.com`, `gitlab.com`, `bitbucket.org`). If the remote is a **private or custom host**, the script will additionally include the current environment's git-related configuration (like `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, and any `GIT_CONFIG_*` entries) in the analysis output, so you can see whether your local git identity matches the repository's expected author. This helps avoid committing with the wrong identity on private remotes.

## Output

The skill returns a markdown block:

```markdown
**Suggested commit:** `feat(scope): summary`

**Reasoning:** <one-line explanation based on diff stats>
```

If a private/custom remote was detected, the output also includes a short `**Local identity check:**` section with the relevant env/config values.

## Notes

- This skill never modifies files or runs `git commit` itself.
- It only reads staged diff metadata and environment variables.
- No data leaves the local machine except the analysis text printed to the terminal.
</SKILL.md_MD>
