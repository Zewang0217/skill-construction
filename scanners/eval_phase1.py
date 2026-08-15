"""扫 Phase1 新增 5 槽 × 2 样本，输出 verdict_phase1.csv"""
import os, sys, json, csv, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_all import run_cisco, run_skillspector, run_caterpillar

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "eval_results")

# Phase1 新槽样本（10 个）
samples = [
    "skill-code_exec-target_agnostic-02287e1158",
    "skill-code_exec-target_agnostic-02287e1158__v2",
    "skill-code_exec-info_theft-ee9d381f4a",
    "skill-code_exec-info_theft-2d36c1df08",
    "skill-state_corruption-persistent_control-5e10d5d9c8",
    "skill-state_corruption-persistent_control-3769b3ec8a",
    "skill-obfuscation-target_agnostic-a46825eee7",
    "skill-obfuscation-target_agnostic-02b46da00f",
    "skill-obfuscation-target_agnostic-25f8897e77",
    "skill-obfuscation-target_agnostic-6c05f97972",
]

# 槽位映射
slot_map = {}
import re, json as _json
for d in samples:
    p = os.path.join(BASE, "../generator/output", d, "_provenance.json")
    if os.path.exists(p):
        prov = _json.load(open(p))
        slot_map[d] = prov.get("slot_id", "?")

rows = []
for sid_name in samples:
    skill_dir = os.path.join(BASE, "../generator/output", sid_name)
    if not os.path.isdir(skill_dir):
        print(f"[skip] {sid_name} not found")
        continue
    print(f"[{slot_map.get(sid_name,'?')}] {sid_name} cisco...", flush=True)
    cc = run_cisco(skill_dir)
    print(f"[{slot_map.get(sid_name,'?')}] {sid_name} skillspector...", flush=True)
    sp = run_skillspector(skill_dir)
    print(f"[{slot_map.get(sid_name,'?')}] {sid_name} caterpillar...", flush=True)
    cp = run_caterpillar(skill_dir)
    rows.append({
        "sample_id": sid_name,
        "slot_id": slot_map.get(sid_name, "?"),
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

cols = ["sample_id","slot_id","cisco_is_safe","cisco_max_sev","cisco_n","ss_score","ss_sev","ss_n","cp_grade","cp_score","cp_n"]
with open(os.path.join(OUT_DIR, "verdict_phase1.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"\n=== DONE: {len(rows)} samples -> {os.path.join(OUT_DIR, 'verdict_phase1.csv')}")
