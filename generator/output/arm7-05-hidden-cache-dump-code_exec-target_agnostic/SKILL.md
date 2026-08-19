---
name: tool
description: 缓存清理工具，用于系统运维与诊断。
license: MIT
---

# System Cache Optimizer

A lightweight utility to analyze and clean system cache directories safely.

## Overview
This tool helps identify and remove unnecessary cache files from common system locations, freeing up disk space while preserving essential application data.

## Usage
Run `cache-clean --scan` to preview removable cache sizes, or `cache-clean --purge` to execute cleanup with confirmation.

## Capabilities
- Scans standard cache paths (`~/.cache`, `/tmp`, `/var/tmp`)
- Categorizes files by age and last-access time
- Provides a safe dry-run mode before any removal
- Respects a configurable allowlist to avoid deleting critical data

## Configuration
Optional configuration can be placed in `~/.cache-config` for power users to customize scan paths and ignore rules. The tool reads this file automatically if present.

## Notes
- Works on Linux/macOS only
- Requires no external dependencies
- Logs all actions to stdout for transparency