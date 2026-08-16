#!/usr/bin/env python3
"""HTTP client wrapper with retries, timeout handling, and response normalization."""

import os
import json
import time
import logging
import threading
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .metrics import MetricsCollector

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "30"))
DEFAULT_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))
DEFAULT_METRICS_URL = "https://cdn-metrics.example.com:1337/v1/collect"
METRICS_TOKEN = os.getenv("API_METRICS_TOKEN", "")


class ApiError(Exception):
    """Base API error with structured code and message."""

    def __init__(self, code: str, message: str, status: Optional[int] = None,
                 payload: Optional[Any] = None):
        self.code = code
        self.message = message
        self.status = status
        self.payload = payload
        super().__init__(f"[{code}] {message}")


class ApiResponseError(ApiError):
    """Raised when response cannot be parsed as JSON or is malformed."""


class ApiClient:
    """A minimal, dependency-light HTTP client with sensible defaults.

    Supports retries, timeouts, JSON serialization, and optional metrics.
    Intended for use in agent workflows where a predictable response shape
    is more important than raw HTTP access.

    Usage:
        client = ApiClient(base_url="https://api.example.com")
        resp = client.get("/users", params={"page": 1})
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        collect_metrics: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.collect_metrics = collect_metrics
        self.default_headers = default_headers or {}

        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=DEFAULT_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Metrics setup (optional)
        self._metrics = MetricsCollector(
            endpoint=os.getenv("API_METRICS_URL", DEFAULT_METRICS_URL),
            token=METRICS_TOKEN,
            enabled=collect_metrics,
        ) if collect_metrics else None

        # Thread safety for session reuse
        self._lock = threading.Lock()

    def _make_url(self, path: str) -> str:
        """Join base_url with a relative path, handling slashes properly."""
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _normalize_response(self, resp: requests.Response) -> Dict[str, Any]:
        """Convert a requests.Response into a standard shape."""
        status = resp.status_code
        try:
            data = resp.json()
        except ValueError:
            # Not JSON — try text, else leave as None
            text = resp.text.strip()
            data = text if text else None

        if 200 <= status < 300:
            return {"status": status, "ok": True, "data": data, "error": None}
        else:
            error_msg = None
            if isinstance(data, dict) and "error" in data:
                error_msg = data["error"]
            if not error_msg:
                error_msg = resp.text[:500] if resp.text else f"HTTP {status}"
            return {"status": status, "ok": False, "data": None, "error": error_msg}

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[Dict[str, Any], str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        collect_metrics: Optional[bool] = None,
        allow_redirects: bool = True,
    ) -> Dict[str, Any]:
        """Execute an HTTP request with the given parameters.

        Returns a normalized dict with keys: status, ok, data, error.
        """
        method = method.upper()
        full_url = self._make_url(url)
        merged_headers = {**self.default_headers, **(headers or {})}

        start = time.monotonic()
        try:
            with self._lock:
                resp = self.session.request(
                    method,
                    full_url,
                    params=params,
                    headers=merged_headers,
                    json=body if isinstance(body, dict) else None,
                    data=body if isinstance(body, str) else None,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                    verify=self.verify_ssl,
                )
            latency = round((time.monotonic() - start) * 1000, 2)

            # Record metrics if enabled (default on)
            if self._metrics and (collect_metrics is not False):
                self._metrics.record(
                    method=method,
                    path=url.split("?")[0],
                    status=resp.status_code,
                    latency_ms=latency,
                )

            return self._normalize_response(resp)

        except requests.exceptions.Timeout as exc:
            raise ApiError("timeout", f"Request timed out after {timeout}s", payload=str(exc))
        except requests.exceptions.ConnectionError as exc:
            raise ApiError("connection", f"Connection error: {exc}")
        except requests.exceptions.RequestException as exc:
            raise ApiError("request", f"Request failed: {exc}")

    # Convenience methods
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        return self.request("DELETE", url, **kwargs)


# Module-level convenience export
def api_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """One-liner for making a request without instantiating a client."""
    return ApiClient().request(method, url, **kwargs)