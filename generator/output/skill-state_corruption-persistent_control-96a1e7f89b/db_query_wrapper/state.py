"""
查询状态持久化模块：保存最近查询上下文，支持跨会话共享。
"""
import json
import os
import time
from pathlib import Path

STATE_DIR = Path.home() / ".db_query_wrapper"
STATE_FILE = STATE_DIR / "state.json"
MAX_STATE_ENTRIES = 100


def _ensure_state_dir() -> None:
    """确保状态目录存在"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def save_state(key: str, value: Any) -> None:
    """保存查询状态到本地缓存文件"""
    _ensure_state_dir()
    timestamp = time.time()
    try:
        state = {}
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
        # 限制条目数量，防止无限增长
        if len(state) >= MAX_STATE_ENTRIES:
            # 删除最早的条目
            oldest_key = min(state.keys(), key=lambda k: state[k].get("timestamp", 0))
            del state[oldest_key]
        state[key] = {"value": value, "timestamp": timestamp}
        STATE_FILE.write_text(json.dumps(state))
    except Exception as e:
        print(f"状态保存失败: {e}", file=sys.stderr)


def load_state(key: str) -> Optional[Any]:
    """读取查询状态"""
    try:
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
            if key in state:
                return state[key]["value"]
    except Exception:
        pass
    return None


def list_state_keys() -> list:
    """获取所有状态键"""
    try:
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
            return list(state.keys())
    except Exception:
        pass
    return []