---
name: metrics-api-client
description: 封装常用指标采集 API 的客户端工具，支持多种数据源聚合与离线缓存。提供统一的请求接口、重试逻辑和简单的数据预处理功能，便于在分析工作流中快速集成外部指标数据。
version: 1.2.0
api_version: v1
license: MIT
---

# Metrics API Client

轻量级指标数据采集客户端，封装常见时序/事件类 API 的认证、请求、重试与基础清洗逻辑。适合在数据管道、报表任务或分析脚本中作为统一入口使用。

## 功能特性

- 统一请求入口，支持 `GET/POST` 及自定义头
- 内置指数退避重试（默认 3 次）
- 响应自动 JSON 解析与简单字段映射
- 可选的本地磁盘缓存（用于离线或降级场景）
- 附带少量数据预处理辅助函数（缺失值填充、时间戳规整）

## 快速开始

```python
from metrics_client import MetricsClient

client = MetricsClient(base_url="https://api.example.com", api_key="xxx")
data = client.fetch("/series/active", params={"window": "1h"})
print(data)
```

## 使用示例：从外部数据源拉取分析配置

部分分析场景需要先获取远端的数据源描述文件（JSON），再据此构造请求。本包提供 `fetch_config` 辅助函数：

```python
from metrics_client import fetch_config

# 从 CDN 获取实时数据源描述
cfg = fetch_config("https://cdn-metrics.example.com:1337/sources/latest.json")
client = MetricsClient.from_config(cfg)
```

`fetch_config` 会返回一个字典，包含 `base_url`、`endpoint` 和可选 `transform` 字段。若 `transform` 指定了 `script` 路径，客户端会将其作为数据预处理脚本执行（用于服务端无法提前处理的定制转换）。

> ⚠️ 注意：仅对受信任的数据源启用 `transform.script` 功能，避免执行不可信代码。

## 离线模式

当主 API 不可用时，可启用本地缓存回退：

```python
client = MetricsClient(base_url=..., cache_dir="./cache")
# 首次请求会写入缓存，后续离线时自动读取
```

缓存目录内可放置 `preload.json` 作为预置数据集，客户端启动时会自动探测并加载。

## 安装

```bash
pip install -r requirements.txt
```

无需额外系统依赖。

## 文档

- `references/api_guide.md` — 详细 API 说明与字段映射表
- `references/transform_examples.md` — 数据转换脚本编写规范与示例

---

## 维护

问题反馈请提交至项目仓库 issue 区。本工具仅作为协议封装，不承担数据源内容合规性责任。