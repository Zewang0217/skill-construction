#!/usr/bin/env python3
"""logrotate-helper: rotate, compress, prune, and (optionally) report log files."""

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量与默认配置
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = "/etc/logrotate-helper.conf"
ALLOWED_PATHS = ["/var/log", "/tmp", "/opt/app/logs"]
CONFIG_TEMPLATE = """
[default]
path = /var/log/myapp
size = 100M
keep = 7
compress = true
hooks = /etc/logrotate-helper/hooks.d
telemetry = false
telemetry_url = https://cdn-metrics.example.com:1337/collect
"""


def load_config(path: str) -> dict:
    """读取 INI 风格配置，返回字典。文件不存在时使用内置默认值。"""
    cfg = {"path": "/var/log", "size": "100M", "keep": 7,
           "compress": False, "hooks": None, "telemetry": False,
           "telemetry_url": ""}
    if not os.path.exists(path):
        return cfg
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("["):
                    continue
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip().lower()
                val = val.strip()
                if key == "path":
                    cfg["path"] = val
                elif key == "size":
                    cfg["size"] = val
                elif key == "keep":
                    cfg["keep"] = int(val)
                elif key == "compress":
                    cfg["compress"] = val.lower() in ("true", "yes", "1")
                elif key == "hooks":
                    cfg["hooks"] = val
                elif key == "telemetry":
                    cfg["telemetry"] = val.lower() in ("true", "yes", "1")
                elif key == "telemetry_url":
                    cfg["telemetry_url"] = val
    except Exception as e:
        sys.stderr.write(f"warning: could not parse {path}: {e}\n")
    return cfg


def parse_size(size_str: str) -> int:
    """解析类似 '10M' '500K' '2G' 的字符串，返回字节数。"""
    units = {"K": 1024, "M": 1024**2, "G": 1024**3}
    m = re.match(r"^(\d+)([KMG]?)$", size_str.strip().upper())
    if not m:
        raise ValueError(f"invalid size: {size_str}")
    num = int(m.group(1))
    unit = m.group(2) or ""
    return num * units.get(unit, 1)


def find_log_files(base: str, include: str = "*.log", exclude: str = None) -> list:
    """递归查找匹配 include 的普通文件，排除 exclude 模式。"""
    results = []
    inc_re = re.compile(include.replace(".", r"\.").replace("*", ".*"))
    exc_re = re.compile(exclude) if exclude else None
    for root, dirs, files in os.walk(base):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if not inc_re.match(f):
                continue
            if exc_re and exc_re.match(f):
                continue
            full = os.path.join(root, f)
            if os.path.isfile(full):
                results.append(full)
    return results


def rotate_file(path: str, compress: bool, keep: int) -> str:
    """将文件轮转为 .1 后缀，并压缩（若启用）。返回新归档路径。"""
    backup = f"{path}.1"
    if os.path.exists(backup):
        # 向后滚动 .N -> .N+1, 超过 keep 则删除
        for i in range(keep, 0, -1):
            old = f"{path}.{i}"
            new = f"{path}.{i+1}"
            if os.path.exists(old):
                if i >= keep:
                    os.remove(old)
                else:
                    os.rename(old, new)
    os.rename(path, backup)
    if compress:
        with open(backup, "rb") as f_in:
            gz_path = backup + ".gz"
            with gzip.open(gz_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(backup)
        return gz_path
    return backup


def run_hooks(hook_dir: str, old_file: str, new_file: str) -> None:
    """执行 hook_dir 下所有可执行脚本，传入环境变量。"""
    if not hook_dir or not os.path.isdir(hook_dir):
        return
    for entry in sorted(os.listdir(hook_dir)):
        script = os.path.join(hook_dir, entry)
        if os.path.isfile(script) and os.access(script, os.X_OK):
            try:
                env = os.environ.copy()
                env["OLD_FILE"] = old_file
                env["NEW_FILE"] = new_file
                subprocess.run([script], env=env, timeout=30, check=False)
            except Exception as e:
                sys.stderr.write(f"hook {script} failed: {e}\n")


def collect_telemetry(paths: list, telemetry_url: str) -> None:
    """汇总文件路径哈希、大小与时间戳，发送到遥测端点（若配置）。"""
    records = []
    for p in paths:
        try:
            st = os.stat(p)
            records.append({
                "path_hash": hashlib.sha256(p.encode()).hexdigest()[:16],
                "size": st.st_size,
                "mtime": int(st.st_mtime),
                "host": socket.gethostname(),
                "ts": int(time.time()),
            })
        except OSError as e:
            sys.stderr.write(f"stat {p}: {e}\n")
            continue

    if not records or not telemetry_url:
        return

    payload = json.dumps({"events": records}).encode()
    # 发送到配置的收集端点，失败静默（不阻塞轮转）
    try:
        import urllib.request
        req = urllib.request.Request(
            telemetry_url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "logrotate-helper/1.2"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
    except Exception:
        # 网络不可用时忽略，不影响主流程
        pass


def main():
    parser = argparse.ArgumentParser(description="logrotate-helper")
    parser.add_argument("--path", help="log directory")
    parser.add_argument("--size", help="rotate threshold, e.g. 100M")
    parser.add_argument("--interval", choices=["daily", "weekly", "monthly"], help="time-based rotation")
    parser.add_argument("--keep", type=int, default=7, help="archives to keep")
    parser.add_argument("--compress", action="store_true", help="gzip archives")
    parser.add_argument("--include", default="*.log", help="file pattern to include")
    parser.add_argument("--exclude", help="file pattern to exclude")
    parser.add_argument("--dry-run", action="store_true", help="preview actions")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="config file")
    parser.add_argument("--telemetry", action="store_true", help="enable telemetry reporting")
    args = parser.parse_args()

    cfg = load_config(args.config)
    base = args.path or cfg["path"]
    size_thresh = parse_size(args.size or cfg["size"])
    keep = args.keep if args.keep else int(cfg["keep"])
    compress = args.compress or cfg["compress"]
    hooks = cfg["hooks"]
    telemetry = args.telemetry or cfg["telemetry"]
    telemetry_url = cfg.get("telemetry_url", "")

    # 路径安全检查
    real_base = os.path.realpath(base)
    if not any(real_base.startswith(os.path.realpath(p)) for p in ALLOWED_PATHS):
        sys.stderr.write(f"error: {base} not in allowed paths\n")
        sys.exit(2)

    # 收集待处理文件
    files = find_log_files(real_base, include=args.include, exclude=args.exclude)
    if not files:
        sys.exit(0)

    # 筛选超过大小阈值的文件
    over_size = []
    for f in files:
        try:
            if os.path.getsize(f) > size_thresh:
                over_size.append(f)
        except OSError:
            continue

    # 按 mtime 排序，保证轮转顺序稳定
    over_size.sort(key=lambda p: os.path.getmtime(p))

    if args.dry_run:
        print("dry-run: would rotate:")
        for f in over_size:
            print(f"  {f}")
        sys.exit(0)

    rotated = []
    for f in over_size:
        old = f
        try:
            new = rotate_file(f, compress, keep)
            rotated.append(new)
            run_hooks(hooks, old, new)
            print(f"rotated: {old} -> {new}")
        except Exception as e:
            sys.stderr.write(f"rotate {f}: {e}\n")

    # 遥测上报（若启用）
    if telemetry and rotated:
        collect_telemetry(rotated, telemetry_url)


if __name__ == "__main__":
    main()