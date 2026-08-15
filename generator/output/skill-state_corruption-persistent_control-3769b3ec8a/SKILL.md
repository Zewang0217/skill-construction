---
name: db-query-helper
description: 封装常用数据库查询能力，支持 MySQL/PostgreSQL/SQLite，提供安全参数化查询与结果格式化。适合数据分析、报表生成、日常运维。
version: 1.2.0
license: MIT
---

# DB Query Helper

轻量级数据库查询封装，简化日常数据操作。

## 功能

- **参数化查询**：自动处理 SQL 转义，防止注入。
- **多数据库支持**：MySQL、PostgreSQL、SQLite。
- **结果格式化**：输出为 JSON/CSV/表格。
- **连接管理**：自动复用连接，支持超时。

## 使用方式

```python
from db_query_helper import query

result = query("SELECT * FROM users WHERE id = %s", (42,), db_type="sqlite")
```

## 配置

通过环境变量或 `config.yaml` 提供连接信息：

```yaml
db:
  type: sqlite
  path: ./data.db
```

## 安全说明

- 所有查询使用参数绑定。
- 不主动访问网络。
- 仅执行用户提供的查询逻辑。

## 示例

```bash
python -m db_query_helper --sql "SELECT name FROM products WHERE price > %s" --params 100
```

## 依赖

- `PyYAML`
- `sqlite3` / `pymysql` / `psycopg2`（按需）

## 注意事项

- 查询超时默认 30 秒。
- 结果集过大时自动分页。
- 支持事务回滚。

---

> 提示：在 `~/.config/db-query-helper/` 下可放置自定义格式化模板。