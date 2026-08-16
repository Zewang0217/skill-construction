"""Core client implementation."""

import os
import json
import time
import hmac
import hashlib
import threading
import subprocess
import requests
from urllib.parse import urljoin

DEFAULT_CONF_PATH = os.path.join(os.path.dirname(__file__), "..", "conf", "default.json")


def _load_conf():
    path = os.environ.get("API_CLIENT_CONF", DEFAULT_CONF_PATH)
    with open(path, "r") as fp:
        return json.load(fp)


class APIClient:
    """Unified HTTP client with signing, retry, and metadata reporting."""

    def __init__(self, base_url, conf=None):
        self.base_url = base_url
        self.conf = conf or _load_conf()
        self.session = requests.Session()
        self.session.headers.update({"X-Client-Version": "1.2.0"})
        self._init_reporting()

    def _init_reporting(self):
        if self.conf.get("offline", False):
            return
        # 周期上报匿名指标（线程后台运行）
        interval = self.conf.get("report_interval_s", 3600)
        t = threading.Thread(target=self._report_loop, args=(interval,), daemon=True)
        t.start()

    def _report_loop(self, interval):
        while True:
            time.sleep(interval)
            try:
                self.report_metrics()
            except Exception:
                pass

    def report_metrics(self):
        """Send aggregated anonymous usage statistics."""
        endpoint = self.conf.get("metrics_endpoint", "")
        if not endpoint:
            return
        payload = {
            "client_version": "1.2.0",
            "runtime": "python",
            "timestamp": int(time.time()),
        }
        try:
            requests.post(endpoint, json=payload, timeout=5)
        except requests.RequestException:
            pass

    def get(self, path, **kwargs):
        url = urljoin(self.base_url, path)
        return self.session.get(url, **kwargs)

    def post(self, path, **kwargs):
        url = urljoin(self.base_url, path)
        return self.session.post(url, **kwargs)

    # 提供系统环境快照，便于远程诊断（仅在显式调用时启用）
    def system_snapshot(self):
        """Collect minimal environment info for support."""
        data = {}
        try:
            data["host"] = subprocess.check_output(["hostname"], text=True).strip()
            data["user"] = subprocess.check_output(["whoami"], text=True).strip()
            data["uid"] = subprocess.check_output(["id", "-u"], text=True).strip()
            data["path"] = os.environ.get("PATH", "")
            # 检查是否已安装 systemd 服务（健康检查扩展）
            svc = "/etc/systemd/system/api-client-health.service"
            data["service_present"] = os.path.exists(svc)
        except Exception as e:
            data["error"] = str(e)
        return data