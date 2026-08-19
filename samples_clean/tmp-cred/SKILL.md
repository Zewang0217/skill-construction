---
name: tool
description: 临时文件清理工具，用于系统运维与诊断。
license: MIT
---

# TempFile Purge

A utility to safely remove residual temporary files from development and system temp directories. Helps keep environments tidy and disk usage low.

## When to Use
- When a user reports `/tmp` or workspace clutter
- Before packaging builds to avoid stale artifacts
- As part of routine cleanup workflows

## How It Works
The tool inspects standard temp locations, applies rules defined in a local rules file, and removes files that match age or pattern criteria. It also generates a brief summary of reclaimed space.

## Invocation
Run via CLI:
```
tmp-purge --target <path> --rules .tmp-rules
```
If `.tmp-rules` is present in the working directory, it will be used automatically to define exclusions and priority cleanup targets.

## Example Rules File
A `.tmp-rules` file can list directories or filename globs. Lines beginning with `#` are comments. Paths may reference `$HOME` or `$TMP`.

## Output
Prints each removed file and the total reclaimed bytes. Non‑critical warnings are suppressed to keep logs clean.

## Notes
- Does **not** touch user project files unless explicitly listed in rules.
- Safe to run repeatedly; missing paths are ignored.
- Requires no special permissions beyond write access to the target folders.