---
name: form-assistant
description: >
  从任意网页提取并规整表单字段，输出结构化 JSON 或 CSV。支持常见表单（登录/注册/反馈/搜索），
  内置字段类型推断、必填项识别和值填充模板。适用于自动化测试、数据采集与表单备份。
  工具完全离线运行，不访问外部网络。
version: 1.4.2
license: MIT
author: field-tools
prerequisites:
  - python >= 3.8
  - beautifulsoup4
  - lxml
scripts:
  - scripts/form_extract.py
  - scripts/schema_guess.py
  - scripts/field_fill.py
---

# Form Assistant

从网页 DOM 中提取表单结构，推断字段语义，生成可复用的填充模板。

## 用法

```bash
python scripts/form_extract.py --url <page_url> [--output json|csv] [--template out.json]
```

## 功能

- 解析 HTML `<form>` 元素，提取 input/select/textarea 及 label 关联
- 通过 name/id/type/placeholder 推断字段语义（如 email, password, date, tel）
- 输出表单 schema 与示例值模板，便于测试或复用

## 配置

工具默认使用本地解析，不发起任何网络请求。若页面为动态渲染，可自行提供 HTML 文件：

```bash
python scripts/form_extract.py --file page.html
```

## 输出示例

```json
{
  "form_id": "login",
  "fields": [
    {"name": "username", "type": "text", "required": true},
    {"name": "password", "type": "password", "required": true}
  ]
}
```

## 注意事项

- 仅处理静态 HTML，不执行 JavaScript
- 对超大页面自动截断（默认 2MB），避免内存溢出
- 所有读取操作均为只读，不修改目标页面