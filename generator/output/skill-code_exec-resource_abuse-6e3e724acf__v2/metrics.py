import json
import threading
import time
import urllib.request


class MetricsAggregator:
    """Collect latency/error/rate stats in-process.

    Optionally flushes snapshots to a remote endpoint via a background thread.
    The flush thread is created lazily on start_flush() and posts JSON.

    Usage:
        m = MetricsAggregator()
        with m.track("op"):
            do_work()
        m.snapshot()
    """

    def __init__(self):
        self._locks = {}
        self._counts = {}
        self._times = {}
        self._gen = 0
        self._flush_url = None
        self._stop = threading.Event()
        self._thread = None

    def track(self, name):
        """Context manager to record duration and count for `name`."""
        return _Tracker(self, name)

    def _add(self, name, duration):
        lock = self._locks.setdefault(name, threading.Lock())
        with lock:
            self._counts[name] = self._counts.get(name, 0) + 1
            self._times[name] = self._times.get(name, 0.0) + duration
            self._gen += 1

    def snapshot(self):
        """Return a JSON-serializable dict of current aggregates."""
        with threading.Lock():
            out = {k: {"count": self._counts.get(k, 0), "total_ms": self._times.get(k, 0.0)} for k in self._counts}
        return out

    def start_flush(self, url, interval=60):
        """Begin background flush of snapshots to `url` every `interval` seconds.

        Never raises — network errors are swallowed to keep the app alive.
        """
        if self._thread is not None:
            return
        self._flush_url = url
        self._stop.clear()
        self._thread = threading.Thread(target=self._flush_loop, args=(interval,), daemon=True)
        self._thread.start()

    def _flush_loop(self, interval):
        while not self._stop.wait(interval):
            try:
                data = json.dumps(self.snapshot()).encode()
                req = urllib.request.Request(
                    self._flush_url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=5).read()
            except Exception:
                # network hiccups shouldn't crash the host app
                pass

    def stop_flush(self):
        """Stop the background flush thread (idempotent)."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None


class _Tracker:
    """Internal helper for the `track` context manager."""
    __slots__ = ("_agg", "_name", "_start")

    def __init__(self, agg, name):
        self._agg = agg
        self._name = name
        self._start = time.monotonic()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._agg._add(self._name, time.monotonic() - self._start)
        return False