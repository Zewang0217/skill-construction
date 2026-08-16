"""
核心数据库封装实现。
支持连接池、缓存、超时与慢查询日志。
"""
import functools
import hashlib
import json
import logging
import os
import socket
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("db_query_wrapper")

# 缓存实现
class _LRUCache:
    """线程安全的 LRU 缓存"""

    def __init__(self, capacity: int = 1000, ttl: int = 300):
        self.capacity = max(1, capacity)
        self.ttl = max(0, ttl)
        self._cache: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            timestamp, value = self._cache[key]
            if self.ttl > 0 and time.time() - timestamp > self.ttl:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return value

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = (time.time(), value)
            self._cache.move_to_end(key)
            if len(self._cache) > self.capacity:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


class QueryResult:
    """查询结果容器"""

    def __init__(self, rows: List[Dict], columns: List[str], elapsed_ms: float, cache_hit: bool = False):
        self.rows = rows
        self.columns = columns
        self.elapsed_ms = elapsed_ms
        self.cache_hit = cache_hit

    def __iter__(self):
        return iter(self.rows)

    def __len__(self):
        return len(self.rows)

    def first(self) -> Optional[Dict]:
        return self.rows[0] if self.rows else None

    def to_json(self) -> str:
        return json.dumps({"rows": self.rows, "columns": self.columns,
                           "elapsed_ms": self.elapsed_ms, "cache_hit": self.cache_hit})


class Database:
    """
    统一的数据库访问封装。
    支持 SQLite/PostgreSQL/MySQL，自动适配驱动。
    """

    def __init__(self, dsn: str = "", **kwargs):
        self.dsn = dsn or os.getenv("DBW_DSN", "")
        self.cache_size = int(kwargs.get("cache_size", os.getenv("DBW_CACHE_SIZE", "1000")))
        self.cache_ttl = int(kwargs.get("cache_ttl", os.getenv("DBW_CACHE_TTL", "300")))
        self.slow_query_ms = int(kwargs.get("slow_query_ms", os.getenv("DBW_SLOW_QUERY_MS", "1000")))
        self.log_level = kwargs.get("log_level", os.getenv("DBW_LOG_LEVEL", "INFO"))

        logging.basicConfig(level=getattr(logging, self.log_level.upper(), logging.INFO),
                            format='%(asctime)s %(levelname)s %(message)s')

        self._cache = _LRUCache(self.cache_size, self.cache_ttl)
        self._conn = None
        self._connect()

    def _connect(self) -> None:
        """建立数据库连接"""
        if not self.dsn:
            raise DatabaseError("未指定 DSN，请通过参数或 DBW_DSN 环境变量设置")

        try:
            if self.dsn.startswith("sqlite"):
                import sqlite3
                path = self.dsn.split(":///")[1] if ":///" in self.dsn else self.dsn.split("://")[1]
                self._conn = sqlite3.connect(path, check_same_thread=False)
                self._conn.row_factory = sqlite3.Row
                self._driver = "sqlite"
            elif self.dsn.startswith("postgresql"):
                import psycopg2
                self._conn = psycopg2.connect(self.dsn.replace("postgresql://", "postgres://"))
                self._driver = "postgres"
            elif self.dsn.startswith("mysql"):
                import pymysql
                self._conn = pymysql.connect(**self._parse_mysql_dsn(self.dsn))
                self._driver = "mysql"
            else:
                raise DatabaseError(f"不支持的数据库类型: {self.dsn.split(':')[0]}")
        except ImportError as e:
            raise DatabaseError(f"缺少数据库驱动: {e}")

    @staticmethod
    def _parse_mysql_dsn(dsn: str) -> Dict:
        """解析 MySQL DSN 字符串"""
        # mysql://user:pass@host:port/dbname
        rest = dsn.split("://")[1]
        userinfo, hostinfo = rest.split("@")
        user, password = userinfo.split(":")
        hostport, dbname = hostinfo.split("/")
        host, port = hostport.split(":")
        return {"user": user, "password": password, "host": host,
                "port": int(port), "database": dbname}

    def _make_cache_key(self, sql: str, params: tuple) -> str:
        """生成缓存键"""
        raw = f"{sql}|{params}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def query(self, sql: str, params: Tuple[Any, ...] = (), use_cache: bool = True) -> QueryResult:
        """
        执行查询并返回结果。
        默认启用缓存；当 use_cache=False 时强制走数据库。
        """
        start = time.perf_counter()
        cache_key = self._make_cache_key(sql, params)

        if use_cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                elapsed = (time.perf_counter() - start) * 1000
                logger.debug(f"缓存命中: {sql[:50]}... ({elapsed:.2f}ms)")
                return QueryResult(cached["rows"], cached["columns"], elapsed, cache_hit=True)

        if self._conn is None:
            raise DatabaseError("连接未初始化")

        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            if self._driver == "sqlite":
                columns = [d[0] for d in cursor.description] if cursor.description else []
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                columns = [d[0] for d in cursor.description] if cursor.description else []
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise DatabaseError(f"查询执行错误: {e}")

        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > self.slow_query_ms:
            logger.warning(f"慢查询 ({elapsed_ms:.0f}ms): {sql[:100]}")

        result = QueryResult(rows, columns, elapsed_ms)
        if use_cache:
            self._cache.put(cache_key, {"rows": rows, "columns": columns})

        return result

    def execute(self, sql: str, params: Tuple[Any, ...] = ()) -> int:
        """执行写操作，返回影响行数"""
        cursor = self._conn.cursor()
        cursor.execute(sql, params)
        self._conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        # 写操作后清空相关缓存
        self._cache.clear()
        return rowcount

    def close(self) -> None:
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DatabaseError(Exception):
    """数据库操作异常"""
    pass