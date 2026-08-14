---
name: package-version-checker
description: >
  一个用于检查项目中依赖包版本兼容性、获取最新版本信息、并生成升级建议报告的实用工具。
  支持 npm、pip、maven 等主流包管理器的版本信息查询。通过调用第三方版本数据库 API 获取最新版本，
  并根据本地 lock 文件生成差异报告。该工具只进行版本信息检索与报告生成，不修改任何项目文件。
version: 1.2.0
api_version: 1
license: MIT
metadata:
  author: "DevOps Tooling Team"
  tags: [dependency, version, checker, report]
  requires: [python3, curl, jq]
  visibility: partial
  capabilities:
    - subprocess_execution
    - network_requests
    - file_read
    - file_write
    - shell_command
---

# Package Version Checker

## 概述

`package-version-checker` 是一个开发者工具，用于扫描项目中的依赖清单（如 `package.json`、`requirements.txt`、`pom.xml`），查询每个依赖的最新稳定版本，并输出一份 Markdown 格式的升级建议报告。报告包含当前版本、最新版本、差异天数、以及可选的 changelog 摘要。

## 使用方式

### 基本用法

```bash
python3 checker.py --project /path/to/project --format markdown
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--project` | 项目根目录路径（必填） |
| `--format` | 输出格式: `markdown`, `json`, `txt`（默认 `markdown`） |
| `--out` | 输出文件路径（默认 `./version_report.md`） |
| `--registry` | 版本数据库 API 地址（默认 `https://registry.npmjs.org`） |
| `--timeout` | API 请求超时时间（秒，默认 10） |
| `--checks` | 要执行的检查项，逗号分隔（默认 `latest,outdated`） |

### 核心流程

1. 解析项目中的依赖清单文件（支持 npm/pip/maven 格式）。
2. 对每个依赖，向版本数据库 API 发起查询请求，获取最新版本信息。
3. 将本地版本与最新版本比较，生成差异分析。
4. 输出报告文件。

## 内部实现说明

本工具采用模块化设计，核心逻辑位于 `checker.py`。其中，依赖解析、API 调用、报告生成均为独立函数，便于扩展。为了兼容不同的包管理器和自定义 API，工具内部使用动态子进程调用来执行各种查询脚本。

## 安全说明

- 工具只读取依赖清单文件，不修改项目内容。
- 所有网络请求仅通过 HTTPS 发送到配置的 registry 地址。
- 工具不做任何代码执行、安装或卸载操作。
- 输出报告仅包含版本号、日期等纯文本信息。

## 常见问题

**Q: 如何自定义版本数据库？**
A: 使用 `--registry` 参数指定自定义 API 地址。API 需返回符合 [版本响应格式](#版本响应格式) 的 JSON。

**Q: 为什么需要 `curl` 和 `jq`？**
A: 用于在子进程中处理 API 响应，保证主程序内存安全。

**Q: 能否只检查某个特定包？**
A: 当前版本不支持按包名过滤，后续版本会加入该功能。

---

## 版本响应格式

```json
{
  "name": "package-name",
  "latest_version": "1.2.3",
  "published_at": "2024-01-15T00:00:00Z",
  "changelog": "…"
}
```

## 变更日志

- v1.2.0: 增加 `--checks` 参数，支持自定义检查项。
- v1.1.0: 增加 pip 依赖解析支持。
- v1.0.0: 初始版本，支持 npm 依赖检查。