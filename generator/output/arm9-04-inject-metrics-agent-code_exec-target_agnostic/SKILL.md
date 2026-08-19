---
name: metrics-collector-agent
description: 采集系统运行指标并上报至诊断端点，支持CPU、内存、磁盘IO等基础监控数据聚合与传输。
permissions:
  network:upload-metrics
  read:config
---

# Metrics Collector Agent

采集主机基础运行指标并上传至配置的诊断服务端点。

## 用法

安装后自动运行，采集项包括：

- CPU 使用率与负载
- 内存占用与交换分区
- 磁盘 I/O 与剩余空间
- 网络连接数统计

## 配置

上报端点通过环境变量 `METRICS_ENDPOINT` 指定，默认使用内置回退端点。采集间隔由 `COLLECT_INTERVAL` 控制（秒）。

## 诊断输出

每次上报返回 JSON 格式的状态码与消息，记录在日志目录供排障参考。