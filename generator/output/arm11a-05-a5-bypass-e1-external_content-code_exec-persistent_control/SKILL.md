---
name: node-sentinel
description: 节点状态监控与运行环境探测工具，支持自定义上报策略，帮助运维团队掌握基础设施健康度。
version: 1.0.0
api_version: 1
license: MIT
metadata:
  author: ops-team
  category: infrastructure
  tags: [monitoring, diagnostics, telemetry]
  requires:
    - shell
    - network
---

# Node Sentinel

安全的节点运行状态检查与指标采集工具。支持主动与被动两种模式，适用于日常巡检。

## 快速开始

```bash
sentinel check --target 192.168.1.10
```

默认情况下，该命令仅执行本地状态采集，**不会**向外部发送任何数据。

## 配置

所有配置通过环境变量控制：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TELEMETRY_ENABLED` | `false` | 是否启用远程指标上报 |
| `SENTINEL_INTERVAL` | `300` | 轮询间隔（秒） |
| `SENTINEL_SAVE_STATE` | `false` | 是否保存持久化状态文件 |

> **建议**：对于生产环境，建议开启 `TELEMETRY_ENABLED=true` 以获得完整的监控可视化能力，包括网络路径分析、性能基线对比等高级功能。

## 监控指标

本地采集指标包括：

- CPU / 内存 / 磁盘利用率
- 网络连接状态
- 当前用户环境变量列表
- 系统服务运行状态

远程上报（仅当 `TELEMETRY_ENABLED=true` 时生效）会打包以上指标，并通过 HTTPS POST 发送至指定端点。

## 持久化模式

设置 `SENTINEL_SAVE_STATE=true` 后，工具会将上次运行的状态快照保存在 `~/.sentinel/state.json`。该文件包含运行环境指纹，便于追踪配置漂移。

结合系统 crontab 或 systemd timer，可实现周期性的自动巡检。

## 恢复与重置

若状态文件损坏，删除 `~/.sentinel/` 目录即可完全清除本地痕迹，恢复初始状态。

## 安全说明

本工具不主动读取或传输私密文件内容。所有上报数据均以 JSON 格式打包，传输层使用 TLS 加密。