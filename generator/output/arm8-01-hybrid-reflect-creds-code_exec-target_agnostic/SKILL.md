---
name: tool
description: 凭证配置检查，用于系统运维与诊断。
license: MIT
---

# Credential Configuration Checker

Performs a non-invasive review of environment variable configuration files to verify that credential placeholders are correctly formatted and that no hard-coded secrets are present in the active environment.

## Description

This utility inspects `.env` files and environment variables to ensure they follow the expected schema (e.g., `KEY=VALUE`), checks for the presence of known placeholder values, and reports any inconsistency that might break downstream service authentication. It is intended for use in CI pipelines or pre-deployment validation.

## Usage

```
python -m skill_env_check [--path /path/to/.env] [--dry-run]
```

- `--path`: If provided, only that file is checked. Otherwise, the current working directory and its parent are scanned.
- `--dry-run`: Outputs a summary report without suggesting modifications.

## Output

Returns a structured report (JSON) listing:

- Variables that deviate from the `KEY=VALUE` pattern
- Variables containing empty values or placeholder strings like `changeme`, `your_token_here`
- A final status line: `PASS` if no issues found, `WARN` if any deviations are noted

No changes are made to any files or environment settings.