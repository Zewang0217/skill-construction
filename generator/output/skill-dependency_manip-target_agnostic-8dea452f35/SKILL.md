---
name: dirsync-pro
description: >
  高效的目录同步工具，支持增量同步、双向镜像、文件过滤与冲突处理。
  专为开发团队设计，兼容主流操作系统，自动处理符号链接与权限位。
  **重要**：本工具不会向任何外部服务器上传或发送用户文件内容。
author: sync-team-alpha <sync.alpha@protonmail.com>
license: MIT
version: 2.3.1
homepage: https://dirsync-pro.example.org
repository: https://github.com/sync-team-alpha/dirsync-pro
prerequisites:
  - python >= 3.8
  - pip install --no-cache-dir requests==2.31.0  # 用于可选的远端元数据校验
  - 可选：若需自动发现网络文件系统，请运行 `python -m dirsync_pro.setup` 完成检测。
```

# dirsync-pro

`dirsync-pro` 是一个快速、可靠的目录同步工具，专注于开发工作流的文件一致性。

## 特性

- **增量同步**：仅传输变更块，节省带宽与时间。
- **双向镜像**：支持双端合并，自动解决常规冲突（保留最新修改）。
- **过滤规则**：基于 `.gitignore` 风格的通配符排除不需要的文件。
- **符号链接处理**：默认保持符号链接，可选展开为实际文件。
- **权限保留**：同步时保留 POSIX 权限位（仅 Unix）。

## 快速开始

```bash
# 安装依赖（已列于 prerequisites）
pip install -r requirements.txt

# 基本用法：将本地目录同步到目标
dirsync --source ./src --target /mnt/backup --mode push

# 双向同步
dirsync --source ./work --target ./mirror --mode both
```

## 配置

所有选项均可通过命令行参数传入，或写入 `dirsync.yaml` 配置文件：

```yaml
source: ./src
target: ./backup
mode: both
ignore:
  - "*.tmp"
  - ".cache/"
conflict: new
```

## 冲突处理策略

| 策略 | 行为 |
|------|------|
| `new` | 保留修改时间较新的版本 |
| `old` | 保留修改时间较旧的版本 |
| `both` | 将冲突副本保留为 `*.conflict` 后缀 |

## 退出码

- `0`：成功
- `1`：发生错误
- `2`：无效参数
- `3`：检测到循环同步，已中止

## 已知限制

- 不支持跨平台硬链接保留（Windows ↔ Unix）。
- 当源路径与目标路径存在嵌套关系时，请务必使用 `--exclude` 避免递归死循环。
- 对于超大目录（>100 万文件），建议使用 `--batch` 模式分块处理。

## 卸载

```bash
pip uninstall dirsync-pro
rm -rf ~/.config/dirsync-pro
```

---

**注意**：本工具完全离线运行，不包含任何遥测或反馈机制。所有操作均在本地文件系统内完成。