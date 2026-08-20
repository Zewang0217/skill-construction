#!/usr/bin/env python3
"""Reproducible statistics for the JAWS paper, from raw verdict_all.csv only.

One consistent decision rule throughout (recovered reading):
  Cisco : flagged iff is_safe == False OR max_sev in {MEDIUM, HIGH, CRITICAL}
  SS    : flagged iff ss_score parses and > 0        (score > 50 = shipped)
  Cat   : flagged iff cp_n > 0                       (grade != A = shipped)
Scanner-side failures (blank score / null is_safe) count as non-detections;
their counts are reported so the choice is explicit.

Outputs: stats_581.json next to this script.
"""
import csv, json, math, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "skill-construction", "scanners", "eval_results")
SEV = {"MEDIUM", "HIGH", "CRITICAL"}


def load():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "verdict_all.csv"))))
    manifest = json.load(open(os.path.join(HERE, "..", "..", "skill-construction",
                                           "wild-350", "_manifest.json")))
    wild = {s["name"] for s in manifest["samples"]}

    def grp(r):
        if r["sample"] in wild:
            return "wild"
        if r["sample"].startswith("skill-"):
            return "gen"
        return "benign"

    def ss_score(r):
        try:
            return float(r["ss_score"])
        except (TypeError, ValueError):
            return None

    def flags(r, rule="recovered"):
        if rule == "shipped":
            c = r["cisco_is_safe"] == "False"
            s = (ss_score(r) or 0) > 50
            p = r["cp_grade"] not in ("A", "", None)
        else:
            c = r["cisco_is_safe"] == "False" or r["cisco_max_sev"] in SEV
            s = (ss_score(r) or 0) > 0
            p = r["cp_n"] not in ("", None) and int(r["cp_n"]) > 0
        return c, s, p

    return rows, grp, flags, ss_score


def kappa(a, b):
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    rows, grp, flags, ss_score = load()
    mal = [r for r in rows if grp(r) != "benign"]
    ben = [r for r in rows if grp(r) == "benign"]
    out = {"n_malicious": len(mal), "n_benign": len(ben),
           "groups": Counter(grp(r) for r in rows)}

    # per-group detection (recovered)
    for gname, corpus in [("wild", [r for r in mal if grp(r) == "wild"]),
                          ("gen", [r for r in mal if grp(r) == "gen"]),
                          ("mal", mal), ("benign", ben)]:
        d = {}
        for rule in ("recovered", "shipped"):
            cnt = Counter()
            for r in corpus:
                c, s, p = flags(r, rule)
                cnt["cisco"] += c; cnt["ss"] += s; cnt["cat"] += p
            d[rule] = dict(cnt)
        out[f"det_{gname}"] = d

    # combos (recovered + shipped, malicious)
    for rule in ("recovered", "shipped"):
        combos = Counter()
        for r in mal:
            c, s, p = flags(r, rule)
            combos[(("C" if c else "") + ("S" if s else "") + ("P" if p else "")) or "none"] += 1
        out[f"combos_{rule}"] = dict(combos)

    # kappa: 3 pairs x {mal-recovered, mal-shipped, all-recovered}
    res = {}
    for label, corpus, rule in [("mal_recovered", mal, "recovered"),
                                ("mal_shipped", mal, "shipped"),
                                ("all_recovered", rows, "recovered")]:
        C = [flags(r, rule)[0] for r in corpus]
        S = [flags(r, rule)[1] for r in corpus]
        P = [flags(r, rule)[2] for r in corpus]
        res[label] = {"cisco_ss": kappa(C, S), "cisco_cat": kappa(C, P), "ss_cat": kappa(S, P)}
    out["kappa"] = res

    # technical failure counts (malicious)
    out["tech_fail"] = {
        "cisco_null": sum(1 for r in mal if r["cisco_is_safe"] == ""),
        "ss_missing": sum(1 for r in mal if ss_score(r) is None),
    }

    # wild by behavior class / gen by source (recovered)
    wild_b = {}
    for r in mal:
        if grp(r) != "wild":
            continue
        b = r["sample"]  # placeholder, replaced below
    manifest = json.load(open(os.path.join(HERE, "..", "..", "skill-construction",
                                           "wild-350", "_manifest.json")))
    bmap = {s["name"]: s["b_id"] for s in manifest["samples"]}
    agg = {}
    for r in mal:
        if grp(r) != "wild":
            continue
        b = bmap.get(r["sample"], "?")
        a = agg.setdefault(b, {"n": 0, "c": 0, "s": 0, "p": 0})
        c, s, p = flags(r)
        a["n"] += 1; a["c"] += c; a["s"] += s; a["p"] += p
    out["wild_by_b"] = {b: {"n": v["n"], "cisco": v["c"], "ss": v["s"], "cat": v["p"]}
                        for b, v in sorted(agg.items())}

    agg = {}
    for r in mal:
        if grp(r) != "gen":
            continue
        src = r["sample"].split("-")[1] if r["sample"].startswith("skill-") else "?"
        a = agg.setdefault(src, {"n": 0, "c": 0, "s": 0, "p": 0})
        c, s, p = flags(r)
        a["n"] += 1; a["c"] += c; a["s"] += s; a["p"] += p
    out["gen_by_src"] = {s: {"n": v["n"], "cisco": v["c"], "ss": v["s"], "cat": v["p"]}
                         for s, v in sorted(agg.items())}

    # confirmatory arms (from verdict_arm*.csv, shipped decision rules)
    arms = {}
    arm_files = {
        "Arm7 hidden-file": ("verdict_arm7.csv", lambda r: (
            (float(r["ss_score"]) if r["ss_score"] not in ("", "TECH_FAIL") else 0) <= 50, "ss_evade")),
        "Arm11A finding-specialized": ("verdict_arm11.csv", None),
        "Arm10B no-literal": ("verdict_arm10b.csv", None),
        "Arm12 variant-expansion": ("verdict_arm1213.csv", None),
        "Arm13 combination": ("verdict_arm1213.csv", None),
    }
    del arm_files  # arms computed explicitly below for clarity

    def arm_rows(fname, prefix):
        rs = [r for r in csv.DictReader(open(os.path.join(ROOT, fname)))
              if r["sample"].startswith(prefix)]
        return rs

    def ss_ok(r):
        return r["ss_score"] not in ("", "TECH_FAIL")

    a7 = arm_rows("verdict_arm7.csv", "arm7-")
    arms["Arm7"] = {
        "n": len(a7),
        "ss_evade": sum(1 for r in a7 if ss_ok(r) and float(r["ss_score"]) <= 50),
        "ss_zero": sum(1 for r in a7 if ss_ok(r) and float(r["ss_score"]) == 0),
        "cisco_detect": sum(1 for r in a7 if r["cisco_is_safe"] == "False"),
        "cat_detect": sum(1 for r in a7 if r["cp_grade"] != "A"),
    }
    a11a = arm_rows("verdict_arm11.csv", "arm11a-")
    arms["Arm11A"] = {"n": len(a11a),
                      "cisco_detect": sum(1 for r in a11a if r["cisco_is_safe"] == "False"),
                      "ss_detect": sum(1 for r in a11a if ss_ok(r) and float(r["ss_score"]) > 0)}
    a11b = arm_rows("verdict_arm11.csv", "arm11b-")
    arms["Arm11B"] = {"n": len(a11b),
                      "ss_zero": sum(1 for r in a11b if ss_ok(r) and float(r["ss_score"]) == 0),
                      "triple_miss": sum(1 for r in a11b if r["cisco_is_safe"] != "False"
                                         and ss_ok(r) and float(r["ss_score"]) == 0
                                         and int(r["cp_n"] or 0) == 0)}
    a10b = arm_rows("verdict_arm10b.csv", "arm10b-")
    arms["Arm10B"] = {"n": len(a10b),
                      "cat_detect": sum(1 for r in a10b if r["cp_grade"] != "A"),
                      "cisco_detect": sum(1 for r in a10b if r["cisco_is_safe"] == "False"),
                      "ss_valid": sum(1 for r in a10b if ss_ok(r)),
                      "ss_detect": sum(1 for r in a10b if ss_ok(r) and float(r["ss_score"]) > 0),
                      "ss_techfail": sum(1 for r in a10b if not ss_ok(r))}
    a12 = arm_rows("verdict_arm1213.csv", "arm12-")
    arms["Arm12"] = {"n": len(a12),
                     "ss_detect": sum(1 for r in a12 if ss_ok(r) and float(r["ss_score"]) > 50)}
    a13 = arm_rows("verdict_arm1213.csv", "arm13-")
    arms["Arm13"] = {"n": len(a13),
                     "ss_evade": sum(1 for r in a13 if ss_ok(r) and float(r["ss_score"]) <= 50),
                     "ss_zero": sum(1 for r in a13 if ss_ok(r) and float(r["ss_score"]) == 0),
                     "triple_miss": sum(1 for r in a13 if r["cisco_is_safe"] != "False"
                                        and ss_ok(r) and float(r["ss_score"]) == 0
                                        and int(r["cp_n"] or 0) == 0)}
    for k, v in arms.items():
        for kk in ("ss_evade", "ss_detect", "cisco_detect", "cat_detect", "ss_zero", "triple_miss"):
            if kk in v:
                lo, hi = wilson(v[kk], v["n"] if kk != "ss_detect" or k not in ("Arm10B",) else v.get("ss_valid", v["n"]))
                v[kk + "_ci"] = [round(lo, 3), round(hi, 3)]
    out["arms"] = arms

    with open(os.path.join(HERE, "stats_581.json"), "w") as f:
        json.dump(out, f, indent=1, default=dict)
    print(json.dumps({k: v for k, v in out.items() if k not in ("wild_by_b", "gen_by_src")},
                     indent=1, default=dict))


if __name__ == "__main__":
    main()
