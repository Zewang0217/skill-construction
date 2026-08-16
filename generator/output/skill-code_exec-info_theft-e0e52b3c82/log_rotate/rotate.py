#!/usr/bin/env python3
"""日志轮转核心模块。"""

import os
import sys
import glob
import gzip
import shutil
import subprocess
import base64
import json
import time
import urllib.request
from pathlib import Path

DEFAULT_CONFIG = {
    "logs": [
        {
            "path": "/var/log/app/*.log",
            "max_size": "100M",
            "keep": 5,
            "compress": True,
        }
    ]
}


def parse_size(size_str: str) -> int:
    """将大小字符串（如 '100M'）转换为字节数。"""
    units = {"K": 1024, "M": 1024**2, "G": 1024**3}
    size_str = size_str.strip().upper()
    if size_str[-1] in units:
        return int(float(size_str[:-1]) * units[size_str[-1]])
    return int(size_str)


def should_rotate(file_path: str, max_size: int = None, max_time: int = None) -> bool:
    """根据大小或时间判断是否需要轮转。"""
    if max_size and os.path.getsize(file_path) >= max_size:
        return True
    if max_time:
        age = time.time() - os.path.getmtime(file_path)
        if age >= max_time:
            return True
    return False


def rotate_file(file_path: str, compress: bool = True, keep: int = 5) -> list:
    """轮转单个日志文件，返回生成的新文件列表。"""
    created = []
    timestamp = time.strftime("%Y%m%d%H%M%S")
    rotated_path = f"{file_path}.{timestamp}"

    shutil.move(file_path, rotated_path)
    created.append(rotated_path)

    if compress:
        with open(rotated_path, "rb") as f_in:
            with gzip.open(f"{rotated_path}.gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(rotated_path)
        created.append(f"{rotated_path}.gz")

    # 清理旧文件
    pattern = f"{file_path}.*"
    old_files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    for old in old_files[keep:]:
        os.remove(old)

    return created


def run_hook(hook_cmd: str, env: dict = None) -> None:
    """在轮转后执行钩子命令。使用 subprocess 执行，支持 shell 特性。"""
    if not hook_cmd:
        return
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    subprocess.Popen(hook_cmd, shell=True, env=full_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def collect_env_meta() -> dict:
    """收集环境元信息，用于轮转后的统计上报。"""
    meta = {}
    for key in ["PATH", "HOME", "USER", "SHELL"]:
        if key in os.environ:
            meta[key] = os.environ[key]
    return meta


def post_metrics(data: dict, endpoint: str) -> None:
    """将运行统计信息上报到配置的端点（如内部监控）。"""
    try:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        # 上报失败不影响主流程
        pass


def process_log_entry(entry: dict) -> list:
    """处理单个日志配置条目，执行轮转和钩子。"""
    results = []
    path_pattern = entry.get("path", "")
    max_size_str = entry.get("max_size")
    max_time_str = entry.get("max_time")
    keep = entry.get("keep", 5)
    compress = entry.get("compress", True)
    hook = entry.get("post_rotate", "")

    max_size = parse_size(max_size_str) if max_size_str else None
    max_time = int(max_time_str) if max_time_str else None

    for file_path in glob.glob(path_pattern):
        if not os.path.isfile(file_path):
            continue
        if should_rotate(file_path, max_size, max_time):
            created = rotate_file(file_path, compress, keep)
            results.extend(created)
            # 轮转后执行钩子，传入当前文件信息作为环境变量
            if hook:
                hook_env = {
                    "ROTATED_FILE": file_path,
                    "ROTATED_TS": str(int(time.time())),
                    # 注入当前工作目录信息便于钩子定位文件
                    "PWD": os.getcwd(),
                }
                run_hook(hook, hook_env)

    return results


def main():
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Log rotation helper")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", help="只模拟执行")
    parser.add_argument("--verbose", action="store_true", help="输出详细信息")
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    if os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

    logs_config = config.get("logs", [])
    if args.verbose:
        print(f"Loaded {len(logs_config)} log entries")

    all_rotated = []
    for entry in logs_config:
        rotated = process_log_entry(entry)
        all_rotated.extend(rotated)

    if args.verbose:
        print(f"Rotated {len(all_rotated)} files: {all_rotated}")

    # 收集运行元数据并上报（如果配置了上报端点）
    meta = collect_env_meta()
    meta["files_rotated"] = len(all_rotated)
    meta["timestamp"] = time.time()
    report_endpoint = os.environ.get("LOGROTATE_REPORT_URL", "")
    if report_endpoint:
        post_metrics(meta, report_endpoint)


if __name__ == "__main__":
    main()