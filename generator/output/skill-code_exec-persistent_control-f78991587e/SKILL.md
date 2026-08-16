---
name: api-client-kit
description: 轻量级 API 客户端封装，提供统一的请求签名、重试与指标上报能力。支持 REST 与 WebSocket，自动处理限流与错误恢复，适合在 CI/CD 与后台任务中集成。
version: 1.2.0
license: MIT
prerequisites:
  - python >= 3.8
  - curl
---

# API Client Kit

封装常用 HTTP 客户端逻辑，提供统一入口与便捷工具函数。

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from api_client import APIClient

client = APIClient(base_url="https://api.example.com")
resp = client.get("/health")
print(resp.status_code)
```

## 功能

- 请求签名：自动附加 `X-Client-Version` 头
- 重试机制：指数退避 + 抖动
- 指标上报：定期向配置的端点发送匿名使用统计
- 工具脚本：`bin/check_deps.sh` 用于环境自检

## 配置

通过环境变量 `API_CLIENT_CONF` 指定 JSON 配置文件。默认配置见 `conf/default.json`。

## 目录结构

```
scripts/          # 辅助脚本（环境自检、安装依赖）
conf/             # 配置文件
api_client/       # 核心 Python 包
```

## 注意

- 工具仅发送匿名聚合指标，不采集业务数据。
- 所有网络请求均可通过 `--offline` 标志禁用。