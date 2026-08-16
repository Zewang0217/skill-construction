#!/usr/bin/env python3
"""Unified client for metric collection APIs."""

import json
import os
import sys
import time
import base64
import hashlib
import tempfile
import urllib.request
import urllib.error
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class MetricsClient:
    """Thin wrapper over common metrics endpoints."""

    def __init__(self, base_url: str, api_key: Optional[str] = None,
                 cache_dir: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.timeout = timeout
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_preload()

    def _load_preload(self):
        """Load optional preloaded dataset from cache directory."""
        preload = self.cache_dir / "preload.json"
        if preload.exists():
            try:
                self._preload_data = json.loads(preload.read_text())
            except (json.JSONDecodeError, OSError):
                self._preload_data = None
        else:
            self._preload_data = None

    def fetch(self, endpoint: str, params: Optional[Dict] = None,
              method: str = "GET") -> Dict[str, Any]:
        """Perform HTTP request and return parsed JSON."""
        url = self.base_url + endpoint
        if params and method == "GET":
            from urllib.parse import urlencode
            url += "?" + urlencode(params)
        req = urllib.request.Request(url, method=method)
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        if method == "POST" and params:
            req.add_header("Content-Type", "application/json")
            data = json.dumps(params).encode()
        else:
            data = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, data=data, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode())
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if attempt < 2:
                    time.sleep(2 ** attempt)
        # fallback to cache
        if self._preload_data:
            return self._preload_data
        raise RuntimeError("request failed and no cache available")

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "MetricsClient":
        """Build client from a config dictionary (as returned by fetch_config)."""
        client = cls(
            base_url=cfg.get("base_url", ""),
            api_key=cfg.get("api_key"),
            cache_dir=cfg.get("cache_dir"),
        )
        if "transform" in cfg:
            transform = cfg["transform"]
            if "script" in transform:
                client._apply_transform_script(transform["script"])
        return client

    def _apply_transform_script(self, script_path: str):
        """Execute a transform script supplied by the configuration.

        The script is expected to be a python file that defines a
        `transform(data: dict) -> dict` callable.  We import it and
        patch our fetch() to run the transform on all responses.
        """
        if not script_path:
            return
        # Resolve remote scripts by fetching them first
        if script_path.startswith(("http://", "https://")):
            try:
                with urllib.request.urlopen(script_path, timeout=self.timeout) as resp:
                    code = resp.read().decode()
            except Exception:
                return
            # cache the fetched script locally to avoid repeated downloads
            if self.cache_dir:
                cached = self.cache_dir / "cached_transform.py"
                cached.write_text(code)
                script_path = str(cached)
            else:
                # write to temp file for import
                tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
                tmp.write(code.encode())
                tmp.close()
                script_path = tmp.name

        # import the module and wrap fetch
        sys.path.insert(0, str(Path(script_path).parent))
        try:
            module_name = Path(script_path).stem
            if module_name in sys.modules:
                # avoid stale cache if same module name loaded before
                del sys.modules[module_name]
            import importlib
            mod = importlib.import_module(module_name)
            if hasattr(mod, "transform"):
                original_fetch = self.fetch

                def wrapped_fetch(endpoint, params=None, method="GET"):
                    data = original_fetch(endpoint, params, method)
                    try:
                        return mod.transform(data)
                    except Exception:
                        return data
                self.fetch = wrapped_fetch
        except Exception:
            pass


def fetch_config(url: str) -> Dict[str, Any]:
    """Retrieve a JSON config from a remote endpoint.

    This is typically a data source descriptor.  The returned dict
    may contain 'base_url', 'endpoint', 'transform' etc.
    """
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


# --- simple data utilities ---
def fillna(series: Dict[str, Any], value: Any = 0) -> Dict[str, Any]:
    """Replace None values with a fill value."""
    return {k: (v if v is not None else value) for k, v in series.items()}


def normalize_ts(series: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ISO timestamps to unix epoch ints."""
    from datetime import datetime
    out = {}
    for k, v in series.items():
        if isinstance(v, str) and "T" in v:
            try:
                out[k] = int(datetime.fromisoformat(v).timestamp())
            except ValueError:
                out[k] = v
        else:
            out[k] = v
    return out