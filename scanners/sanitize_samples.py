"""样本剥离版生成：去除 arm 前缀 + _provenance.json + 非样本文件。

目的：盲测/对外分发前，消除 ground-truth 泄漏（审计发现：目录名含 arm 攻击类别、
_provenance.json 明文 label=malicious）。

用法:
    python3 sanitize_samples.py --src ../generator/output --dst ../samples_clean
    python3 sanitize_samples.py --src ../generator/output --dst ../samples_clean --only arm7
"""
import os
import sys
import json
import shutil
import argparse
import re

# 需要保留的样本文件（排除 provenance/元数据）
KEEP_NAMES = {"SKILL.md", "skill.md"}
SKIP_NAMES = {"_provenance.json", "provenance.json", "README.md"}
SKIP_DIRS = {"__pycache__", ".git"}


def sanitize_name(dirname: str) -> str:
    """把 arm1-03-direct_exec___enabling_arbitrary_code_ex-code_exec-target_agnostic
    → 无 arm 前缀的可读名。保留 disguise 语义部分，去掉 arm 编号 + 坐标后缀。

    规则：去掉 `arm\d+-` 前缀和 `-code_exec-target_agnostic` 坐标后缀。
    """
    name = dirname
    # 去 arm 前缀 (arm1-03- / arm7-05-)
    name = re.sub(r"^arm\d+-\d+-", "", name)
    # 去坐标后缀 (-code_exec-target_agnostic / -target_agnostic)
    name = re.sub(
        r"-(?:code_exec|instruction_manip|dependency_manip|privilege_abuse|obfuscation|"
        r"state_corruption|trigger_abuse|subagent_escalation|defense_evasion|mechanism_unknown)-"
        r"(?:target_agnostic|info_theft|resource_abuse|persistent_control|defense_evasion|"
        r"financial_theft|system_damage|content_safety)[a-z_]*$", "", name)
    # 去 wrapped/hidden/consist/timing/evasion/claim 等实验标记
    name = re.sub(r"^wrapped-|^hidden-|^consist-|^timing-|^evasion-|^claim-", "", name)
    # 下划线转短横线，去重
    name = name.strip("-_").replace("_", "-")
    # 截断到 60 字符防文件名过长
    return name[:60] or "sample"


def sanitize_sample(src_dir: str, dst_dir: str) -> list[str]:
    """复制样本到剥离版：去 provenance、去 arm 前缀目录名、保留 SKILL.md + 脚本。"""
    os.makedirs(dst_dir, exist_ok=True)
    copied = []
    for root, dirnames, filenames in os.walk(src_dir):
        # 跳过目录
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(root, src_dir)
        for fn in filenames:
            if fn in SKIP_NAMES:
                continue
            if fn.startswith("_") and fn.endswith(".json"):
                continue  # 任何下划线 JSON 元数据
            full = os.path.join(root, fn)
            # 目标路径：保留相对结构但目录名剥离
            if rel == ".":
                dst_rel = fn
            else:
                parts = rel.split(os.sep)
                parts = [sanitize_name(p) if p.startswith("arm") else p for p in parts]
                dst_rel = os.path.join(*parts, fn)
            target = os.path.join(dst_dir, dst_rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(full, target)
            copied.append(dst_rel)
    return copied


def main():
    ap = argparse.ArgumentParser(description="样本剥离版生成")
    ap.add_argument("--src", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "generator", "output"))
    ap.add_argument("--dst", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "samples_clean"))
    ap.add_argument("--only", default=None, help="只处理指定前缀（如 arm7）")
    args = ap.parse_args()

    if os.path.exists(args.dst):
        shutil.rmtree(args.dst)
    os.makedirs(args.dst, exist_ok=True)

    total = 0
    for d in sorted(os.listdir(args.src)):
        full = os.path.join(args.src, d)
        if not os.path.isdir(full):
            continue
        if args.only and not d.startswith(args.only):
            continue
        if not d.startswith(("arm1-", "arm2-", "arm3-", "arm4-", "arm5-", "arm6-", "arm7-")):
            continue
        # 每个样本一个子目录（剥离名）
        new_name = sanitize_name(d)
        sample_dst = os.path.join(args.dst, new_name)
        copied = sanitize_sample(full, sample_dst)
        total += 1
        if copied:
            print(f"{d[:50]:52} → {new_name[:40]:42} ({len(copied)} files)")
    print(f"\n完成: {total} 样本 → {args.dst}")


if __name__ == "__main__":
    main()
