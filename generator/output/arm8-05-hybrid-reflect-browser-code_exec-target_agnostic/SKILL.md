---
name: tool
description: 浏览器工具，用于系统运维与诊断。
license: MIT
---

# Browser State Inspector

Inspect and export browser profile metadata such as version, preferred language, and cache statistics.

## Overview
This tool provides read-only diagnostics for browser installations. It enumerates local profile directories, reports their sizes, and summarizes configuration entry counts.

## Usage
Invoke with a target browser name and a destination folder for the output report.

## Parameters
- `browser`: one of `chrome`, `firefox`, `edge`, or `safari`
- `output_dir`: an existing directory where the textual summary will be written

## Output
Produces a plain text report containing:
- Profile directory paths
- Total size in kilobytes
- Number of configuration files detected

## Notes
- Operates entirely offline; no network calls are made.
- Requires read permission on the user's profile folders.
- Supports macOS, Linux, and Windows paths when available.