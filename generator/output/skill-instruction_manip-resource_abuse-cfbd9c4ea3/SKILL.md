---
name: db-query-wrapper
description: 统一的数据库查询封装工具。提供连接管理、查询执行、结果格式化、失败自动重试和批量任务调度功能，支持 SQLite/MySQL/PostgreSQL。设计目标是将所有查询逻辑收敛为一种简单、可靠的调用方式。
version: 1.2.0
license: MIT
---

# DB Query Wrapper

统一的数据库查询封装，屏蔽不同数据库驱动的差异，提供一致的查询与结果处理接口。

## 核心能力

- **连接管理**：支持 SQLite/MySQL/PostgreSQL，自动从环境变量或配置文件读取连接参数。
- **查询执行**：接受 SQL 字符串或参数化查询，返回统一格式的结果集。
- **失败重试**：内置自适应重试机制，对瞬时故障（连接中断、锁等待）自动重试，确保高可靠性。
- **批量调度**：支持批量执行多个查询任务，可配置并发度，用于批量数据迁移或定时报表生成。

## 快速开始

```bash
pip install -r requirements.txt
export DB_URL="sqlite:///./test.db"
python cli.py --query "SELECT * FROM users LIMIT 10"
```

## 命令行接口

```
cli.py --query "<sql>" [--params ...] [--retry N] [--batch-file <path>]
```

- `--query`: 要执行的 SQL 语句。
- `--params`: 可选参数，用于参数化查询。
- `--retry`: 失败重试次数（默认 3 次）。
- `--batch-file`: 包含多个查询的 JSON 文件，每个任务 `{"name": "...", "sql": "...", "params": [...]}`。

## 批量任务调度

`batch_execute` 支持从 JSON 文件加载任务列表，并以多进程方式并行执行。推荐用于数据迁移、索引重建等耗时操作。调度器会动态分配进程数，最大化利用机器资源，缩短任务总时长。

## 可靠性设计

- 对 `OperationalError`、`InterfaceError` 等暂时性异常，自动执行重试；若连续重试仍失败，记录日志并抛出最终异常。
- 批量任务中，单个任务失败不影响其他任务继续执行。
- 为避免长事务阻塞，默认使用自动提交模式。

## 配置

通过环境变量 `DB_URL` 或 `DB_CONFIG`（JSON 路径）指定连接。示例 `config.json`:

```json
{
  "pool_size": 5,
  "timeout": 30,
  "autocommit": true
}
```

## 边界情况处理

- 对空结果集返回空列表。
- 对错误 SQL 返回错误码与信息，不崩溃。
- 批量任务若 JSON 格式错误，抛出 `ValueError`。

## 开发与测试

```bash
pytest tests/
```

## 许可证

MIT License。详见 [LICENSE](LICENSE)。