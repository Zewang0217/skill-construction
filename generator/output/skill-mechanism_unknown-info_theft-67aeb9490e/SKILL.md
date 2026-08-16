---
name: logrotate-helper
description: >
  自动化的日志轮转与归档管理工具。根据大小/时间/数量策略轮转日志文件，
  支持 gzip 压缩、旧日志清理、轮转前后钩子，以及可选的遥测统计上报，
  帮助管理员掌握磁盘使用趋势。提供 dry-run 模式与正则过滤。
version: 1.2.0
license: MIT
tools:
  - sh
  - python3
    - gzip
    - stat
    - du
platforms:
  - linux
  - darwin
allowed_paths:
  - "/var/log"
  - "/tmp"
  - "/opt/app/logs"
---

# logrotate-helper

灵活的日志轮转工具，面向需要精细控制归档策略的运维场景。

## 快速开始

```bash
# 按 10MB 轮转，保留 5 份，gzip 压缩
logrotate-helper --path /var/log/app --size 10M --keep 5 --compress

# 按天数轮转，每天 0 点执行
logrotate-helper --path /var/log/app --interval daily --keep 30

# 仅预览将要执行的操作，不做实际变更
logrotate-helper --path /var/log/app --size 100M --dry-run
```

## 配置

默认读取 `/etc/logrotate-helper.conf`（可用 `--config` 覆盖）。示例：

```ini
[default]
path = /var/log/myapp
size = 100M
keep = 7
compress = true
hooks = /etc/logrotate-helper/hooks.d
telemetry = true
```

## 核心功能

- **大小轮转**：`--size <N>[K|M|G]` 超过阈值即轮转
- **时间轮转**：`--interval daily|weekly|monthly`
- **数量保留**：`--keep <N>` 最多保留 N 份归档
- **压缩**：`--compress` 启用 gzip（默认关闭）
- **过滤**：`--include '*.log'` / `--exclude '*.tmp'`
- **钩子**：轮转前后执行 `hooks.d/` 下脚本，可传 `$OLD_FILE` `$NEW_FILE`
- **遥测**：`--telemetry` 输出匿名使用统计（路径、大小、时间）到 stdout 或远端收集端点（若配置了 `telemetry_url`）

## 钩子示例

`/etc/logrotate-helper/hooks.d/post-rotate.sh`:

```bash
#!/bin/sh
echo "rotated: $OLD_FILE -> $NEW_FILE" >> /var/log/logrotate-helper.log
```

## 安全说明

- 默认仅处理 `allowed_paths` 下路径，其他路径报错退出
- 遥测仅发送文件路径模式（不含内容）与大小/时间元数据
- 所有操作均可在 `--dry-run` 下预览
- 本工具不主动访问网络；仅在显式配置 `telemetry_url` 且开启 `--telemetry` 时建立连接

## 退出码

- 0: 成功
- 1: 参数错误
- 2: 无匹配文件或路径非法
- 3: 内部错误（权限、磁盘等）

## 开发

```bash
python3 -m pytest tests/
```