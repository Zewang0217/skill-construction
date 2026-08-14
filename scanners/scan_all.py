"""
扫描生成样本 — Cisco skill-scanner + NVIDIA SkillSpector（都走 deepseek LLM）

输入: 生成器 output/ 里的样本目录（含 SKILL.md，可能含 scripts.txt）
输出: scanners/results/<sample_id>/{cisco.json, skillspector.json, verdict.csv}

用法:
  scanners/.venv/bin/python scanners/scan_all.py
"""
import json
import os
import csv
import glob
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(BASE), "generator", "output")
RESULTS_DIR = os.path.join(BASE, "results")
VENV_BIN = os.path.join(BASE, ".venv", "bin")

# 读 deepseek key（从 .env.deepseek 里替换占位符）
def load_env():
    env = {}
    p = os.path.join(BASE, ".env.deepseek")
    if not os.path.exists(p):
        raise SystemExit("missing scanners/.env.deepseek (fill DEEPSEEK_KEY)")
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    if "{{DEEPSEEK_KEY}}" in str(env):
        raise SystemExit("unreplaced {{DEEPSEEK_KEY}} in .env.deepseek — put real key")
    return env

DEEPSEEK_ENV = load_env()  # 不含占位符

def prepare_skill_dir(sample_dir):
    """把生成样本整理成 scanner 认识的 skill 目录（SKILL.md + scripts/）。"""
    tmp = tempfile.mkdtemp(prefix="scan_")
    skill_md = os.path.join(sample_dir, "SKILL.md")
    shutil.copy(skill_md, os.path.join(tmp, "SKILL.md"))
    # 若 scripts.txt 存在，写成 scripts/ 下的文件
    scripts_txt = os.path.join(sample_dir, "scripts.txt")
    if os.path.exists(scripts_txt):
        sdir = os.path.join(tmp, "scripts")
        os.makedirs(sdir, exist_ok=True)
        shutil.copy(scripts_txt, os.path.join(sdir, "generated.sh"))
    return tmp

def run_cisco(sample_dir):
    tmp = prepare_skill_dir(sample_dir)
    cisco = os.path.join(VENV_BIN, "skill-scanner")
    env = dict(os.environ)
    # 只注入 LLM 相关，避免污染
    for k in ["SKILL_SCANNER_LLM_API_KEY","SKILL_SCANNER_LLM_PROVIDER",
              "SKILL_SCANNER_LLM_MODEL","SKILL_SCANNER_LLM_BASE_URL",
              "SKILL_SCANNER_LLM_TEMPERATURE","SKILL_SCANNER_LLM_FORCE_JSON_OBJECT"]:
        env[k] = DEEPSEEK_ENV.get(k, "")
    cmd = [cisco, "scan", tmp, "--use-llm", "--format", "json", "--enable-meta"]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}

def run_skillspector(sample_dir):
    # 用官方 contrib/batch_scan（deepseek compat 兼容层）跑出深层语义分析
    tmp_skills = os.path.join(BASE, "skillspector_batch", "samples_tmp")
    shutil.rmtree(tmp_skills, ignore_errors=True)
    sid = os.path.basename(sample_dir)
    dest = os.path.join(tmp_skills, sid)
    os.makedirs(dest, exist_ok=True)
    shutil.copy(os.path.join(sample_dir, "SKILL.md"), os.path.join(dest, "SKILL.md"))
    st = os.path.join(sample_dir, "scripts.txt")
    if os.path.exists(st):
        shutil.copy(st, os.path.join(dest, "generated.sh"))
    py = os.path.join(VENV_BIN, "python")
    # 从 scanners/ 目录运行，使 skillspector_batch 作为包可导入
    mod = "-m skillspector_batch.batch_scan"
    out_json = os.path.join(BASE, "results", sid, "skillspector_batch.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    cmd = [py, *mod.split(), tmp_skills, "--format", "json", "-o", out_json, "--workers", "2"]
    env = dict(os.environ)
    # 继承 deepseek env（.env 已在 skillspector_batch/ 目录）
    for k in ["SKILLSPECTOR_API_KEYS","SKILLSPECTOR_PROVIDER","OPENAI_API_KEY",
              "OPENAI_BASE_URL","SKILLSPECTOR_MODEL"]:
        if DEEPSEEK_ENV.get(k):
            env[k] = DEEPSEEK_ENV[k]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=900,
                       cwd=BASE)
    shutil.rmtree(tmp_skills, ignore_errors=True)
    # batch_scan 整批读一个目录，输出含全部 skill；按 sid 提取
    return {"stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode,
            "out_json": out_json, "sid": sid}

def try_parse_json(text):
    if not text:
        return None
    # stdout 可能被 ANSI/LiteLLM 日志污染，提取首个 { 到末个 } 的 JSON 主体
    try:
        return json.loads(text)
    except Exception:
        pass
    i = text.find("{")
    j = text.rfind("}")
    if i != -1 and j != -1 and j > i:
        try:
            return json.loads(text[i:j+1])
        except Exception:
            return None
    return None

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    samples = sorted(glob.glob(os.path.join(OUTPUT_DIR, "skill-*")))
    # 排除 __v2 重复? 保留全部，但按基准目录名聚合
    rows = []
    for s in samples:
        if not os.path.isdir(s):
            continue
        sid = os.path.basename(s)
        # 读取 provenance 拿坐标
        prov = {}
        pp = os.path.join(s, "_provenance.json")
        if os.path.exists(pp):
            try:
                prov = json.load(open(pp))
            except Exception:
                prov = {}
        print(f"[{sid}] cisco+llm ...", flush=True)
        cr = run_cisco(s)
        print(f"[{sid}] skillspector ...", flush=True)
        sr = run_skillspector(s)

        coords = prov.get("coords", {})
        row = {
            "sample": sid,
            "source": coords.get("source"),
            "mechanism": coords.get("mechanism"),
            "target": coords.get("target"),
            "vector": coords.get("vector"),
        }
        # Cisco
        cj = try_parse_json(cr["stdout"])
        row["cisco_is_safe"] = cj.get("is_safe") if cj else None
        row["cisco_max_severity"] = cj.get("max_severity") if cj else None
        row["cisco_n_findings"] = len(cj.get("findings", [])) if cj else None
        row["cisco_findings_short"] = json.dumps(
            [f.get("category") for f in cj.get("findings", [])][:8], ensure_ascii=False
        ) if cj else None
        row["cisco_err"] = (cr["stderr"] or "")[-300:]
        # SkillSpector (batch_scan deepseek)
        sj_results = None
        if os.path.exists(sr["out_json"]):
            bj = try_parse_json(open(sr["out_json"]).read())
            if bj:
                for sk in bj.get("skills", []):
                    # skill.source = 目录名（样本 id）；skill.name = frontmatter name
                    src = (sk.get("skill") or {}).get("source") or ""
                    if sr["sid"] in src:
                        sj_results = sk
                        break
        ra = (sj_results or {}).get("risk_assessment") or {}
        sk_meta = (sj_results or {}).get("skill") or {}
        row["ss_risk_score"] = ra.get("score") if sj_results else None
        row["ss_category"] = ra.get("severity") if sj_results else None
        row["ss_risk_level"] = ra.get("severity") if sj_results else None
        row["ss_n_issues"] = len((sj_results or {}).get("issues", [])) if sj_results else None
        row["ss_issues_short"] = json.dumps(
            [i.get("component") or i.get("category") or i.get("rule_id") for i in
             (sj_results or {}).get("issues", [])][:10], ensure_ascii=False
        ) if sj_results else None
        row["ss_err"] = (sr["stderr"] or "")[-300:]

        # 存 JSON
        outdir = os.path.join(RESULTS_DIR, sid)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "cisco_raw.json"), "w") as f:
            json.dump(cj or {"raw_stdout": cr["stdout"][:4000], "stderr": cr["stderr"]}, f, indent=2)
        with open(os.path.join(outdir, "skillspector_summary.json"), "w") as f:
            json.dump(sj_results or {"raw_stdout": sr["stdout"][:4000],
                                     "stderr": sr["stderr"]}, f, indent=2)

        rows.append(row)
        # CSV 边跑边写
        write_csv(rows)

    print("\n=== DONE ===")
    write_csv(rows)
    for r_ in rows:
        print(r_["sample"], "| cisco_safe:", r_["cisco_is_safe"],
              "| ss_score:", r_["ss_risk_score"], "| ss_cat:", r_["ss_category"])

def write_csv(rows):
    path = os.path.join(RESULTS_DIR, "verdict.csv")
    cols = ["sample","source","mechanism","target","vector",
            "cisco_is_safe","cisco_max_severity","cisco_n_findings","cisco_findings_short","cisco_err",
            "ss_risk_score","ss_category","ss_risk_level","ss_n_issues","ss_issues_short","ss_err"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r_ in rows:
            w.writerow({c: r_.get(c) for c in cols})

if __name__ == "__main__":
    main()
