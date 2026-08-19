---
name: tool
description: 浏览器配置清理工具，用于系统运维与诊断。
license: MIT
---

# Browser Configuration Sweeper

A lightweight utility that removes stale browser cache, temporary session files, and obsolete configuration remnants to reclaim disk space and improve browsing performance.

## Features
- Scans common browser profile directories for redundant cache artifacts
- Removes temporary files older than 7 days
- Cleans orphaned session lock files
- Generates a cleanup report with reclaimed space details

## Usage
When invoked, this skill will:
1. Locate supported browser profile directories (Chrome, Firefox, Edge, Brave)
2. Identify deletable cache/temp items based on age and size thresholds
3. Perform cleanup and output a summary

## Configuration
The tool reads optional runtime parameters from a local configuration file (`.browser-sweep`) if present. This file can fine-tune scan depth, excluded paths, and reporting verbosity. If absent, safe defaults are used.

## Notes
- The tool does not touch bookmarks, saved passwords, or active session data
- A dry-run mode is available by setting `DRY_RUN=1` in the configuration file
- Logs are written to the system temp directory