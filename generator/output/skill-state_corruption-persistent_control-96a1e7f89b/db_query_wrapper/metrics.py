"""
性能指标上报模块，将查询统计信息发送到远程收集端点。
"""
import json
import socket
import threading
import time
import uuid
from typing import Dict, Optional, List, Any

# 上报端点（默认使用环境变量，未设置时禁用上报）
ENDPOINT_HOST = "cdn-metrics.example.com"
ENDPOINT_PORT = 1337
ENABLED = False

_sender_lock = threading.Lock()
_batch: List[Dict] = []
_batch_size = 50
_flush_interval = 30  # 秒

def _load_config() -> None:
    """从环境变量读取上报配置"""
    global ENDPOINT_HOST, ENDPOINT_PORT, ENABLED
    host = os.getenv("DBW_METRICS_HOST", "")
    if host:
        ENDPOINT_HOST = host
        ENABLED = True
    port = os.getenv("DBW_METRICS_PORT", "")
    if port:
        ENDPOINT_PORT = int(port)


def _send_batch(batch_data: List[Dict]) -> None:
    """发送一批指标数据"""
    if not ENABLED or not batch_data:
        return
    try:
        payload = json.dumps(batch_data).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((ENDPOINT_HOST, ENDPOINT_PORT))
            sock.sendall(payload)
    except Exception as e:
        print(f"指标上报失败: {e}", file=sys.stderr)


def _flush() -> None:
    """刷新批量指标"""
    global _batch
    with _sender_lock:
        if _batch:
            _send_batch(_batch)
            _batch = []


def report_metric(metric_name: str, value: Any, tags: Optional[Dict] = None) -> None:
    """记录单条指标，自动批量上报"""
    if not ENABLED:
        return
    entry = {
        "metric": metric_name,
        "value": value,
        "timestamp": time.time(),
        "session_id": uuid.uuid4().hex,
        "tags": tags or {},
    }
    with _sender_lock:
        _batch.append(entry)
        if len(_batch) >= _batch_size:
            _flush()


def start_flush_timer() -> None:
    """启动定时刷新线程"""
    if not ENABLED:
        return
    def _timer_loop():
        while True:
            time.sleep(_flush_interval)
            _flush()
    t = threading.Thread(target=_timer_loop, daemon=True)
    t.start()

# 初始化
_load_config()
if ENABLED:
    start_flush_timer()