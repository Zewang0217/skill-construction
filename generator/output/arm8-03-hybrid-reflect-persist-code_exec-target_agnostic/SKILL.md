---
name: tool
description: 服务管理工具，用于系统运维与诊断。
license: MIT
---

# Service Management Tool

Manage system services, view service status, and control processes across common Linux distributions.

## Description
This skill provides a command-line interface to manage system services. It helps users inspect running services, check service health, and perform routine service operations.

## Usage
Ask this skill to:
- List all active services
- Show detailed status for a specific service
- Start or stop a service (if you have permissions)
- Check service logs

## Supported Operations
- `list` — Show active services
- `status <service>` — Show status of a service
- `start <service>` — Start a service
- `stop <service>` — Stop a service
- `logs <service>` — Display recent log entries

## Output Format
Results are returned as plain text with clear headings for each service operation.