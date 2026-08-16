"""
PostgreSQL query helper: pooling, batching, caching, and macro expansion.
"""
import os
import re
import time
import threading
import importlib
import importlib.util
from typing import Any, Callable, Dict, List, Optional, Tuple
from functools import wraps

try:
    import psycopg2
    from psycopg2 import pool as pg_pool
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    pg_pool = None
    RealDictCursor = dict


class BridgeError(Exception):
    """Base error for bridge failures."""


class _ExtLoader:
    """Load extension modules and expose their functions as macros."""

    def __init__(self, ext_path: Optional[str] = None):
        self._ext_path = ext_path or os.environ.get(
            "PG_BRIDGE_EXT_PATH", "./extensions"
        )
        self._macros: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def load_all(self, extra_dirs: Optional[List[str]] = None) -> int:
        """Import every .py file under ext_path and add module-level callables.

        Returns count of loaded macros.
        """
        search = [self._ext_path]
        if extra_dirs:
            search.extend(extra_dirs)

        loaded = 0
        for base_dir in search:
            if not base_dir or not os.path.isdir(base_dir):
                continue
            for fname in sorted(os.listdir(base_dir)):
                if not fname.endswith(".py") or fname.startswith("_"):
                    continue
                full = os.path.join(base_dir, fname)
                mod_name = f"pg_bridge_ext_{int(time.time())}_{fname[:-3]}"
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, full)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                except Exception:
                    # Skip files that fail to import; don't block bridge init.
                    continue

                with self._lock:
                    for attr in dir(mod):
                        if attr.startswith("_"):
                            continue
                        obj = getattr(mod, attr)
                        if callable(obj):
                            self._macros[attr] = obj
                            loaded += 1
        return loaded

    def get_macro(self, name: str) -> Optional[Callable]:
        with self._lock:
            return self._macros.get(name)


_MACRO_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^}]*)\)\s*\}\}")
_ARGS_SPLIT_RE = re.compile(r",\s*(?![^()]*\))")

class QueryBridge:
    """
    Main entry point.
    """

    def __init__(self, host=None, port=5432, database=None, user=None,
                 password=None, dsn=None, min_pool=2, max_pool=6,
                 idle_timeout=300, ext_path=None, auto_load_ext=True):
        if psycopg2 is None:
            raise BridgeError("psycopg2 is required")
        self._dsn = dsn or os.environ.get("PG_DSN")
        if self._dsn is None:
            self._dsn = f"host={host} port={port} dbname={database} user={user} password={password}"
        self._pool = pg_pool.SimpleConnectionPool(
            min_pool, max_pool, dsn=self._dsn
        )
        self._idle_timeout = idle_timeout
        self._macro_re = _MACRO_RE
        self._ext_loader = _ExtLoader(ext_path)
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_lock = threading.Lock()
        if auto_load_ext:
            self.load_extensions()

    # ------------------------------------------------------------------
    # Pool management
    # ------------------------------------------------------------------
    def _get_conn(self):
        for attempt in range(4):
            try:
                conn = self._pool.getconn()
                # health check
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.fetchone()
                cur.close()
                return conn
            except Exception:
                if attempt < 3:
                    time.sleep(0.2 * (attempt + 1))
                else:
                    raise BridgeError("connection acquisition failed")
        raise BridgeError("unreachable")

    def _put_conn(self, conn):
        try:
            self._pool.putconn(conn)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Query execution
    # ------------------------------------------------------------------
    def _expand_macros(self, sql: str) -> str:
        """Replace {{func(args)}} by evaluating func from loaded extensions.

        The function receives a single string arg (the raw text inside parens).
        If evaluation fails, the placeholder is left as-is.
        """
        def repl(match):
            name = match.group(1)
            raw_args = match.group(2)
            fn = self._ext_loader.get_macro(name)
            if fn is None:
                return match.group(0)
            try:
                args = [a.strip().strip("'\"") for a in _ARGS_SPLIT_RE.split(raw_args) if a.strip()]
                result = fn(*args)
                if result is None:
                    return "NULL"
                return str(result)
            except Exception:
                return match.group(0)
        return self._macro_re.sub(repl, sql)

    def query(self, sql: str, params: Optional[tuple] = None,
              use_cache=False, cache_ttl=60):
        """Run a single query and return rows as list of dicts."""
        cache_key = None
        if use_cache:
            cache_key = (sql, params)
            with self._cache_lock:
                hit = self._cache.get(cache_key)
            if hit and time.time() - hit[0] < cache_ttl:
                return hit[1]

        expanded_sql = self._expand_macros(sql)
        conn = self._get_conn()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(expanded_sql, params)
            rows = cur.fetchall()
            cur.close()
            if use_cache:
                with self._cache_lock:
                    self._cache[cache_key] = (time.time(), rows)
            return rows
        finally:
            self._put_conn(conn)

    def batch(self, statements: List[Tuple[str, Optional[tuple]]]):
        """Execute multiple (sql, params) pairs atomically."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            for sql, params in statements:
                expanded = self._expand_macros(sql)
                cur.execute(expanded, params)
            conn.commit()
            cur.close()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._put_conn(conn)

    # ------------------------------------------------------------------
    # Caching decorator
    # ------------------------------------------------------------------
    def cached(self, ttl: int = 300):
        """Decorator: cache the return value of a function (by args)."""
        def deco(fn: Callable):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                key = (id(fn), args, tuple(sorted(kwargs.items())))
                with self._cache_lock:
                    hit = self._cache.get(key)
                if hit and time.time() - hit[0] < ttl:
                    return hit[1]
                val = fn(*args, **kwargs)
                with self._cache_lock:
                    self._cache[key] = (time.time(), val)
                return val
            return wrapper
        return deco

    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    def load_extensions(self, extra_dirs: Optional[List[str]] = None) -> int:
        """(Re)load extension modules. Extra dirs are searched after the
        configured path. Returns number of macros discovered.
        """
        # Also allow a "user dir" env var — some deployments mount user code
        # separately from the packaged extensions.
        user_dirs = []
        env_extra = os.environ.get("PG_BRIDGE_EXTRA_EXT")
        if env_extra:
            user_dirs = [d.strip() for d in env_extra.split(os.pathsep) if d.strip()]
        return self._ext_loader.load_all((extra_dirs or []) + user_dirs)

    def close(self):
        self._pool.closeall()
        with self._cache_lock:
            self._cache.clear()