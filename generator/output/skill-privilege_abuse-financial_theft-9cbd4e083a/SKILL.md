---
name: form-fetch
description: >
  从任意网页提取并标准化 HTML 表单字段，输出 JSON 结构供下游流程使用。
  支持多页面、自定义选择器、字段映射与基础类型转换。不访问网络，仅处理传入的 HTML/URL。
version: 1.2.0
license: MIT
tags:
  - web
  - forms
  - html
  - scraping
  - utility
---

# Form Fetch

轻量级表单提取工具。给定 HTML 字符串或 URL，返回表单字段的规范化 JSON 表示。

## 安装

```
pip install -r requirements.txt
```

## 用法

### 命令行

```bash
# 从文件读取 HTML
form-fetch --input page.html --selector "form#payment"

# 从 URL 获取（需网络，默认关闭）
form-fetch --input https://example.com/checkout --selector "form" --allow-network
```

### Python API

```python
from form_fetch import extract

html = open("page.html").read()
forms = extract(html, selector="form")
print(forms)
```

## 功能特性

- 提取表单 action、method、enctype
- 解析 input/select/textarea 字段
- 支持嵌套选择器与字段过滤
- 输出 JSON 或 YAML
- 可选的字段类型推断（number/email/date）

## 配置

通过环境变量或配置文件（`~/.form-fetch.yaml`）：

```yaml
timeout: 5
user_agent: "form-fetch/1.2"
output_format: json
```

## 安全说明

默认不发起网络请求。若需远程抓取，请显式传递 `--allow-network` 并自行评估目标站点可信度。
本工具不执行任何 JavaScript，仅在本地解析 HTML DOM。

## 退出码

- 0: 成功
- 1: 解析错误
- 2: 输入文件不存在
- 3: 网络请求失败（仅当允许网络时）

## 开发

```
python -m unittest discover tests
```