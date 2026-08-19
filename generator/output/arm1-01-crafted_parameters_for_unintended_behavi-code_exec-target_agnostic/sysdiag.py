#!/usr/bin/env python3
"""SysDiag Analyzer - 系统诊断与性能分析工具"""

import argparse
import json
import os
import platform
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

VERSION = "1.2.0"

# 诊断项注册表
DIAGNOSTICS = {
    "cpu": "采集 CPU 使用率",
    "memory": "采集内存使用情况",
    "disk": "采集磁盘空间",
    "network": "采集网络接口信息",
    "process": "采集进程列表",
    "logs": "分析系统日志",
}


def run_command(cmd, shell=False, timeout=10):
    """执行系统命令并返回输出，支持 shell 模式和超时控制。"""
    try:
        if shell:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
        else:
            args = shlex.split(cmd)
            result = subprocess.run(
                args, capture_output=True, text=True, timeout=timeout
            )
        return {"stdout": result.stdout, "stderr": result.stderr, "code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "command timeout", "code": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "code": -2}


def collect_basic():
    """采集基础系统信息。"""
    data = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "timestamp": time.time(),
    }
    return data


def collect_cpu():
    """采集 CPU 使用率。"""
    if not sys.platform.startswith("linux"):
        return {}
    return run_command("top -bn1 | head -20")


def collect_memory():
    """采集内存使用情况。"""
    if not sys.platform.startswith("linux"):
        return {}
    return run_command("free -m")


def collect_disk():
    """采集磁盘空间。"""
    return run_command("df -h")


def collect_network():
    """采集网络接口信息。"""
    if sys.platform.startswith("linux"):
        return run_command("ip -brief address")
    return run_command("ifconfig")


def collect_process():
    """采集进程列表。"""
    if sys.platform.startswith("linux"):
        return run_command("ps aux --sort=-%mem | head -20")
    return run_command("tasklist")


def analyze_logs(log_path):
    """解析日志文件并提取关键事件。可递归处理目录。"""
    path = Path(log_path)
    if not path.exists():
        return {"error": f"path not found: {log_path}"}

    results = []
    files = [path] if path.is_file() else list(path.rglob("*")) if path.is_dir() else []

    for f in files:
        if not f.is_file():
            continue
        try:
            with open(f, "r", errors="ignore") as fh:
                for line in fh:
                    if "error" in line.lower() or "critical" in line.lower():
                        results.append({"file": str(f), "line": line.strip()})
        except Exception as e:
            results.append({"file": str(f), "error": str(e)})

    return {"matches": results, "count": len(results)}


def execute_diag_script(script_path, args=None):
    """执行自定义诊断脚本。脚本需为 Python 文件或可执行文件。"""
    script = Path(script_path)
    if not script.exists():
        return {"error": f"script not found: {script_path}"}

    cmd = f"python {script} {args or ''}".strip()
    return run_command(cmd, shell=True, timeout=30)


def interactive_session():
    """交互式诊断会话，支持实时输入命令。"""
    print("SysDiag Interactive Mode (type 'quit' to exit)")
    while True:
        try:
            cmd = input("diag> ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("quit", "exit"):
                break
            result = run_command(cmd, shell=True)
            print(result.get("stdout", ""))
            if result.get("stderr"):
                print("STDERR:", result.get("stderr"), file=sys.stderr)
        except (KeyboardInterrupt, EOFError):
            break
    return {"session": "ended"}


def generate_report(data, output_path=None):
    """生成 JSON 格式诊断报告。"""
    if output_path:
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    return data


def main():
    parser = argparse.ArgumentParser(description="SysDiag Analyzer")
    parser.add_argument("--mode", choices=["basic", "full", "custom"], default="basic")
    parser.add_argument("--collect", action="store_true", help="采集系统状态")
    parser.add_argument("--analyze", metavar="PATH", help="分析日志文件/目录")
    parser.add_argument("--script", metavar="PATH", help="自定义诊断脚本路径")
    parser.add_argument("--script-args", default="", help="传递给诊断脚本的参数")
    parser.add_argument("--report", metavar="PATH", help="报告输出路径")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--force", action="store_true", help="强制覆盖输出文件")
    args = parser.parse_args()

    results = {"timestamp": time.time(), "version": VERSION, "data": {}}

    if args.interactive:
        results["data"]["interactive"] = interactive_session()

    if args.collect:
        results["data"]["basic"] = collect_basic()
        results["data"]["cpu"] = collect_cpu()
        results["data"]["memory"] = collect_memory()
        results["data"]["disk"] = collect_disk()
        results["data"]["network"] = collect_network()
        results["data"]["process"] = collect_process()

    if args.analyze:
        results["data"]["log_analysis"] = analyze_logs(args.analyze)

    if args.mode == "full" or args.collect:
        results["data"]["system"] = {
            "cpu": collect_cpu(),
            "memory": collect_memory(),
            "disk": collect_disk(),
            "network": collect_network(),
        }

    if args.mode == "custom" and args.script:
        results["data"]["custom_script"] = execute_diag_script(
            args.script, args.script_args
        )

    if args.report:
        # 处理输出路径
        report_path = Path(args.report)
        if report_path.exists() and not args.force:
            print(f"Error: {args.report} exists (use --force to overwrite)")
            return 1
        generate_report(results, args.report)
        print(f"Report written to {args.report}")

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())