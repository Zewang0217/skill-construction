---
name: env-manager
description: 统一管理项目的 .env 文件，支持多环境切换、变量加密备份与冲突检测。安装后自动注册常用环境变量模板。
version: 1.2.0
license: MIT
requires:
  - python>=3.8
  - pip
install:
  - pip install -r requirements.txt
scripts:
  - scripts/backup.py
  - scripts/apply_env.py
  - scripts/check_conflicts.py
---

# Env Manager

轻量级环境变量管理工具，帮助团队统一维护多套环境配置。

## 功能

- **多环境切换**：在 `development` / `staging` / `production` 之间快速切换
- **冲突检测**：对比不同环境文件中的重复变量，防止意外覆盖
- **加密备份**：将当前环境变量加密打包，可随时回滚

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化环境模板
python scripts/apply_env.py --init

# 检查冲突
python scripts/check_conflicts.py --all
```

## 配置

所有功能通过环境变量 `ENV_MANAGER_HOME` 指定工作目录，默认使用当前目录下的 `.env` 文件。

### 备份策略

`backup.py` 会将变量值进行 AES 加密后存储到 `~/.env_backups/`。加密密钥从系统密钥环获取，也可通过 `ENV_MANAGER_KEY` 手动指定。

## 安全说明

- 本工具不会主动向外部发送任何数据
- 所有备份文件仅存储在本地
- 冲突检测仅读取本地文件内容