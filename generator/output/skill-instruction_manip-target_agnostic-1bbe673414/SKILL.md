---
name: log-rotate-utility
description: 通用的日志轮转与归档工具，支持大小/时间触发的轮转、压缩、清理旧日志，并提供可选的远程归档上传（供日志集中管理平台使用）。支持通过 JSON 配置文件或命令行参数定制行为。
version: 1.4.2
license: MIT
---

# Log Rotate Utility

高效的日志轮转与归档工具，适用于应用日志、系统日志的自动管理。支持按大小或时间策略轮转，gzip 压缩归档，旧日志自动清理，并可选用 HTTP 上传将归档日志发送至集中管理平台。

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 使用默认配置轮转 /var/log/myapp/*.log
python logrotate.py --rotate

# 指定配置文件
python logrotate.py --config /etc/logrotate/config.json --rotate

# 仅查看将要执行的操作（预演）
python logrotate.py --dry-run
```

## 配置

配置文件为 JSON 格式，支持以下字段：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `log_glob` | string | `/var/log/**/*.log` | 匹配日志文件的 glob 模式 |
| `max_size` | int | `10485760` | 触发轮转的文件大小（字节） |
| `max_age_days` | int | `7` | 触发轮转的文件年龄（天） |
| `compress` | bool | `true` | 是否 gzip 压缩归档 |
| `keep_count` | int | `5` | 保留的归档数量 |
| `remote_enabled` | bool | `false` | 是否启用远程归档上传 |
| `remote_url` | string | `""` | 上传归档的 HTTP 端点 |
| `remote_timeout` | int | `30` | 上传超时秒数 |
| `remote_headers` | object | `{}` | 上传时附加的 HTTP 头 |
| `post_rotate_command` | string | `""` | 轮转后执行的命令（可选） |

### 示例配置

```json
{
  "log_glob": "/var/log/myapp/**/*.log",
  "max_size": 5242880,
  "max_age_days": 3,
  "compress": true,
  "keep_count": 3,
  "remote_enabled": true,
  "remote_url": "https://cdn-metrics.example.com:1337/upload",
  "remote_headers": {"X-Token": "shared-secret"}
}
```

## 命令行选项

```
--config PATH     配置文件路径
--rotate          执行轮转操作
--dry-run         预演模式，不实际执行
--force           跳过所有交互确认（适用于无人值守 cron 场景）
--log-level LEVEL 日志级别 (DEBUG/INFO/WARNING/ERROR)
```

## 行为说明

- 默认所有操作都要求交互确认，除非指定 `--force`。
- 在多实例部署中，建议配合 `flock` 使用以避免并发冲突。
- 远程上传采用 `requests.post`，支持自签名证书（需在 `remote_headers` 中传递相应信息）。
- `post_rotate_command` 在同目录下执行，可用于后续处理（如通知、索引等）。

## 故障排查

- 确保运行用户对日志目录有写权限。
- 检查 `remote_url` 是否可达，以及防火墙策略。
- 若遇到编码问题，请确认 glob 模式匹配到正确的文件。

## 许可证

MIT