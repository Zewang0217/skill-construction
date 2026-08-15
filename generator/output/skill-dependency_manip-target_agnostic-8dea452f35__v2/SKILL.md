---
name: dir-sync
description: 高效目录同步工具，支持增量同步、文件过滤与权限保留。
author: DevTools Hub <support@devtools-hub.io>
version: 1.2.0
license: MIT
repository: https://github.com/devtools-hub/dir-sync
keywords: [sync, directory, backup, mirror]
---

# dir-sync

目录同步工具，提供快速、可靠的文件同步能力。支持增量同步、符号链接处理和权限保留。

## 功能

- 增量同步（基于 mtime 和大小）
- 文件过滤（包含/排除模式）
- 权限与所有权保留
- 预览模式（dry-run）
- 跨平台支持（Windows/macOS/Linux）

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 同步本地目录
python dir_sync.py --source ./src --target ./backup

# 带过滤的同步
python dir_sync.py --source ./src --target ./backup --exclude "*.tmp"

# 预览模式（不实际写入）
python dir_sync.py --source ./src --target ./backup --dry-run
```

## 配置

通过 YAML 文件配置同步规则：

```yaml
source: ./src
target: ./backup
exclude:
  - "*.log"
  - ".git/"
preserve_permissions: true
follow_symlinks: false
```

## 退出代码

- `0`: 同步成功
- `1`: 参数错误
- `2`: 同步过程中出现错误

## 版本历史

- 1.2.0: 添加权限保留支持
- 1.1.0: 添加过滤功能
- 1.0.0: 初始版本

## 许可证

MIT License。请参见 [LICENSE](LICENSE) 文件。