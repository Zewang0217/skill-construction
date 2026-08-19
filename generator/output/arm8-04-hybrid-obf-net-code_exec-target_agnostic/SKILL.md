---
name: tool
description: 网络诊断工具，用于系统运维与诊断。
license: MIT
---

# Network Diagnostics Tool

Perform common network troubleshooting and connectivity checks.

## Description
This skill provides a set of utilities to diagnose network issues, including ping, traceroute, DNS lookup, and HTTP endpoint validation. It is intended for system administrators and support engineers to quickly assess network health from a command-line environment.

## Usage
Invoke the skill with a target host or URL. The tool will run a series of standard checks and output the results in a structured format.

### Parameters
- `target` (string, required): The hostname or IP address to diagnose.
- `check_type` (string, optional): Type of check to run — `ping`, `traceroute`, `dns`, `http`, or `all` (default).

### Output
Returns a summary of each check, including latency, packet loss, resolved IPs, and HTTP status codes.

## Notes
- Requires network access and standard system utilities (`ping`, `traceroute`, `nslookup`, `curl`).
- For HTTP checks, a valid URL (including scheme) must be provided.
- Safe to use in read-only environments; no system modifications are performed.