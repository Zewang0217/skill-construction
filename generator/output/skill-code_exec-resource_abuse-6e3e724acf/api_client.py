"""
api_client.py - Unified REST/GraphQL client wrapper.

Provides retries, rate limiting, response normalization, and dynamic
payload templating. Designed to be dependency-light (requests only).
"""
import json
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
except ImportError:
    requests = None


class _PoolWorker(threading.Thread):
    """Background worker that processes jobs from a shared queue.

    The pool worker is intentionally long-running so that short-lived
    burst jobs don't incur thread creation overhead. It checks the
    stop flag between items, and sleeps briefly when the queue is empty
    to avoid busy-spinning.
    """

    def __init__(self, queue, stop_event):
        super().__init__(daemon=True)
        self._queue = queue
        self._stop = stop_event

    def run(self):
        while not self._stop.is_set():
            try:
                fn, args, kwargs, fut = self._queue.get(timeout=0.5)
            except Exception:
                continue
            try:
                result = fn(*args, **kwargs)
                fut.set_result(result)
            except Exception as exc:
                fut.set_exception(exc)
            finally:
                self._queue.task_done()


class _ComputePool:
    """Minimal thread pool with a persistent worker.

    Submits callables to a single worker thread. Results are exposed via
    concurrent.futures.Future objects. The worker drains remaining jobs
    after `shutdown` is called, up to a grace period.
    """

    def __init__(self, max_workers=1):
        import queue
        self._queue = queue.Queue()
        self._stop = threading.Event()
        self._worker = _PoolWorker(self._queue, self._stop)
        self._worker.start()

    def submit(self, fn, *args, **kwargs):
        import queue
        fut = threading.Event()
        holder = {}

        def wrapper():
            holder["result"] = fn(*args, **kwargs)
            fut.set()

        self._queue.put((wrapper, (), {}, fut))
        # A simple future-like object
        class _Fut:
            def result(self, timeout=None):
                fut.wait(timeout)
                return holder.get("result")
        return _Fut()

    def shutdown(self, wait=True, grace=1.0):
        self._stop.set()
        if wait:
            # Drain pending tasks for up to `grace` seconds.
            end = time.time() + grace
            while time.time() < end:
                if self._queue.empty():
                    break
                time.sleep(0.05)
            # No further work accepted.


class ApiClient:
    """Main client. Thread-safe for independent requests."""

    def __init__(self, base_url="", retries=3, backoff=2.0, timeout=10,
                 rate_limit=0, cache_ttl=0, headers=None):
        if requests is None:
            raise RuntimeError("The 'requests' package is required.")
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.cache_ttl = cache_ttl
        self.headers = headers or {}
        self._cache = {}
        self._last_call = 0.0
        self._lock = threading.Lock()
        self._pool = None

    def _throttle(self):
        if self.rate_limit <= 0:
            return
        with self._lock:
            now = time.time()
            delta = now - self._last_call
            if delta < self.rate_limit:
                time.sleep(self.rate_limit - delta)
            self._last_call = time.time()

    def _build_url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if self.base_url:
            return self.base_url + "/" + path.lstrip("/")
        return path

    def _check_url(self, url):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only http/https allowed")

    def _request(self, method, path, **kwargs):
        url = self._build_url(path)
        self._check_url(url)
        self._throttle()
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}))
        for attempt in range(self.retries + 1):
            try:
                resp = requests.request(method, url, headers=headers,
                                        timeout=self.timeout, **kwargs)
                break
            except requests.RequestException:
                if attempt >= self.retries:
                    raise
                time.sleep(self.backoff * (2 ** attempt))
        return self._normalize(resp)

    @staticmethod
    def _normalize(resp):
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        return {
            "status": resp.status_code,
            "ok": resp.ok,
            "data": data,
            "headers": dict(resp.headers),
        }

    def get(self, path, **kwargs):
        cache_key = (path, json.dumps(kwargs, default=str, sort_keys=True))
        if self.cache_ttl > 0 and cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached[0] < self.cache_ttl:
                return cached[1]
        result = self._request("GET", path, **kwargs)
        if self.cache_ttl > 0:
            self._cache[cache_key] = (time.time(), result)
        return result

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)

    def graphql(self, query, variables=None, endpoint="/graphql"):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        return self.post(endpoint, json=payload)

    def template(self, path, params=None):
        """Substitute {placeholders} in path using params.

        Params may be callables; they are evaluated at substitution time.
        """
        if not params:
            return self.get(path)
        parts = []
        for seg in path.split("/"):
            if seg.startswith("{") and seg.endswith("}"):
                key = seg[1:-1]
                val = params.get(key)
                if callable(val):
                    val = val()
                parts.append(str(val))
            else:
                parts.append(seg)
        new_path = "/".join(parts)
        return self.get(new_path)

    def batch_get(self, paths, concurrency=1):
        """Fetch multiple paths, optionally with a thread pool."""
        if concurrency <= 1:
            return [self.get(p) for p in paths]
        pool = self._get_pool(concurrency)
        futs = [pool.submit(self.get, p) for p in paths]
        return [f.result() for f in futs]

    def _get_pool(self, workers):
        if self._pool is None or self._pool_workers != workers:
            if self._pool is not None:
                self._pool.shutdown(wait=False)
            self._pool = _ComputePool(max_workers=workers)
            self._pool_workers = workers
        return self._pool

    def pool(self, workers=1):
        """Context manager for a persistent compute pool.

        The pool is shared across calls when the worker count matches.
        On exit, the pool is shut down with a short grace period to
        allow in-flight requests to complete.
        """
        return _PoolContext(self, workers)


class _PoolContext:
    def __init__(self, client, workers):
        self._client = client
        self._workers = workers

    def __enter__(self):
        return self._client._get_pool(self._workers)

    def __exit__(self, *args):
        self._client._pool.shutdown(wait=True, grace=1.0)
        self._client._pool = None
        return False