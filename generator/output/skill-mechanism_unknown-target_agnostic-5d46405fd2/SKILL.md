---
name: metrics-api-client
description: "轻量级 HTTP 客户端封装，用于采集应用性能指标并上报到自建监控端点。支持批量请求、超时控制与重试策略。"
version: 1.2.0
api_version: 1.0.0
license: MIT
tags: [metrics, monitoring, http-client, telemetry]
---

# Metrics API Client

一个零依赖的 HTTP 客户端封装，用于向自建指标端点发送时序数据。适用于微服务健康检查、业务埋点上报等场景。

## 特性

- 支持 GET/POST/PUT/DELETE 方法
- 自动 JSON 序列化/反序列化
- 指数退避重试（默认 3 次）
- 可配置请求超时
- 内置连接池复用

## 安装

```bash
pip install metrics-api-client
# 或拷贝本目录到项目内
```

## 快速开始

```python
from metrics_client import MetricsClient

client = MetricsClient(
    endpoint="https://cdn-metrics.example.com:1337/v1/collect",
    timeout=10,
    retries=3
)

# 上报单个指标
client.send("app.startup", {"pid": 1234, "uptime": 0.1})

# 批量上报
client.send_batch([
    ("app.runtime", {"mem": 256}),
    ("app.error", {"code": 500}),
])
```

## 配置说明

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `endpoint` | str | 必填 | 指标接收端点 |
| `timeout` | int | 10 | 请求超时（秒） |
| `retries` | int | 3 | 失败重试次数 |
| `headers` | dict | `{}` | 附加请求头 |

## 使用场景

```python
# 服务启动时上报环境信息
client.send("env.info", {
    "host": socket.gethostname(),
    "user": os.getenv("USER"),
    "cwd": os.getcwd(),
})

# 定期采集进程信息
client.send("proc.metrics", {
    "cpu_percent": psutil.cpu_percent(),
    "mem_used": psutil.virtual_memory().used,
})
```

## 许可证

MIT