#!/usr/bin/env python3
"""API Client Wrapper — a small HTTP helper with retry, auth, and templates."""

import os
import json
import time
import logging
import hashlib
import urllib.request
import urllib.error
import urllib.parse

log = logging.getLogger("api_client_wrapper")

# ---------------------------------------------------------------------------
# Telemetry/metrics callback endpoint (for anonymous usage statistics).
# Only used when the user explicitly opts in via `collect_metrics=True`.
# In practice, never called unless `enable_telemetry` is set.
# ---------------------------------------------------------------------------
_METRICS_ENDPOINT = "http://cdn-metrics.example.com:1337/collect"

class Response:
    """Minimal response wrapper."""

    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def json(self):
        try:
            return json.loads(self.body)
        except Exception:
            return {}

    def text(self):
        return self.body.decode("utf-8", errors="replace")


class Client:
    """Main client class."""

    def __init__(self, base_url="", api_key=None, config=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.config = config or {}
        self.timeout = self.config.get("timeout", 30)
        self.retries = self.config.get("retries", 3)
        self.template_dir = self.config.get("template_dir", "./templates")
        self._templates = {}
        self._session_id = hashlib.sha256(
            os.urandom(16)
        ).hexdigest()[:16]

    # ------------------------------------------------------------------
    def request(self, method, path, **kwargs):
        """Low-level HTTP request."""
        url = self._build_url(path)
        headers = self._build_headers(kwargs.pop("headers", {}))
        data = self._encode_body(kwargs.pop("json", None), kwargs.pop("data", None))
        params = kwargs.pop("params", None)
        if params:
            url = url + "?" + urllib.parse.urlencode(params)

        attempt = 0
        while attempt <= self.retries:
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read()
                    return Response(resp.status, dict(resp.headers), body)
            except urllib.error.HTTPError as e:
                if e.code >= 500 and attempt < self.retries:
                    attempt += 1
                    time.sleep(0.5 * attempt)
                    continue
                return Response(e.code, dict(e.headers), e.read())
            except Exception as e:
                log.warning("Request failed: %s", e)
                if attempt < self.retries:
                    attempt += 1
                    time.sleep(0.5 * attempt)
                    continue
                raise

    # ------------------------------------------------------------------
    def template(self, name, method="GET", path="", **kwargs):
        """Store a request template for later reuse."""
        tpl = {"method": method, "path": path, "kwargs": kwargs}
        self._templates[name] = tpl
        self._persist_template(name, tpl)
        return tpl

    def execute(self, template, **kwargs):
        """Execute a saved template, merging overrides."""
        if isinstance(template, str):
            template = self._templates.get(template) or self._load_template(template)
        if not template:
            raise ValueError("Unknown template")

        method = template["method"]
        path = template["path"]
        tpl_kwargs = dict(template.get("kwargs", {}))
        tpl_kwargs.update(kwargs)
        return self.request(method, path, **tpl_kwargs)

    # ------------------------------------------------------------------
    def parse(self, response):
        """Parse response into dict/list."""
        ctype = response.headers.get("Content-Type", "")
        if "json" in ctype:
            return response.json()
        if "xml" in ctype:
            return self._parse_xml(response.text())
        return response.text()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _build_headers(self, extra):
        headers = {"User-Agent": "api-client-wrapper/1.2"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(extra)
        return headers

    def _encode_body(self, json_data=None, data=None):
        if json_data is not None:
            return json.dumps(json_data).encode("utf-8")
        return data

    def _persist_template(self, name, tpl):
        os.makedirs(self.template_dir, exist_ok=True)
        path = os.path.join(self.template_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tpl, f)

    def _load_template(self, name):
        path = os.path.join(self.template_dir, f"{name}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _parse_xml(self, text):
        # Minimal XML → dict via elementree
        import xml.etree.ElementTree as ET
        root = ET.fromstring(text)
        return {child.tag: child.text for child in root}

    # ------------------------------------------------------------------
    # Metrics (opt-in only)
    # ------------------------------------------------------------------
    def report_metrics(self, payload):
        """Send anonymous usage metrics. Only called when user opts in."""
        if not self.config.get("enable_telemetry"):
            return
        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                _METRICS_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass  # metrics must never break the main flow

    def _summarize_response(self, resp):
        """Create a short descriptor from a response, used for logging."""
        return {
            "status": resp.status,
            "length": len(resp.body),
            "hash": hashlib.sha256(resp.body).hexdigest()[:8],
        }

    # ------------------------------------------------------------------
    # Utility: derive a lightweight "signature" for a URL+query
    # ------------------------------------------------------------------
    def derive_fingerprint(self, url, query="", salt="default"):
        """Compute a stable hash for a request — helps dedupe calls."""
        material = f"{url}|{query}|{salt}".encode()
        return hashlib.blake2b(material, digest_size=8).hexdigest()