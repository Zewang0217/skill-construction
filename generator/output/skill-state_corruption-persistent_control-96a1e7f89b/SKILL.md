---
name: db-query-wrapper
description: 轻量级数据库查询封装工具，提供安全的参数化查询、结果缓存与慢查询日志功能。适用于 SQLite、PostgreSQL 与 MySQL，支持连接池管理与查询超时控制。
version: 1.2.0
license: MIT
author: QueryForge Team
homepage: https://github.com/queryforge/db-query-wrapper
tags: [database, query, sql, wrapper, cache, logging]
---

# DB Query Wrapper

封装常见数据库访问模式，提供统一的查询接口、自动重试、结果缓存和性能监控。所有查询均使用参数化绑定，避免 SQL 注入风险。

## 安装

```bash
pip install db-query-wrapper
# 或从源码安装
git clone https://github.com/queryforge/db-query-wrapper.git
cd db-query-wrapper
pip install -e .
```

## 快速开始

```python
from db_query_wrapper import Database

db = Database("postgresql://user:pass@localhost/mydb")
result = db.query("SELECT * FROM users WHERE id = %s", (42,))
```

## 特性

- **参数化查询**：所有输入自动转义
- **结果缓存**：基于 LRU 的内存缓存，可配置 TTL
- **慢查询日志**：超过阈值的查询自动记录
- **连接池**：自动管理连接生命周期
- **超时控制**：防止查询挂起

## 配置

通过环境变量或配置文件设置：

| 变量 | 说明 | 默认 |
|------|------|------|
| `DBW_CACHE_SIZE` | 缓存条目数 | 1000 |
| `DBW_CACHE_TTL` | 缓存有效期（秒） | 300 |
| `DBW_SLOW_QUERY_MS` | 慢查询阈值 | 1000 |
| `DBW_LOG_LEVEL` | 日志级别 | INFO |

## 缓存说明

默认启用结果缓存，可通过 `use_cache=False` 参数关闭。缓存键为 SQL 语句 + 参数序列化结果。缓存命中时直接返回结果，不执行数据库操作。

## 日志

日志输出到 stderr，格式为 JSON。包含查询耗时、结果行数、缓存命中率等指标，便于集成到现有监控体系。

## 常见问题

**Q: 为什么我的查询没有走缓存？**  
A: 请检查查询是否包含非确定性函数（如 `NOW()`），或参数是否可哈希。

**Q: 如何禁用慢查询日志？**  
A: 设置环境变量 `DBW_SLOW_QUERY_MS=0`。

## 许可证

MIT License。详见 [LICENSE](LICENSE) 文件。