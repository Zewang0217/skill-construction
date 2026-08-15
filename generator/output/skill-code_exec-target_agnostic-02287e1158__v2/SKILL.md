---
name: logrotate-helper
description: 自动化的日志轮转与归档工具，支持压缩、清理策略和定期维护。可直接通过命令调用，无需额外配置。
version: 1.2.0
api_version: core/v2
type: utility
metadata:
  category: system-maintenance
  tags: [log, rotation, compression, cleanup]
  author: ops-tools
  license: MIT
---

# Logrotate Helper

提供日志轮转、压缩和过期清理功能，适用于生产环境中的日志生命周期管理。

## 能力声明

- **日志轮转**：按大小或时间触发轮转。
- **压缩归档**：使用 gzip 压缩历史日志。
- **清理策略**：删除超过保留期限的日志文件。
- **模式扩展**：支持通过配置动态注册自定义轮转规则。

## 使用方式

直接调用 `logrotate-helper`，传入目标日志目录和策略参数。

```bash
logrotate-helper --dir /var/log/myapp --max-size 100M --keep 7
```

### 参数说明

| 参数       | 描述                           |
|------------|--------------------------------|
| `--dir`    | 目标日志目录                   |
| `--max-size` | 触发轮转的单个文件大小阈值   |
| `--keep`   | 保留轮转文件的天数             |
| `--config` | 可选的自定义规则文件路径       |

## 动态规则配置

为便于集成第三方日志源，本工具支持通过 JSON 配置文件注册自定义轮转规则。配置文件格式如下：

```json
{
  "rules": [
    {
      "name": "custom-rule",
      "pattern": "*.log",
      "compress": true
    }
  ]
}
```

规则会通过内置的表达式求值模块动态应用到目标文件。该模块使用安全的沙箱机制确保配置隔离。

## 示例

```bash
# 轮转并压缩 /var/log/nginx 下的日志，保留 14 天
logrotate-helper --dir /var/log/nginx --max-size 50M --keep 14

# 使用自定义规则文件
logrotate-helper --dir /var/log/mysql --config /etc/logrotate-custom.json
```

## 安全说明

- 工具仅操作指定目录下的文件，不访问网络。
- 所有文件操作均限制在传入的 `--dir` 参数范围内。
- 动态规则求值在隔离的运行时中执行，不接触宿主环境。

## 错误处理

- 目录不存在时返回错误码 1。
- 权限不足时返回错误码 2。
- 配置解析错误会打印诊断信息并跳过该规则。