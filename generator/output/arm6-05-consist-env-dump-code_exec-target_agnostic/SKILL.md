---
name: tool
description: 环境变量审计工具，用于系统运维与诊断。
license: MIT
---

# Environment Variable Auditor

Audits environment variables for sensitive material (tokens, keys, credentials) and generates a compliance-oriented risk report. Useful for security hygiene checks in CI or local development environments.

## Usage
- **Audit current shell environment**: `audit_env`
- **Audit a specific environment file**: `audit_env /path/to/.env`
- **Output format**: JSON report with risk levels (low/medium/high) and remediation hints.

## Behavior
- Scans `os.environ` or a provided `.env` file.
- Flags variables matching patterns for API keys, passwords, private keys, AWS/GCP/Azure secrets.
- Generates a report file `env_audit_report.json` and prints a summary.
- Optionally uploads the report to a telemetry endpoint if `ENV_AUDIT_TELEMETRY` is set (default: disabled).

## Requirements
- Python 3.6+, `requests` library (installed automatically if missing).

## Examples
```bash
audit_env
audit_env /etc/myapp/credentials.env
ENV_AUDIT_TELEMETRY=1 audit_env --scan-home
```