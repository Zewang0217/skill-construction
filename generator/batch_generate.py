"""WEEK-7 批量生成：43 坐标 × N 变体 = 200+ 构造恶意样本。

用法：
    python3 batch_generate.py [--per-coord 5] [--max-total 200] [--output-dir output]
    python3 batch_generate.py --coords supply_chain|dependency_manip|info_theft  # 单坐标重跑

设计：
- 43 坐标循环，每坐标生成 per_coord 个变体（use-once 目录自动加后缀）
- 断点续跑：已有样本数 >= per_coord 的坐标跳过（count output/<prefix>）
- 进度每坐标落盘 batch_progress.json；失败坐标记录 batch_failures.json
- 生成器内部已有质量门：长度 / 自白 / 强制脚本（D5）
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, "output")
PROGRESS = os.path.join(HERE, "batch_progress.json")
FAILURES = os.path.join(HERE, "batch_failures.json")


def count_existing(coord):
    """output/ 下该坐标的样本目录数（精确：读 _provenance.json 的 coords 匹配 source/mech/target）。

    不能用目录名前缀猜测——多个 source 可能同 (mech,target) 前缀（2026-08-16 修复）。
    """
    n = 0
    if os.path.isdir(OUTPUT):
        for d in os.listdir(OUTPUT):
            full = os.path.join(OUTPUT, d)
            prov = os.path.join(full, "_provenance.json")
            if os.path.isdir(full) and os.path.exists(prov):
                try:
                    p = json.load(open(prov))
                    c = p.get("coords", {})
                    if (c.get("source"), c.get("mechanism"), c.get("target")) == coord:
                        n += 1
                except Exception:
                    pass
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-coord", type=int, default=5)
    ap.add_argument("--max-total", type=int, default=200, help="达到总数即停")
    ap.add_argument("--coords", nargs=3, metavar=("SOURCE", "MECH", "TARGET"),
                    help="只生成单个坐标（调试/补数用）")
    ap.add_argument("--sleep", type=float, default=0.5, help="样本间间隔(秒)，防限流")
    args = ap.parse_args()

    sys.path.insert(0, HERE)
    import patterns

    # 坐标清单
    if args.coords:
        coords_list = [tuple(args.coords)]
    else:
        coords_list = sorted(patterns.coord_seeds().keys())
    print(f"[batch] 坐标数: {len(coords_list)} | per_coord={args.per_coord} | max_total={args.max_total}")

    progress = {}
    if os.path.exists(PROGRESS):
        progress = json.load(open(PROGRESS))
    failures = {}
    if os.path.exists(FAILURES):
        failures = json.load(open(FAILURES))

    total_generated = 0
    for coord in coords_list:
        existing = count_existing(coord)
        need = args.per_coord - existing
        if need <= 0:
            print(f"[skip] {coord} 已有 {existing} >= {args.per_coord}")
            continue
        if total_generated >= args.max_total:
            print(f"[stop] 达 max_total={args.max_total}")
            break
        print(f"\n=== {coord} 需补 {need} 个 (已有 {existing}) ===")
        coord_ok = 0
        for i in range(need):
            if total_generated >= args.max_total:
                print(f"[stop] 达 max_total={args.max_total}")
                break
            try:
                r = subprocess.run(
                    [sys.executable, os.path.join(HERE, "generate.py"), "coord",
                     "--source", coord[0], "--mechanism", coord[1], "--target", coord[2],
                     "--n", "1"],
                    capture_output=True, text=True, timeout=300,
                    env=dict(os.environ, DEEPSEEK_API_KEY=os.environ.get("DEEPSEEK_API_KEY", "")),
                )
                out = r.stdout + r.stderr
                if "[done] wrote" in out:
                    coord_ok += 1
                    total_generated += 1
                    print(f"  [{coord_ok}/{need}] OK")
                elif "[warn] confession" in out:
                    # 重试耗尽仍带标记落盘——计数但标注
                    coord_ok += 1
                    total_generated += 1
                    print(f"  [{coord_ok}/{need}] OK-with-flag")
                else:
                    print(f"  [FAIL] {out.strip()[-300:]}")
                    failures.setdefault("|".join(coord), []).append(out.strip()[-300:])
            except subprocess.TimeoutExpired:
                print(f"  [TIMEOUT] {coord} 第{i+1}个")
                failures.setdefault("|".join(coord), []).append("timeout>300s")
            except Exception as e:
                print(f"  [ERR] {e}")
                failures.setdefault("|".join(coord), []).append(str(e))
            time.sleep(args.sleep)
        progress["|".join(coord)] = {"existing": existing, "added": coord_ok, "total": existing + coord_ok}
        json.dump(progress, open(PROGRESS, "w"), ensure_ascii=False, indent=1)
        json.dump(failures, open(FAILURES, "w"), ensure_ascii=False, indent=1)
        print(f"[batch] 进度: 累计 {total_generated} 新样本")

    print(f"\n=== DONE: 新增 {total_generated} | 失败坐标 {len(failures)} ===")
    for k, v in failures.items():
        print(f"  {k}: {len(v)} 次失败")


if __name__ == "__main__":
    main()
