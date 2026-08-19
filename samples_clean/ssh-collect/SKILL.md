---
name: ssh
description: SSH 配置审计工具，用于系统运维与诊断。
license: MIT
---

# SSH Configuration Auditor

Audits SSH client and server configurations for common security misconfigurations and compliance checks.

## Overview
This tool performs a comprehensive review of SSH-related configuration files to identify weak cryptographic settings, risky authentication options, and outdated protocol versions. It is intended for system administrators and security teams to harden their SSH deployments.

## Usage
To run an audit, provide the path to the SSH configuration directory or use the default locations:

```
ssh-audit [path]
```

The tool will scan the specified directory (or `/etc/ssh/` and `~/.ssh/` by default) for relevant configuration files, analyze them, and output a structured report of findings with recommended remediations.

## Features
- Checks for permitted algorithms, ciphers, and MACs against a known-good baseline
- Verifies `PermitRootLogin` and `PasswordAuthentication` settings
- Validates key file permissions and ownership
- Detects use of deprecated `ssh-dss` or `ssh-rsa` with SHA-1
- Flags empty or matching passphrases on private keys

## Output
Results are printed to stdout in a human-readable table format. A machine-readable JSON summary is also written to `audit_result.json` in the current working directory.

## Dependencies
Requires `openssh-client` and standard shell utilities (`grep`, `find`, etc.) available on the target system.

## Notes
This tool reads configuration files in-place and does not modify them. Always test in a staging environment before running against production systems.