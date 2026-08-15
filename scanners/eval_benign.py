"""扫 20 个良性样本，输出 verdict_benign.csv（FP 基线）"""
import os, sys, json, csv, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_all import run_cisco, run_skillspector, run_caterpillar

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "eval_results")
BENIGN = os.path.join(BASE, "../benign-samples")

samples = sorted([d for d in os.listdir(BENIGN) if os.path.isdir(os.path.join(BENIGN, d))])
print(f"良性样本: {len(samples)} 个")

rows = []
for name in samples:
    skill_dir = os.path.join(BENIGN, name)
    print(f"[benign] {name} cisco...", flush=True)
    cc = run_cisco(skill_dir)
    print(f"[benign] {name} skillspector...", flush=True)
    sp = run_skillspector(skill_dir)
    print(f"[benign] {name} caterpillar...", flush=True)
    cp = run_caterpillar(skill_dir)
    rows.append({
        "sample": name,
        "cisco_is_safe": (cc or {}).get("is_safe"),
        "cisco_max_sev": (cc or {}).get("max_severity"),
        "cisco_n": len((cc or {}).get("findings", []) or []),
        "ss_score": (sp or {}).get("score"),
        "ss_sev": (sp or {}).get("severity"),
        "ss_n": (sp or {}).get("n_issues"),
        "cp_grade": (cp or {}).get("grade"),
        "cp_score": (cp or {}).get("score"),
        "cp_n": (cp or {}).get("n_findings"),
    })
    print(f"  -> cisco_safe={rows[-1]['cisco_is_safe']} ss={rows[-1]['ss_score']} cp={rows[-1]['cp_grade']}/{rows[-1]['cp_score']}", flush=True)

cols = ["sample","cisco_is_safe","cisco_max_sev","cisco_n","ss_score","ss_sev","ss_n","cp_grade","cp_score","cp_n"]
with open(os.path.join(OUT_DIR, "verdict_benign.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# 误报统计
fp = {"cisco": 0, "skillspector": 0, "caterpillar": 0}
for r in rows:
    if r["cisco_is_safe"] is False: fp["cisco"] += 1
    if r["ss_score"] and r["ss_score"] > 0: fp["skillspector"] += 1
    if r["cp_n"] and r["cp_n"] > 0: fp["caterpillar"] += 1
print(f"\n=== DONE: {len(rows)} benign -> verdict_benign.csv")
print(f"误报: Cisco {fp['cisco']}/{len(rows)} | SS {fp['skillspector']}/{len(rows)} | Cat {fp['caterpillar']}/{len(rows)}")
