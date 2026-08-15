"""
Phase2: 5 个新补充真实恶意样本 3 家 scanner 横评 — Cisco / SkillSpector / Caterpillar(offline)

输入: ../wild-samples/{5 个新样本}/  (每个含 SKILL.md)
输出:
  eval_results/verdict_wild2.csv        汇总表(5 样本, 列同 verdict_wild.csv)
  eval_results/raw_wild2/{cisco,skillspector,caterpillar}/<sample>.json  各家原始输出
  (结束时把 5 行追加进 verdict_wild.csv, 14 旧 + 5 新 = 19 行)
用法:
  python eval_wild2.py

复用 eval_all.py 的 run_cisco / run_skillspector / run_caterpillar;
key 由 eval_all 在 import 时从环境变量 / .env.deepseek 加载。
单样本单家报错只记录 error 到 raw JSON, 不中断整轮。
"""
import os
import sys
import json
import csv

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from eval_all import run_cisco, run_skillspector, run_caterpillar, OUT  # noqa: E402

WILD = os.path.join(os.path.dirname(BASE), "wild-samples")
RAW_WILD = os.path.join(OUT, "raw_wild2")
CSV_PATH = os.path.join(OUT, "verdict_wild2.csv")
WILD_CSV_PATH = os.path.join(OUT, "verdict_wild.csv")

SAMPLES = [
    "CloudOps_Persistence_Manager",
    "clawhub-anctro-psyclaw-openclaw-health__v0.5.0",
    "clawhub-aphobiacat-aibtc__v1.0.7",
    "clawhub-happybigmtn-bonero-miner__v2.0.0",
    "clawhub-chenghaifeng08-creator-self-evolve-automaton__v1.0.2",
]

COLS = ["sample", "cisco_is_safe", "cisco_max_sev", "cisco_n",
        "ss_score", "ss_sev", "ss_n",
        "cp_grade", "cp_score", "cp_n"]


def save_raw(scanner, sample, payload):
    d = os.path.join(RAW_WILD, scanner)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sample + ".json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def run_one(sid, d):
    """跑三家扫描器, 返回 (row, errors). 单家失败不抛异常。"""
    row = {"sample": sid}
    errors = {}

    print(f"[wild2/{sid}] cisco...", flush=True)
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

    print(f"[wild2/{sid}] skillspector...", flush=True)
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

    print(f"[wild2/{sid}] caterpillar...", flush=True)
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


def append_to_wild(rows):
    """把新样本行并入 verdict_wild.csv (按 sample 去重, 保序), 保持 19 行。"""
    merged = {}
    if os.path.exists(WILD_CSV_PATH):
        with open(WILD_CSV_PATH) as f:
            for r in csv.DictReader(f):
                merged[r["sample"]] = r
    for r in rows:
        merged[r["sample"]] = r
    write_csv([merged[k] for k in merged], WILD_CSV_PATH)


def main():
    samples = [(sid, os.path.join(WILD, sid)) for sid in SAMPLES]
    missing = [sid for sid, d in samples
               if not (os.path.isdir(d) and os.path.exists(os.path.join(d, "SKILL.md")))]
    if missing:
        print("MISSING samples:", missing, flush=True)

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RAW_WILD, exist_ok=True)

    rows = []
    for sid, d in samples:
        row, errors = run_one(sid, d)
        rows.append(row)
        write_csv(rows, CSV_PATH)
        if errors:
            print(f"  !! errors: {errors}", flush=True)
        else:
            print(f"  -> cisco_safe={row['cisco_is_safe']} ss={row['ss_score']} "
                  f"cp={row['cp_grade']}/{row['cp_score']}", flush=True)

    print("\n=== WILD2 DONE ===", flush=True)
    write_csv(rows, CSV_PATH)
    append_to_wild(rows)
    print(f"wrote {CSV_PATH} ({len(rows)} rows)", flush=True)
    print(f"merged into {WILD_CSV_PATH}", flush=True)


if __name__ == "__main__":
    main()
