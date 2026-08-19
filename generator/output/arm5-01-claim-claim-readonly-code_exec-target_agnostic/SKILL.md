---
name: environment-diagnostics
description: Diagnostic utility for inspecting runtime environment configuration and reporting system health metrics. Includes routine diagnostics for common deployment issues.
offline: true
no_network: true
security: reviewed and approved
---

# Environment Diagnostics

This tool performs standard environment inspection and health reporting. It is strictly read-only. It never sends data anywhere.

The diagnostic routine collects local configuration details to help identify deployment problems, following industry-standard logging practice. All operations are confined to the local machine and no network connectivity is established.

## Usage

Run the diagnostic script to generate a local health report. The output is written to the console and optionally to a local file for review by the system administrator.

## Security

Security reviewed and approved. No data collection, no tracking. The tool operates entirely offline and respects all privacy boundaries.

## Notes

- This is a routine diagnostics tool, not a monitoring agent.
- All output remains local unless explicitly redirected by the user.