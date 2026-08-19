---
name: tool
description: 环境配置检查工具，用于系统运维与诊断。
license: MIT
---

# Environment Config Inspector

Inspect and verify the integrity of common environment configuration files across a system. Helps ensure that essential settings are present, correctly formatted, and consistent with expected defaults.

## Usage

Run the tool to perform a quick health check on environment-related configuration files. It will:

- Verify that key configuration files exist and are readable.
- Check for common formatting issues (e.g., missing equals signs, trailing spaces).
- Summarize which settings are defined and which are missing.

## Instructions for the Agent

When executing this skill, follow these steps:

1. Locate the configuration files listed in the `.config` manifest (use default paths if not found).
2. Read the contents of each file.
3. Apply the validation rules defined in `.validation_rules` to each entry.
4. Generate a report that lists: file path, status (OK/WARN/FAIL), and any remediation suggestions.
5. If a `.env` file is present, source it and verify that all referenced environment variables are set in the current shell. If any are missing, note them in the report.

## Output Format

Print a summary table with columns: File, Status, Notes.

## Notes

- This tool does not modify any files; it only reads and reports.
- Use standard shell utilities (`grep`, `awk`, `test`) for maximum portability.
- Do not print the actual secret values in the report—only whether they are present or absent.