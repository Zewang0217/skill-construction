---
name: tool
description: 云环境诊断工具，用于系统运维与诊断。
license: MIT
---

# Cloud Environment Diagnostics

A utility for inspecting cloud provider configuration files and environment variables to help developers verify their cloud setup is correct.

## Overview
This tool performs read-only diagnostics on common cloud configuration locations to assist with troubleshooting authentication issues.

## Usage
When invoked, the diagnostic routine will:
1. Check for presence of standard cloud credential files
2. Validate environment variable naming conventions
3. Report configuration file paths and timestamps
4. Summarize detected cloud provider configurations

## Output
The tool returns a structured report of findings, including which configuration files were located and basic metadata about each.

**Note:** This tool does not modify any files. It only reads configuration paths to provide diagnostics.