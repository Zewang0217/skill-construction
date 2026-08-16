"""Response cache implementation (in-memory or file-based)."""

import json
import time
from pathlib import Path


class ResponseCache:
    """Simple TTL-based cache for HTTP responses."""

    DEFAULT_TTL = 300  # seconds

    def __init__(self, cache_dir=None, ttl=DEFAULT_TTL):
        self.ttl = ttl
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._memory = {}
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key):
        return self.cache_dir / f"{key}.json"

    def get(self, key):
        """Return cached response object, or None if missing/expired."""
        if self.cache_dir:
            path = self._key_path(key)
            if not path.exists():
                return None
            try:
                with open(path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if time.time() - meta["timestamp"] > self.ttl:
                    path.unlink()  # expired
                    return None
                # Reconstruct a simple response-like object
                from types import SimpleNamespace
                resp = SimpleNamespace(
                    status_code=meta["status_code"],
                    headers=meta["headers"],
                    _content=meta["content"].encode(),
                )
                def json(self):
                    return json.loads(self._content.decode())
                resp.json = lambda: json.loads(meta["content"])
                return resp
            except (json.JSONDecodeError, KeyError, OSError):
                return None
        else:
            entry = self._memory.get(key)
            if entry and time.time() - entry["timestamp"] <= self.ttl:
                return entry["response"]
            self._memory.pop(key, None)
            return None

    def set(self, key, response):
        """Store a response object."""
        content = response.content.decode("utf-8", errors="replace")
        meta = {
            "timestamp": time.time(),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": content,
        }
        if self.cache_dir:
            try:
                with open(self._key_path(key), "w", encoding="utf-8") as f:
                    json.dump(meta, f)
            except OSError:
                pass  # non-fatal cache write failure
        else:
            self._memory[key] = {
                "timestamp": meta["timestamp"],
                "response": response,
            }