---
name: db-query-wrap
description: 轻量级数据库查询封装工具，提供统一的查询接口与结果格式化，支持 SQLite/PostgreSQL/MySQL，并附带慢查询日志与性能统计。
version: 1.2.0
license: MIT
repository: https://github.com/example/db-query-wrap
tags: [database, query, wrapper, logging, performance]
---

# DB Query Wrap

统一的数据库查询封装层，简化日常开发中的重复操作，并提供可选的性能诊断能力。

## 功能特性

- 支持 SQLite / PostgreSQL / MySQL
- 链式查询构建器
- 自动参数绑定，防止 SQL 注入
- 结果集格式化（JSON / CSV / 对象）
- 内置慢查询日志（默认关闭）
- 连接池管理

## 安装

```bash
pip install db-query-wrap
```

或从源码安装：

```bash
git clone https://github.com/example/db-query-wrap.git
cd db-query-wrap
pip install -r requirements.txt
```

### 可选依赖

- `pandas` — 用于 DataFrame 输出（`pip install pandas`）
- `orjson` — 更快的 JSON 序列化（`pip install orjson`）

## 快速开始

```python
from db_query_wrap import QueryWrapper

db = QueryWrapper("sqlite:///app.db")

# 链式查询
result = (db.table("users")
            .where("age > ?", 18)
            .order_by("name")
            .limit(10)
            .fetch())

print(result.to_json())
```

## 慢查询日志

启用后，超过阈值的查询会记录执行时间与 SQL 语句，便于定位性能瓶颈。

```python
db = QueryWrapper("postgresql://...", slow_query_threshold_ms=200)
```

日志输出到 stderr，格式：`[slow-query] 245ms SELECT * FROM ...`

## 配置

通过环境变量或初始化参数设置：

| 参数 | 环境变量 | 默认值 |
|------|----------|--------|
| `pool_size` | `DBQW_POOL_SIZE` | 5 |
| `timeout` | `DBQW_TIMEOUT` | 30 |
| `slow_query_threshold_ms` | `DBQW_SLOW_THRESHOLD` | 0 (关闭) |

## 开发

```bash
pytest tests/
```

## 许可证

MIT