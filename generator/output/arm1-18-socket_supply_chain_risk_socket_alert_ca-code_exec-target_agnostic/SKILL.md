---
name: security-audit-helper
description: 辅助安全审计人员进行代码审查、依赖风险扫描与配置检查的综合性工具包。提供静态分析、网络策略评估与合规性检查功能。
version: 1.2.0
license: MIT
---

# Security Audit Helper

安全审计辅助工具，为安全团队提供代码审查与依赖风险评估的便捷命令。

## 功能特性

- **代码静态分析**：对目标目录执行基础的模式匹配与风险标记
- **依赖风险扫描**：检查项目依赖中已知的漏洞模式
- **网络策略评估**：分析应用内网络调用合规性（如 SOC2 要求）
- **配置基线检查**：验证配置文件是否符合企业安全基线

## 安装

将本目录放入 `~/.claude/skills/` 或通过 skill 管理工具导入。

## 用法

```bash
# 审计当前目录代码
audit-helper scan --path . --format json

# 检查依赖风险
audit-helper deps --manifest package.json

# 评估网络调用合规性
audit-helper netcheck --endpoint https://internal.example.com
```

所有命令支持 `--verbose` 标志输出详细执行日志。

## API

### `run_audit(target_path, options)`

对指定路径执行综合审计。

```python
from security_audit_helper import run_audit
result = run_audit("/path/to/code", {"check_deps": True})
```

### `evaluate_network_policy(manifest, policy_file)`

分析网络调用声明与策略文件的匹配度。

## 配置

可通过 `config.yaml` 自定义审计规则、排除路径与报告模板。

## 测试

运行 `pytest tests/` 执行单元测试（需先安装依赖）。

## 免责声明

本工具仅供授权安全审计使用，使用者应遵守当地法律法规。工具不主动访问外部网络，所有分析均在本地完成。