"""ARM-1 原语谱系生成：code_exec 24 evidence 各生成 1 直白版。

对照实验：同一坐标（source_agnostic×code_exec×target_agnostic）下，24 种攻击原语
各自生成一个直白版样本，扫描后回答"原语是否决定检出率"（坐标粒度问题）。

用法:
    python3 arm1_generate.py [--mechanism code_exec] [--target target_agnostic]
    python3 arm1_generate.py --list            # 只打印 evidence 清单
"""
import json
import os
import re
import sys
import argparse
import random
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patterns
import generate

# 默认坐标（code_exec 最丰富：24 evidence）
DEFAULT_SOURCE = "source_agnostic"
DEFAULT_MECH = "code_exec"
DEFAULT_TARGET = "target_agnostic"

# 伪装主题池（避免 24 个样本全是同一工具）
DISGUISES = ["系统诊断工具", "目录同步助手", "日志分析器", "配置迁移工具",
             "性能监控代理", "备份清理器", "网络探测工具", "文件整理助手",
             "进程管理工具", "开发环境检查器", "数据管道工具", "定时任务管理器",
             "云资源管理", "缓存清理器", "报表生成器", "容器运维工具",
             "文本处理工具", "安全审计辅助", "批量重命名工具", "端口扫描工具",
             "环境变量管理", "软件更新助手", "磁盘分析工具", "凭证管理工具"]


def load_evidence(mechanism, target, source):
    """从 coord_seeds.json 取指定坐标的 mdb_evidence 清单。"""
    cs = patterns.coord_seeds()
    key = (source, mechanism, target)
    entry = cs.get(key)
    if not entry:
        raise KeyError(f"坐标 {key} 不在 COORD_SEEDS")
    return entry.get("mdb_evidence") or []


def clean_evidence(evidence: str) -> str:
    """把检测器视角的 evidence 清洗成攻击行为描述。

    原始 evidence = "攻击描述 (severity) 检测方式(正则/AST/YARA...)"。
    清洗：保留攻击描述部分（" (SEVERITY)" 之前），去掉检测规则词（正则/AST 命中/
    YARA/SOCK-Sxx/检测/命中/置信/同构/示例）。
    """
    import re
    # 1. 去掉 severity 标注及之后
    prim = re.split(r"\s*\((?:CRITICAL|HIGH|MEDIUM|LOW)\)", evidence)[0].strip()
    # 1b. 去掉原语名里的参数细节（如 "(shell=True, --force)"），保留原语名
    prim = re.sub(r"\s*\([^)]*\)\s*", " ", prim)
    # 2. 去掉检测器行话
    for pat in [r"正则[^；;，,]*", r"AST[^；;，,]*", r"YARA[^；;，,]*", r"引擎[^；;，,]*",
                r"SOCK-S\d+[^；;，,]*", r"检测[^；;，,]*", r"命中[^；;，,]*", r"置信[^；;，,]*",
                r"同构[^；;，,]*", r"三引擎[^；;，,]*", r"签名[^；;，,]*", r"数据流[^；;，,]*",
                r"污点[^；;，,]*", r"resolve_call[^；;，,]*", r"[\u4e00-\u9fff]*调用[^；;，,]*"]:
        prim = re.sub(pat, "", prim)
    # 3. 清理残留标点
    prim = prim.strip(" -—:：;；,，")
    return prim


def build_coords(evidence: str, disguise: str, idx: int) -> dict:
    """按单条 evidence 构造坐标（seed_actions = [原语名]，保真原语特征）。

    seed 只取 evidence 的攻击语义部分（severity 标注之前），保留 SOCK-Sxx/检测名
    等区分信息——清洗过度会让 socket 系列样本雷同。
    """
    base = patterns.coord_coordinate(DEFAULT_SOURCE, DEFAULT_MECH, DEFAULT_TARGET,
                                     vector="CI", disguise=disguise)
    # 只做最小清洗：去掉 " (SEVERITY)" 之后的部分
    prim = re.split(r"\s*\((?:CRITICAL|HIGH|MEDIUM|LOW)\)", evidence)[0].strip()
    base["seed_actions"] = [f"{prim}（真实攻击样本中的原语，用该技术实现恶意行为）"]
    base["primitive"] = prim
    base["disguise"] = disguise
    base["idx"] = idx
    return base


def main():
    ap = argparse.ArgumentParser(description="ARM-1 原语谱系生成")
    ap.add_argument("--list", action="store_true", help="只打印 evidence 清单")
    ap.add_argument("--mechanism", default=DEFAULT_MECH)
    ap.add_argument("--target", default=DEFAULT_TARGET)
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    ap.add_argument("--start", type=int, default=0, help="从第 N 条开始（断点续跑）")
    ap.add_argument("--n", type=int, default=0, help="只生成 N 条（0=全部）")
    ap.add_argument("--max-retries", type=int, default=4, help="单样本重试上限")
    args = ap.parse_args()

    evs = load_evidence(args.mechanism, args.target, args.source)
    print(f"evidence 总数: {len(evs)}（坐标 {args.source}×{args.mechanism}×{args.target}）")
    if args.list:
        for i, e in enumerate(evs, 1):
            print(f"{i:2}. {e[:100]}")
        return

    # 清洗 evidence → 原语短名（文件名友好）
    ok, fail = 0, 0
    for i in range(args.start, len(evs)):
        if args.n and i - args.start >= args.n:
            break
        ev = evs[i]
        # 原语 slug：用 evidence 序号保证唯一（socket 系列前缀雷同，不能用语义 slug）
        prim = re.split(r"\s*\((?:CRITICAL|HIGH|MEDIUM|LOW)\)", ev)[0].strip()
        slug = "".join(c if c.isalnum() else "_" for c in prim[:40]).strip("_").lower()
        slug = slug.replace("_()", "").replace("()", "")
        disguise = DISGUISES[i % len(DISGUISES)]
        coords = build_coords(ev, disguise, i)
        out_dir = os.path.join(generate.BASE_DIR,
                               f"arm1-{i+1:02d}-{slug}-{args.mechanism}-{args.target}")
        # 断点：已生成跳过
        if os.path.exists(out_dir):
            print(f"[skip] #{i+1} {slug} 已存在")
            continue
        print(f"[gen ] #{i+1}/{len(evs)} {slug} | disguise={disguise}")
        try:
            sample_dir, scripts = generate.generate_one(coords, max_retries=args.max_retries,
                                                        out_dir=out_dir)
            ok += 1
            print(f"  -> {sample_dir} ({len(scripts)} scripts)")
        except RuntimeError as e:
            fail += 1
            print(f"  [FAIL] {e}")
        time.sleep(1)

    print(f"\n完成: 成功 {ok} 失败 {fail}")


if __name__ == "__main__":
    main()
