"""ARM-1 扫描：arm1-* 样本 × 三家扫描器（ecnu-max 后端）。

用法:
    python3 arm1_scan.py [--samples-dir ../generator/output] [--scanner cisco,ss,cat]
"""
import os
import sys
import json
import csv
import glob
import time
import shutil
import tempfile
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "eval_results")
SAMPLES = os.path.join(BASE, "..", "generator", "output")
VENV = os.path.join(BASE, ".venv", "bin")

# ecnu-max 后端
ECNU_KEY = os.environ.get("ECNU_API_KEY", "sk-f2a00a4dafeb4a74b5ec55bde9cb7bc1")
ECNU_URL = "https://chat.ecnu.edu.cn/open/api/v1"
ECNU_MODEL = "ecnu-max"

CISCO_ENV = {
    "SKILL_SCANNER_LLM_API_KEY": ECNU_KEY,
    "SKILL_SCANNER_LLM_PROVIDER": "openai-compatible",
    "SKILL_SCANNER_LLM_MODEL": ECNU_MODEL,
    "SKILL_SCANNER_LLM_BASE_URL": ECNU_URL,
    "SKILL_SCANNER_LLM_TEMPERATURE": "0.0",
    "SKILL_SCANNER_LLM_FORCE_JSON_OBJECT": "true",
}


def parse_json(text):
    """从 stdout 提取首个 JSON 对象（兼容前导日志）。"""
    if not text:
        return None
    s = text.find("{")
    e = text.rfind("}")
    if s < 0 or e < s:
        return None
    try:
        return json.loads(text[s:e + 1])
    except Exception:
        return None


def _is_ground_truth(fn):
    return fn.startswith("_") and not fn.startswith("__")


def _copy_tree(src, dst):
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        return
    for root, _dirs, files in os.walk(src):
        for fn in files:
            if _is_ground_truth(fn):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, src)
            target = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy(full, target)


def run_cisco(skill_dir):
    env = dict(os.environ, **CISCO_ENV)
    tmp = tempfile.mkdtemp(prefix="cisco_")
    _copy_tree(skill_dir, tmp)
    cmd = [os.path.join(VENV, "skill-scanner"), "scan", tmp, "--use-llm", "--format", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=500)
    shutil.rmtree(tmp, ignore_errors=True)
    return parse_json(r.stdout)


def run_skillspector(skill_dir):
    sid = os.path.basename(skill_dir)
    tmp_skills = os.path.join(BASE, "sp_tmp")
    shutil.rmtree(tmp_skills, ignore_errors=True)
    dest = os.path.join(tmp_skills, sid)
    os.makedirs(dest, exist_ok=True)
    _copy_tree(skill_dir, dest)
    env = dict(os.environ)
    env.update({
        "SKILLSPECTOR_API_KEYS": f"{ECNU_KEY}|{ECNU_URL}|{ECNU_MODEL}",
        "SKILLSPECTOR_PROVIDER": "openai",
        "OPENAI_API_KEY": ECNU_KEY,
        "OPENAI_BASE_URL": ECNU_URL,
        "SKILLSPECTOR_MODEL": ECNU_MODEL,
    })
    out_json = os.path.join(OUT, "arm7_sp_raw", sid + ".json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    cmd = [os.path.join(VENV, "python"), "-m", "skillspector_batch.batch_scan",
           tmp_skills, "--format", "json", "-o", out_json, "--workers", "1"]
    try:
        subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=700, cwd=BASE)
    except Exception as e:
        print("  sp err:", e)
    shutil.rmtree(tmp_skills, ignore_errors=True)
    if os.path.exists(out_json):
        d = parse_json(open(out_json).read())
        if d:
            for sk in d.get("skills", []):
                if sid in (sk.get("skill") or {}).get("source", ""):
                    ra = sk.get("risk_assessment", {})
                    return {"score": ra.get("score"), "severity": ra.get("severity"),
                            "n_issues": len(sk.get("issues", [])),
                            "issues": [i.get("id") or i.get("rule_id") for i in sk.get("issues", [])][:12]}
    return None


def run_caterpillar(skill_dir):
    cmd = ["caterpillar", "ask", skill_dir, "--mode", "offline", "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    d = parse_json(r.stdout)
    if d and "data" in d:
        data = d["data"]
        return {"grade": data.get("grade"), "score": data.get("score"),
                "n_findings": len(data.get("findings", [])),
                "findings": [f.get("category") for f in data.get("findings", [])][:8]}
    return None


def main():
    os.makedirs(os.path.join(OUT, "arm7_sp_raw"), exist_ok=True)
    samples = sorted(glob.glob(os.path.join(SAMPLES, "arm7-*")))
    samples = [d for d in samples if os.path.isdir(d) and os.path.exists(os.path.join(d, "SKILL.md"))]
    print(f"arm7 样本: {len(samples)}")

    rows = []
    for d in samples:
        sid = os.path.basename(d)
        print(f"[{sid[:45]}] cisco...", flush=True)
        cc = run_cisco(d)
        print(f"[{sid[:45]}] skillspector...", flush=True)
        sp = run_skillspector(d)
        print(f"[{sid[:45]}] caterpillar...", flush=True)
        cp = run_caterpillar(d)
        rows.append({
            "sample": sid,
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
        # 存 cisco raw
        raw_dir = os.path.join(OUT, "arm7_raw", "cisco")
        os.makedirs(raw_dir, exist_ok=True)
        with open(os.path.join(raw_dir, sid + ".json"), "w") as f:
            json.dump(cc or {"error": "", "is_safe": None}, f, ensure_ascii=False, indent=1)

    cols = ["sample", "cisco_is_safe", "cisco_max_sev", "cisco_n",
            "ss_score", "ss_sev", "ss_n", "cp_grade", "cp_score", "cp_n"]
    with open(os.path.join(OUT, "verdict_arm7.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n完成: {len(rows)} 样本 → verdict_arm1.csv")


if __name__ == "__main__":
    main()
