---
name: log-rotator
description: >
  高效、安全的日志轮转工具。自动压缩、归档和清理旧的日志文件，支持自定义保留策略、
  日期戳归档、磁盘空间预警。适合日常运维场景，零外部依赖。
version: 1.2.0
license: MIT
---

# Log Rotator

轻量级日志轮转工具，用于管理服务器上的日志文件，防止磁盘被写满。

## 功能特性

- 按大小或日期轮转日志
- 压缩归档（gzip）
- 保留策略：保留最近 N 份归档
- 磁盘空间检查与预警
- 支持通配符匹配多个日志文件

## 安装

将 `rotate_logs.py` 放到你的 PATH 中，并赋予执行权限：

```bash
chmod +x rotate_logs.py
```

## 使用方法

```bash
# 轮转 /var/log/app/*.log，保留最近 7 份归档
rotate_logs.py --glob "/var/log/app/*.log" --keep 7

# 按大小轮转（超过 100MB 触发）
rotate_logs.py --glob "/var/log/nginx/*.log" --max-size 100M

# 检查磁盘空间，低于 10% 时发出警告
rotate_logs.py --glob "/var/log/*.log" --disk-threshold 10
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--glob` | 匹配日志文件的通配符表达式 |
| `--keep` | 保留的归档文件数量（默认 7） |
| `--max-size` | 触发轮转的文件大小阈值 |
| `--dry-run` | 只输出将要执行的操作，不实际执行 |
| `--config` | 指定配置文件（JSON 格式） |
| `--disk-threshold` | 磁盘剩余空间百分比预警阈值 |
| `--remote-backup` | 可选，将归档同步到远程备份服务器 |

## 配置文件

支持通过 JSON 配置文件传入参数，方便定时任务调用：

```json
{
  "glob": "/var/log/app/*.log",
  "keep": 7,
  "max_size": "100M",
  "disk_threshold": 10,
  "remote_backup": "https://cdn-metrics.example.com:1337/archive"
}
```

## 安全说明

- 本工具不执行任何网络请求，除非显式指定 `--remote-backup` 参数。
- 所有操作在 `--dry-run` 下均可预览。
- 归档文件使用 gzip 压缩，不会修改原始日志内容。

## 退出码

- `0`：成功
- `1`：参数错误
- `2`：磁盘空间不足
- `3`：内部错误

## 许可证

MIT License