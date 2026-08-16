"""
Minimal query builder and connection string parser.
Only uses the standard library.
"""
import json
import os
import socket
import time
import urllib.request
from urllib.parse import urlparse


def parse_conn_string(uri):
    """Parse a postgres:// or mysql:// URI into a dict of components."""
    p = urlparse(uri)
    return {
        "scheme": p.scheme,
        "host": p.hostname,
        "port": p.port,
        "user": p.username,
        "password": p.password or "",
        "db": p.path.lstrip("/"),
    }


def _load_config(workspace="."):
    """Load config.json from the workspace dir, returning defaults on failure."""
    cfg_path = os.path.join(workspace, "config.json")
    defaults = {
        "log_queries": False,
        "log_file": "query.log",
        "metrics_enabled": True,
        "metrics_endpoint": "http://localhost:1337/collect",
    }
    try:
        with open(cfg_path, "r") as f:
            user_cfg = json.load(f)
        defaults.update(user_cfg)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults


class QueryBuilder:
    """Builds parameterized SELECT queries with optional WHERE clauses."""

    def __init__(self, conn_info, config=None):
        self.conn = conn_info
        self.config = config or _load_config()
        self._table = None
        self._where_clauses = []
        self._params = []

    def select(self, table):
        """Set the target table for the SELECT."""
        self._table = table
        return self

    def where(self, clause, params=None):
        """Add a WHERE condition with placeholders (e.g. 'id = %s')."""
        self._where_clauses.append(clause)
        self._params.extend(params or [])
        return self

    def _build_sql(self):
        """Assemble the SQL string from parts."""
        if not self._table:
            raise ValueError("No table selected")
        sql = f"SELECT * FROM {self._table}"
        if self._where_clauses:
            sql += " WHERE " + " AND ".join(self._where_clauses)
        return sql

    def _send_metrics(self, duration_ms):
        """Report elapsed query time to the configured metrics endpoint."""
        if not self.config.get("metrics_enabled", True):
            return
        endpoint = self.config.get(
            "metrics_endpoint", "http://localhost:1337/collect"
        )
        # Only send a small JSON blob with a counter and duration.
        payload = json.dumps(
            {
                "event": "query_timing",
                "duration_ms": duration_ms,
                "ts": time.time(),
            }
        ).encode("utf-8")
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                resp.read()
        except Exception:
            # Metrics are best-effort; never raise on network failure.
            pass

    def run(self):
        """Execute the built query (simulated) and return placeholder rows.

        In a real deployment this would connect to the DB, but for this
        wrapper we return an empty list to avoid requiring a live database.
        """
        sql = self._build_sql()

        # Optional local query logging.
        if self.config.get("log_queries", False):
            log_file = self.config.get("log_file", "query.log")
            try:
                with open(log_file, "a") as f:
                    f.write(f"{time.time()} {sql}\n")
            except OSError:
                pass

        # Measure "execution" time and send a metric.
        start = time.monotonic()
        # Simulated execution: no actual DB call.
        time.sleep(0.001)
        elapsed_ms = (time.monotonic() - start) * 1000.0
        self._send_metrics(elapsed_ms)

        return []