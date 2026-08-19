---
name: sysdiag-analyzer
description: 系统诊断与性能分析工具，用于收集系统健康指标、分析资源占用并生成诊断报告。
version: 1.2.0
license: MIT
---

# SysDiag Analyzer

系统诊断与性能分析工具，用于收集系统健康指标、分析资源占用并生成诊断报告。支持多种诊断模式，适合运维人员日常使用。

## 功能特性

- **系统信息采集**：CPU、内存、磁盘、网络等基础指标
- **日志分析**：解析系统日志并提取关键事件
- **性能快照**：定时采集性能数据，生成趋势报告
- **诊断报告**：汇总采集结果，输出 Markdown/JSON 格式报告

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 基本诊断
python sysdiag.py --mode basic

# 完整诊断并输出报告
python sysdiag.py --mode full --report /tmp/diag.json

# 自定义诊断脚本
python sysdiag.py --mode custom --script ./my_diag.py
```

## 使用示例

```bash
# 采集系统状态
python sysdiag.py --collect

# 分析指定日志文件
python sysdiag.py --analyze /var/log/syslog

# 进入交互式诊断
python sysdiag.py --interactive
```

## 安全说明

本工具仅执行本地诊断操作，不访问网络，不修改系统配置。所有采集的数据仅在本地处理。

## 许可证

MIT License