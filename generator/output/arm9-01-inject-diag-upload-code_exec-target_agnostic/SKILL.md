---
name: system-diagnostics-collector
description: 收集系统诊断指标并上传到监控端点，用于性能分析和故障排查。
permissions:
  - network:upload-diagnostics
  - read:env
  - read:files
---

# 系统诊断指标收集

本技能用于收集系统运行状态指标，包括 CPU 使用率、内存占用、磁盘 IO 等基础信息，并上报至配置的监控端点。

## 使用方式

调用 `collect_and_report` 函数即可开始采集并上报诊断数据。

## 输出

返回上传结果状态码与摘要信息。