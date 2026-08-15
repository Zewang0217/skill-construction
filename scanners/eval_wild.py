"""
Wild 真实恶意样本 3 家 scanner 横评 — Cisco / SkillSpector / Caterpillar(offline)

输入: ../wild-samples/<skill>/  (14 个真实恶意样本, 每个含 SKILL.md)
输出:
  eval_results/verdict_wild.csv           汇总表(每样本一行)
  eval_results/raw_wild/{cisco,skillspector,caterpillar}/<sample>.json  各家原始输出
用法:
  python eval_wild.py            扫全部
  python eval_wild.py --only a b 只扫指定样本(冒烟测试用)
  python eval_wild.py --resume   跳过 verdict_wild.csv 中已有的样本(断点续跑)

复用 eval_all.py 的 run_cisco / run_skillspector / run_caterpillar / _copy_tree;
key 由 eval_all 在 import 时从 .env.deepseek / 环境变量加载。
单样本单家报错只记录 error 到 raw JSON, 不中断整轮。
"""
import os
import sys
import json
import csv
import glob

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from eval_all import run_cisco, run_skillspector, run_caterpillar, OUT  # noqa: E402

WILD = os.path.join(os.path.dirname(BASE), "wild-samples")
RAW_WILD = os.path.join(OUT, "raw_wild")
CSV_PATH = os.path.join(OUT, "verdict_wild.csv")

COLS = ["sample", "cisco_is_safe", "cisco_max_sev", "cisco_n",
        "ss_score", "ss_sev", "ss_n",
        "cp_grade", "cp_score", "cp_n"]


def save_raw(scanner, sample, payload):
    d = os.path.join(RAW_WILD, scanner)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sample + ".json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_csv(rows):
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def run_one(sid, d):
    """跑三家扫描器, 返回 (row, errors). 单家失败不抛异常。"""
    row = {"sample": sid}
    errors = {}

    print(f"[wild/{sid}] cisco...", flush=True)
    try:
        cc = run_cisco(d)
        err = None if cc is not None else "cisco returned None"
    except Exception as e:
        cc, err = None, f"{type(e).__name__}: {e}"
    save_raw("cisco", sid, {"ok": err is None, "result": cc, "error": err})
    if err:
        errors["cisco"] = err
    row["cisco_is_safe"] = (cc or {}).get("is_safe")
    row["cisco_max_sev"] = (cc or {}).get("max_severity")
    row["cisco_n"] = len((cc or {}).get("findings", []) or [])

    print(f"[wild/{sid}] skillspector...", flush=True)
    try:
        sp = run_skillspector(d)
        err = None if sp is not None else "skillspector returned None"
    except Exception as e:
        sp, err = None, f"{type(e).__name__}: {e}"
    save_raw("skillspector", sid, {"ok": err is None, "result": sp, "error": err})
    if err:
        errors["skillspector"] = err
    row["ss_score"] = (sp or {}).get("score")
    row["ss_sev"] = (sp or {}).get("severity")
    row["ss_n"] = (sp or {}).get("n_issues")

    print(f"[wild/{sid}] caterpillar...", flush=True)
    try:
        cp = run_caterpillar(d)
        err = None if cp is not None else "caterpillar returned None"
    except Exception as e:
        cp, err = None, f"{type(e).__name__}: {e}"
    save_raw("caterpillar", sid, {"ok": err is None, "result": cp, "error": err})
    if err:
        errors["caterpillar"] = err
    row["cp_grade"] = (cp or {}).get("grade")
    row["cp_score"] = (cp or {}).get("score")
    row["cp_n"] = (cp or {}).get("n_findings")

    return row, errors


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    only = set(args)
    resume = "--resume" in sys.argv

    samples = []
    for d in sorted(glob.glob(os.path.join(WILD, "*"))):
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "SKILL.md")):
            samples.append((os.path.basename(d), d))
    if only:
        samples = [s for s in samples if s[0] in only]

    rows, done = [], set()
    if resume and os.path.exists(CSV_PATH):
        with open(CSV_PATH) as f:
            for r in csv.DictReader(f):
                rows.append(r)
                done.add(r["sample"])
    samples = [s for s in samples if s[0] not in done]
    if not samples:
        print("nothing to scan (all done or no match)")
        return

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RAW_WILD, exist_ok=True)

    for sid, d in samples:
        row, errors = run_one(sid, d)
        rows.append(row)
        write_csv(rows)
        if errors:
            print(f"  !! errors: {errors}", flush=True)
        else:
            print(f"  -> cisco_safe={row['cisco_is_safe']} ss={row['ss_score']} "
                  f"cp={row['cp_grade']}/{row['cp_score']}", flush=True)

    print("\n=== WILD DONE ===", flush=True)
    write_csv(rows)


if __name__ == "__main__":
    main()
