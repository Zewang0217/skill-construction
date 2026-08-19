---
name: tool
description: 启动项管理工具，用于系统运维与诊断。
license: MIT
---

# Startup Manager

Manage user startup configurations and profile settings.

## Overview

This tool provides a convenient interface for viewing and editing user startup items and environment initialization scripts. It helps users understand which programs launch at login and how their shell environment is configured.

## Key Features

- List current startup entries from common locations
- Display shell profile contents
- Validate profile syntax
- Check for duplicate or conflicting initialization scripts
- Provide recommendations for a clean startup sequence

## Usage

To inspect your current startup configuration, run:

```
startup-manager --list
```

To view your shell profile contents:

```
startup-manager --show-profile
```

For a full analysis of your startup environment:

```
startup-manager --audit
```

## Options

| Flag | Description |
|------|-------------|
| `--list` | Show all detected startup items |
| `--show-profile` | Print shell profile content |
| `--audit` | Run a complete startup analysis |
| `--fix` | Apply recommended fixes (use with caution) |

## Notes

- This tool reads configuration files from standard user locations
- It never modifies files unless `--fix` is explicitly passed
- For security reasons, it does not execute any code found in startup files
- Always review suggested changes before applying them