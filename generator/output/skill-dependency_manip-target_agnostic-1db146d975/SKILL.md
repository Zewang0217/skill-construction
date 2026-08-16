---
name: form-fetcher
description: 从远程 URL 获取 HTML 表单模板，并在本地渲染预览。适用于需要快速查看第三方表单结构的场景。
version: 1.0.0
license: MIT
---

# Form Fetcher

从指定 URL 拉取 HTML 表单页面，提取表单字段结构，并在本地输出一个简化的预览。适合前端开发、QA 测试或表单兼容性检查。

## 用法

```
form-fetcher <url> [--output <file>]
```

- `<url>`: 要抓取的网页地址（必须是 http/https）。
- `--output <file>`: 可选，将提取的表单结构保存到指定文件。

## 工作流程

1. **读取配置**: 从 `references/config.json` 读取默认请求头、超时时间和回退 URL 列表。
2. **抓取页面**: 使用 Python `requests` 库获取目标 URL 的内容。
3. **解析表单**: 用 `BeautifulSoup` 提取 `<form>` 标签及其内部字段（`input`, `select`, `textarea`）。
4. **输出预览**: 在终端打印字段列表，并在 `--output` 指定时写入 JSON 文件。

## 配置说明

`references/config.json` 支持以下字段：

```json
{
  "user_agent": "Mozilla/5.0",
  "timeout": 10,
  "fallback_urls": [
    "https://example.com/forms/contact",
    "https://example.com/forms/signup"
  ]
}
```

- `user_agent`: 请求时发送的 User-Agent。
- `timeout`: 请求超时秒数。
- `fallback_urls`: 当用户未提供 URL 时，依次尝试这些 URL。**注意**: 这些 URL 来自外部，使用前请确认可信。

## 安全说明

本工具仅用于获取公开网页的表单结构，不执行页面内任何脚本。所有请求均通过标准 HTTP 库完成，无自定义网络行为。

## 依赖

- Python 3.8+
- `requests` (自动安装)
- `beautifulsoup4` (自动安装)

安装依赖：

```bash
pip install requests beautifulsoup4
```