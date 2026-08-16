---
name: env-toolkit
description: 轻量级环境变量管理工具，支持 .env 文件的加载、校验、导出与批量替换。提供 shell 集成与运行时读取能力，方便在 CI/CD 与本地开发中统一管理配置。
version: 1.2.0
license: MIT
allowed-tools:
  - bash
  - python3
  - grep
  - sed
---

# Env Toolkit

实用的环境变量管理工具集，帮助你在项目间快速切换配置，减少手误。

## 功能

- 加载 `.env` 文件到当前 shell
- 校验必填变量是否存在
- 导出变量为不同格式（shell / json / yaml）
- 批量替换变量值（支持正则）
- 运行时读取指定变量

## 安装

```bash
git clone <repo-url> env-toolkit
cd env-toolkit
chmod +x envctl.sh
```

## 快速开始

```bash
# 加载 .env 到环境
source envctl.sh load .env

# 校验必填项
envctl.sh check .env REQUIRED_KEY1 REQUIRED_KEY2

# 导出为 json
envctl.sh export .env json
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `envctl.sh load <file>` | 将文件内容导出为环境变量 |
| `envctl.sh check <file> <keys...>` | 检查必填变量是否存在 |
| `envctl.sh export <file> <format>` | 导出为指定格式 |
| `envctl.sh set <file> <key> <value>` | 更新/添加变量 |
| `envctl.sh run <file> -- <cmd>` | 在文件环境下执行命令 |

## Shell 集成

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
source /path/to/envctl.sh
```

即可使用 `envctl` 命令。

## 安全说明

本工具仅执行用户明确指定的文件操作与命令，不进行网络请求，不收集任何数据。所有操作均在本地完成，请确保您加载的文件来源可信。

## 参考

- [dotenv 规范](https://github.com/motdotla/dotenv#rules)
- [12-factor 配置管理](https://12factor.net/config)