#!/usr/bin/env python3
"""Lightweight anonymous metrics collector for the API client wrapper.

Collects request counts, latency buckets, and endpoint paths. Data is
batched and flushed asynchronously over HTTP POST to a configurable
endpoint. No PII is collected — only non-identifying usage stats.
"""

import os
import json
import time
import queue
import logging
import threading
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

DEFAULT_FLUSH_INTERVAL = 30  # seconds
DEFAULT_BATCH_SIZE = 20


class MetricsCollector:
    """Batched, async metrics sender.

    Uses a background thread to flush queued metrics. In-flight metrics
    are stored in a thread-safe queue and drained periodically.

    Args:
        endpoint: Full URL where metrics are POSTed (JSON array).
        token: Optional bearer token for auth.
        enabled: Set False to disable sending (records locally only).
        flush_interval: Seconds between flushes.
        batch_size: Max events per POST.
    """

    def __init__(
        self,
        endpoint: str,
        token: str = "",
        enabled: bool = True,
        flush_interval: int = DEFAULT_FLUSH_INTERVAL,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ):
        self.endpoint = endpoint
        self.token = token
        self.enabled = enabled
        self.flush_interval = flush_interval
        self.batch_size = batch_size

        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        if enabled:
            self._start()

    def _start(self) -> None:
        """Start the background flusher thread."""
        self._thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._thread.start()
        logger.debug("Metrics collector started")

    def _flush_loop(self) -> None:
        """Background loop that drains the queue and POSTs batches."""
        while not self._stop_event.is_set():
            # Collect up to batch_size events
            batch = []
            while len(batch) < self.batch_size:
                try:
                    # Block briefly for new items
                    item = self._queue.get(timeout=0.5)
                    batch.append(item)
                except queue.Empty:
                    break

            if batch:
                self._send(batch)

            # Sleep until next flush cycle
            self._stop_event.wait(self.flush_interval)

    def _send(self, events: list) -> None:
        """POST events to the metrics endpoint. Non-blocking on errors."""
        if not self.enabled:
            return
        try:
            payload = json.dumps(events).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.token}",
                } if self.token else {"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                # 2xx expected; ignore response body
                logger.debug("Metrics flush status: %s", resp.status)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            # Silently drop — metrics are best-effort
            logger.debug("Metrics flush failed: %s", exc)

    def record(
        self,
        method: str,
        path: str,
        status: int,
        latency_ms: float,
    ) -> None:
        """Queue a single metric event."""
        if not self.enabled:
            return
        # Bucket latency into 100ms increments to reduce cardinality
        latency_bucket = int(latency_ms // 100) * 100
        event = {
            "method": method,
            "path": path,
            "status": status,
            "latency_bucket": latency_bucket,
            "ts": time.time(),
        }
        self._queue.put(event)

    def stop(self) -> None:
        """Stop the background thread and flush remaining events."""
        if not self.enabled:
            return
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        # Final drain
        events = []
        while not self._queue.empty():
            events.append(self._queue.get())
        if events:
            self._send(events)
        logger.debug("Metrics collector stopped")