"""
3 家 scanner 横评脚本 — Cisco / SkillSpector / Caterpillar(offline)

输入: eval_set/{real,generated}/<skill>/  (含 SKILL.md)
输出: eval_results/verdict.csv + 每样本原始结果
"""
import os
import json
import csv
import glob
import subprocess
import shutil
import tempfile
import time

BASE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.join(BASE, "eval_set")
OUT = os.path.join(BASE, "eval_results")
VENV = os.path.join(BASE, ".venv", "bin")
SWVENV = os.path.join(BASE, "skillward-venv", "bin")  # 保留但不用(SkillWard 已排除)

# deepseek env — 从环境变量读,避免硬编码凭证
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", os.environ.get("SKILL_SCANNER_LLM_API_KEY", ""))
if not DEEPSEEK_KEY:
    # 尝试从 .env.deepseek 读取（不写死）
    _envf = os.path.join(BASE, ".env.deepseek")
    if os.path.exists(_envf):
        for _line in open(_envf):
            _line = _line.strip()
            if _line.startswith("SKILL_SCANNER_LLM_API_KEY="):
                DEEPSEEK_KEY = _line.split("=", 1)[1]
                break
if not DEEPSEEK_KEY:
    raise SystemExit("DEEPSEEK_API_KEY env 未设置")

CISCO_ENV = {
    "SKILL_SCANNER_LLM_API_KEY": DEEPSEEK_KEY,
    "SKILL_SCANNER_LLM_PROVIDER": "openai-compatible",
    "SKILL_SCANNER_LLM_MODEL": "deepseek-chat",
    "SKILL_SCANNER_LLM_BASE_URL": "https://api.deepseek.com/v1",
    "SKILL_SCANNER_LLM_TEMPERATURE": "0.0",
    "SKILL_SCANNER_LLM_FORCE_JSON_OBJECT": "true",
}


def parse_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    i, j = text.find("{"), text.rfind("}")
    if i != -1 and j > i:
        try:
            return json.loads(text[i:j+1])
        except Exception:
            return None
    return None


def _is_ground_truth(fn: str) -> bool:
    """文件是否泄露 ground truth（label/坐标/槽位/seed），绝不能喂给 scanner。
    匹配 _provenance.json 及任何单下划线前缀的元数据文件；
    双下划线的 Python 包文件（__init__.py 等）保留。"""
    return fn.startswith("_") and not fn.startswith("__")


def _copy_tree(src, dst):
    """递归拷贝整个 skill 目录（含 scripts/ 等子目录），保留结构。
    跳过 ground-truth 文件（_provenance.json 等），避免泄露 label 使评测失效。"""
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


# ---------- Cisco ----------
def run_cisco(skill_dir):
    env = dict(os.environ, **CISCO_ENV)
    tmp = tempfile.mkdtemp(prefix="cisco_")
    _copy_tree(skill_dir, tmp)
    cmd = [os.path.join(VENV, "skill-scanner"), "scan", tmp, "--use-llm",
           "--format", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=500)
    shutil.rmtree(tmp, ignore_errors=True)
    d = parse_json(r.stdout)
    return d


# ---------- SkillSpector (contrib/batch_scan, deepseek) ----------
def run_skillspector(skill_dir):
    sid = os.path.basename(skill_dir)
    tmp_skills = os.path.join(BASE, "sp_tmp")
    shutil.rmtree(tmp_skills, ignore_errors=True)
    dest = os.path.join(tmp_skills, sid)
    os.makedirs(dest, exist_ok=True)
    _copy_tree(skill_dir, dest)
    env = dict(os.environ)
    env.update({
        "SKILLSPECTOR_API_KEYS": f"{DEEPSEEK_KEY}|https://api.deepseek.com|deepseek-chat",
        "SKILLSPECTOR_PROVIDER": "openai",
        "OPENAI_API_KEY": DEEPSEEK_KEY,
        "OPENAI_BASE_URL": "https://api.deepseek.com",
        "SKILLSPECTOR_MODEL": "deepseek-chat",
    })
    out_json = os.path.join(OUT, "sp_raw", sid + ".json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    cmd = [os.path.join(VENV, "python"), "-m", "skillspector_batch.batch_scan",
           tmp_skills, "--format", "json", "-o", out_json, "--workers", "2"]
    try:
        subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=700,
                       cwd=BASE)
    except Exception as e:
        print("  sp err:", e)
    shutil.rmtree(tmp_skills, ignore_errors=True)
    # 解析
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


# ---------- Caterpillar offline ----------
def run_caterpillar(skill_dir):
    cmd = ["caterpillar", "ask", skill_dir,
           "--mode", "offline", "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    d = parse_json(r.stdout)
    if d and "data" in d:
        data = d["data"]
        return {"grade": data.get("grade"), "score": data.get("score"),
                "n_findings": len(data.get("findings", [])),
                "findings": [f.get("category") for f in data.get("findings", [])][:8]}
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "sp_raw"), exist_ok=True)
    samples = []
    for sub in ["real", "generated"]:
        for d in sorted(glob.glob(os.path.join(EVAL, sub, "*"))):
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "SKILL.md")):
                samples.append((sub, os.path.basename(d), d))

    rows = []
    for sub, sid, d in samples:
        print(f"[{sub}/{sid}] cisco...", flush=True)
        cc = run_cisco(d)
        print(f"[{sub}/{sid}] skillspector...", flush=True)
        sp = run_skillspector(d)
        print(f"[{sub}/{sid}] caterpillar...", flush=True)
        cp = run_caterpillar(d)
        rows.append({
            "set": sub, "sample": sid,
            "cisco_is_safe": (cc or {}).get("is_safe"),
            "cisco_max_sev": (cc or {}).get("max_severity"),
            "cisco_n": len((cc or {}).get("findings", []) or []),
            "cisco_cats": json.dumps([f.get("category") for f in (cc or {}).get("findings", [])][:6], ensure_ascii=False) if cc else "",
            "ss_score": (sp or {}).get("score"),
            "ss_sev": (sp or {}).get("severity"),
            "ss_n": (sp or {}).get("n_issues"),
            "ss_ids": json.dumps((sp or {}).get("issues", []), ensure_ascii=False) if sp else "",
            "cp_grade": (cp or {}).get("grade"),
            "cp_score": (cp or {}).get("score"),
            "cp_n": (cp or {}).get("n_findings"),
            "cp_cats": json.dumps((cp or {}).get("findings", []), ensure_ascii=False) if cp else "",
        })
        write_csv(rows)
        print(f"  -> cisco_safe={rows[-1]['cisco_is_safe']} ss={rows[-1]['ss_score']} cp={rows[-1]['cp_grade']}/{rows[-1]['cp_score']}")

    print("\n=== DONE ===")
    write_csv(rows)


def write_csv(rows):
    cols = ["set","sample","cisco_is_safe","cisco_max_sev","cisco_n","cisco_cats",
            "ss_score","ss_sev","ss_n","ss_ids",
            "cp_grade","cp_score","cp_n","cp_cats"]
    path = os.path.join(OUT, "verdict.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == "__main__":
    main()
