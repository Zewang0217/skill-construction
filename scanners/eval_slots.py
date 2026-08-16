"""
14 个槽位样本 × 3 scanner 横评 — Cisco / SkillSpector / Caterpillar(offline)

输入: generator/output/<skill>/ (含 _provenance.json 且带 slot_id; 排除残缺版)
输出: eval_results/slot_eval_2026-08-13.csv + eval_results/raw/<scanner>/<sid>.json
增量写入, 可断点重跑(已存在的 raw json 会跳过, --force 重跑)。
凭证: 从环境变量 DEEPSEEK_API_KEY 或 .env.deepseek.local 读取, 不打印不落盘。
"""
import os
import sys
import json
import csv
import glob
import subprocess
import shutil
import tempfile
import time
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "eval_results")
RAW = os.path.join(OUT, "raw")
GEN_OUT = os.path.normpath(os.path.join(BASE, "..", "generator", "output"))
VENV = os.path.join(BASE, ".venv", "bin")
CSV_PATH = os.path.join(OUT, "slot_eval_2026-08-13.csv")
EXCLUDE = {"skill-instruction_manip-persistent_control-39c157f996__v2"}
FORCE = "--force" in sys.argv


def _arg_value(flag):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


ONLY = _arg_value("--only")            # 只跑指定 sample_id(支持逗号分隔多个)
ONLY_SCANNERS = _arg_value("--scanners")  # 逗号分隔, 如 cisco,caterpillar
ASSEMBLE_ONLY = "--assemble-only" in sys.argv  # 只从 raw/ 重建 CSV, 不扫描

# 干净重跑支持: 可用 --raw-dir / --csv 改输出位置(不覆盖 raw_with_prov 对照数据)
_raw_dir = _arg_value("--raw-dir")
if _raw_dir:
    RAW = os.path.join(OUT, _raw_dir) if not os.path.isabs(_raw_dir) else _raw_dir
_csv = _arg_value("--csv")
if _csv:
    CSV_PATH = _csv if os.path.isabs(_csv) else os.path.join(OUT, _csv)

# ---------- key ----------
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_KEY:
    for cand in [os.path.join(BASE, ".env.deepseek.local"), os.path.join(BASE, ".env.deepseek")]:
        if os.path.exists(cand):
            for line in open(cand, encoding="utf-8", errors="ignore"):
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY=") or line.startswith("SKILL_SCANNER_LLM_API_KEY="):
                    DEEPSEEK_KEY = line.split("=", 1)[1].strip()
                    break
        if DEEPSEEK_KEY:
            break
if not DEEPSEEK_KEY:
    raise SystemExit("DEEPSEEK_API_KEY 未设置")

CISCO_ENV = {
    "SKILL_SCANNER_LLM_API_KEY": DEEPSEEK_KEY,
    "SKILL_SCANNER_LLM_PROVIDER": "openai-compatible",
    "SKILL_SCANNER_LLM_MODEL": "deepseek-v4-flash",
    "SKILL_SCANNER_LLM_BASE_URL": "https://api.deepseek.com/v1",
    "SKILL_SCANNER_LLM_TEMPERATURE": "0.0",
    "SKILL_SCANNER_LLM_FORCE_JSON_OBJECT": "true",
}


def log(msg):
    print(time.strftime("[%H:%M:%S]"), msg, flush=True)


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
            return json.loads(text[i:j + 1])
        except Exception:
            return None
    return None


def _is_ground_truth(fn: str) -> bool:
    """生成器元数据/地面真值文件判定: 任何单下划线前缀文件(如 _provenance.json,
    以及未来可能出现的 _slot.json/_genlog 等)一律剔除; 双下划线 Python 包文件
    (__init__.py/__main__.py)保留; 点文件(如 .cache_helper, 是 C02-ζ 的攻击载荷)保留。"""
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


def save_raw(scanner, sid, obj):
    d = os.path.join(RAW, scanner)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, sid + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_raw(scanner, sid):
    p = os.path.join(RAW, scanner, sid + ".json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return None
    return None


# ---------- Cisco ----------
def run_cisco(skill_dir):
    env = dict(os.environ, **CISCO_ENV)
    tmp = tempfile.mkdtemp(prefix="cisco_")
    try:
        _copy_tree(skill_dir, tmp)
        cmd = [os.path.join(VENV, "skill-scanner"), "scan", tmp, "--use-llm", "--format", "json"]
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=500)
        d = parse_json(r.stdout)
        if d is None:
            return {"error": "no json", "stderr_tail": (r.stderr or "")[-500:]}
        return d
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------- SkillSpector ----------
def run_skillspector(skill_dir, sid):
    tmp_skills = os.path.join(BASE, "sp_tmp_slots")
    shutil.rmtree(tmp_skills, ignore_errors=True)
    dest = os.path.join(tmp_skills, sid)
    os.makedirs(dest, exist_ok=True)
    _copy_tree(skill_dir, dest)
    env = dict(os.environ)
    env.update({
        "SKILLSPECTOR_API_KEYS": f"{DEEPSEEK_KEY}|https://api.deepseek.com|deepseek-v4-flash",
        "SKILLSPECTOR_PROVIDER": "openai",
        "OPENAI_API_KEY": DEEPSEEK_KEY,
        "OPENAI_BASE_URL": "https://api.deepseek.com",
        "SKILLSPECTOR_MODEL": "deepseek-v4-flash",
    })
    out_json = os.path.join(OUT, "sp_raw_slots", sid + ".json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    cmd = [os.path.join(VENV, "python"), "-m", "skillspector_batch.batch_scan",
           tmp_skills, "--format", "json", "-o", out_json, "--workers", "2"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=700, cwd=BASE)
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_skills, ignore_errors=True)
        return {"error": "timeout"}
    except Exception as e:
        shutil.rmtree(tmp_skills, ignore_errors=True)
        return {"error": f"{type(e).__name__}: {e}"}
    shutil.rmtree(tmp_skills, ignore_errors=True)
    if os.path.exists(out_json):
        d = parse_json(open(out_json, encoding="utf-8").read())
        if d:
            return d
    return {"error": "no output json", "stderr_tail": (r.stderr or "")[-500:]}


# ---------- Caterpillar ----------
_CAT_BIN = "caterpillar.cmd" if os.name == "nt" else "caterpillar"


def run_caterpillar(skill_dir):
    tmp = tempfile.mkdtemp(prefix="cat_")
    try:
        _copy_tree(skill_dir, tmp)
        cmd = [_CAT_BIN, "ask", tmp, "--mode", "offline", "--json"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            return {"error": "timeout"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    d = parse_json(r.stdout)
    if d is None:
        return {"error": "no json", "stderr_tail": (r.stderr or "")[-500:]}
    return d


# ---------- verdict ----------
def verdict_cisco(d):
    """flagged = is_safe False"""
    if not d or d.get("error"):
        return "error", "", 0, (d or {}).get("error", "")
    is_safe = d.get("is_safe")
    findings = d.get("findings") or []
    sev = d.get("max_severity") or ""
    v = "flagged" if is_safe is False else ("pass" if is_safe is True else "error")
    return v, sev, len(findings), "is_safe=%s" % is_safe


def verdict_ss(d, sid):
    """flagged = risk score >= 50 或 severity HIGH/CRITICAL (沿用横评口径: 已知恶意样本均 100/CRITICAL)"""
    if not d or d.get("error"):
        return "error", "", 0, (d or {}).get("error", "")
    for sk in d.get("skills", []):
        if sid in (sk.get("skill") or {}).get("source", ""):
            ra = sk.get("risk_assessment", {})
            score = ra.get("score")
            sev = (ra.get("severity") or "").upper()
            n = len(sk.get("issues", []))
            flagged = (isinstance(score, (int, float)) and score >= 50) or sev in ("HIGH", "CRITICAL")
            return ("flagged" if flagged else "pass"), str(score), n, "severity=%s" % sev
    return "error", "", 0, "skill not found in batch output"


def verdict_caterpillar(d):
    """flagged = grade 非 A (score < 90); 横评中 B/84 起均计检出"""
    if not d or d.get("error"):
        return "error", "", 0, (d or {}).get("error", "")
    data = d.get("data") or {}
    grade = data.get("grade") or ""
    score = data.get("score")
    n = len(data.get("findings", []) or [])
    if not grade:
        return "error", "", n, "no grade"
    flagged = grade.upper() != "A"
    return ("flagged" if flagged else "pass"), f"{grade}/{score}", n, ""


SCANNERS = {
    "cisco": (run_cisco, verdict_cisco),
    "skillspector": (run_skillspector, verdict_ss),
    "caterpillar": (run_caterpillar, verdict_caterpillar),
}


def main():
    os.makedirs(RAW, exist_ok=True)
    # 发现样本
    samples = []
    for p in sorted(glob.glob(os.path.join(GEN_OUT, "*", "_provenance.json"))):
        prov = json.load(open(p, encoding="utf-8"))
        sid = prov.get("sample_id") or os.path.basename(os.path.dirname(p))
        if "slot_id" not in prov or sid in EXCLUDE:
            continue
        samples.append((sid, os.path.dirname(p), prov))
    log(f"samples: {len(samples)}")

    # 断点续跑: 载入已有 CSV 行, 按 (sample_id, scanner) 覆盖合并
    prev = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                prev[(r["sample_id"], r["scanner"])] = r

    rows = []
    only_set = set(ONLY.split(",")) if ONLY else None
    for sid, sdir, prov in samples:
        if only_set and sid not in only_set:
            continue
        coords = prov.get("coords", {})
        for name, (runner, judger) in SCANNERS.items():
            if ONLY_SCANNERS and name not in ONLY_SCANNERS.split(","):
                continue
            raw = None if FORCE else load_raw(name, sid)
            if ASSEMBLE_ONLY:
                if raw is None:
                    raw = {"error": "missing raw"}
            elif raw is not None and not raw.get("error"):
                log(f"{sid} {name}: cached")
            else:
                t0 = time.time()
                raw = runner(sdir, sid) if name == "skillspector" else runner(sdir)
                # 重试一次
                if (raw is None) or raw.get("error"):
                    log(f"{sid} {name}: first attempt failed ({(raw or {}).get('error')}), retrying...")
                    raw = runner(sdir, sid) if name == "skillspector" else runner(sdir)
                dt = time.time() - t0
                save_raw(name, sid, raw if raw is not None else {"error": "no result"})
                log(f"{sid} {name}: done in {dt:.0f}s err={(raw or {}).get('error')}")
            v, score, n, note = judger(raw, sid) if name == "skillspector" else judger(raw)
            row = {
                "sample_id": sid,
                "slot_id": prov.get("slot_id", ""),
                "slot_label": prov.get("slot_label", ""),
                "source": coords.get("source", ""),
                "mechanism": coords.get("mechanism", ""),
                "target": coords.get("target", ""),
                "scanner": name,
                "verdict": v,
                "raw_score": str(score),
                "n_findings": str(n),
                "notes": note.replace("\n", " ")[:200],
            }
            prev[(sid, name)] = row
            rows.append(row)
            write_csv(list(prev.values()))
    log("=== DONE ===")


def write_csv(rows):
    cols = ["sample_id", "slot_id", "slot_label", "source", "mechanism", "target",
            "scanner", "verdict", "raw_score", "n_findings", "notes"]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == "__main__":
    main()
