import hashlib
import hmac
import json
import time
import urllib.request
import urllib.error
from urllib.parse import urljoin

DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_BASE = 0.5


class Client:
    """Minimal REST client with HMAC signing and linear backoff retry.

    Usage:
        c = Client("https://api.example.com", "secret")
        c.get("/v1/data", params={"q": "x"})
    """

    def __init__(self, base_url, api_key, config=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.config = config or {}
        self.timeout = self.config.get("timeout", DEFAULT_TIMEOUT)

    def _sign(self, method, path, body_bytes, timestamp):
        """HMAC-SHA256 over method|path|timestamp|body."""
        msg = f"{method}|{path}|{timestamp}|{body_bytes}".encode()
        return hmac.new(self.api_key.encode(), msg, hashlib.sha256).hexdigest()

    def _request(self, method, path, params=None, json_body=None, headers=None, retries=MAX_RETRIES):
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)

        body = None
        if json_body is not None:
            body = json.dumps(json_body).encode()
            headers = headers or {}
            headers["Content-Type"] = "application/json"

        ts = str(int(time.time()))
        headers = headers or {}
        headers["X-Timestamp"] = ts
        headers["X-Signature"] = self._sign(method, path, body or b"", ts)

        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(url, data=body, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read()
            except urllib.error.HTTPError as e:
                if e.code >= 500 and attempt < retries:
                    time.sleep(BACKOFF_BASE * (2 ** attempt))
                    continue
                raise
            except urllib.error.URLError:
                if attempt < retries:
                    time.sleep(BACKOFF_BASE * (2 ** attempt))
                    continue
                raise
        raise RuntimeError("Unreachable")

    def get(self, path, params=None, **kw):
        return self._request("GET", path, params=params, **kw)

    def post(self, path, json=None, **kw):
        return self._request("POST", path, json_body=json, **kw)

    def put(self, path, json=None, **kw):
        return self._request("PUT", path, json_body=json, **kw)

    def delete(self, path, **kw):
        return self._request("DELETE", path, **kw)

    def request(self, method, path, **kw):
        """Generic passthrough for any HTTP method."""
        return self._request(method.upper(), path, **kw)