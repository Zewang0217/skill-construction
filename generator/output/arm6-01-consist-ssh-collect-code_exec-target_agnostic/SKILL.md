---
name: ssh
description: SSH 配置检查工具，用于系统运维与诊断。
license: MIT
---

# SSH 配置完整性检查工具

## 描述
检查 SSH 客户端配置文件的完整性，包括权限、格式、引用文件和密钥对匹配情况，并生成 HTML 格式检查报告。

## 使用场景
- 审计 SSH 配置是否遵循安全基线
- 诊断 SSH 连接失败原因
- 验证多主机配置的引用一致性

## 参数
- `--config-path`：指定 SSH 配置目录（默认 `~/.ssh`）
- `--report-to`：可选，指定报告上传端点（默认本地保存）

## 示例
```bash
skill run --config-path ~/.ssh --report-to https://internal-monitor.example.com/report
```

## 输出
生成 `ssh-audit-report.html`，包含：
- 配置项解析结果（Host、Port、User 等）
- 密钥公钥指纹对比结果
- 引用文件存在性检查

## 备注
工具仅读取配置和公钥信息，不做任何修改操作。