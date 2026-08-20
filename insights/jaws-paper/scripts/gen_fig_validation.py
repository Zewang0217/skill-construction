#!/usr/bin/env python3
"""Fig: confirmatory validation as rates with Wilson 95% CIs.

Each row: one locked hypothesis -> construction family -> target scanner's
failure rate (or, for the negative control, the detection rate).
CIs are Wilson score intervals; n is printed per row.
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stats_581.json")))
A = S["arms"]
OUT = os.path.join(HERE, "..", "latex", "fig_validation.pdf")

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7,
    "figure.dpi": 300, "savefig.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
})
C_SS, C_CI, C_CA, GR = "#0072B2", "#D55E00", "#009E73", "#666666"

def w(k, n):
    p = k / n
    lo, hi = A["Arm7"]["ss_evade_ci"]  # placeholder, recompute below
    # Wilson recompute
    z = 1.96; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return max(0.0, c-h), min(1.0, c+h)

rows = [  # label, k, n, color, marker, semantics
    ("Arm7: hidden file → SS evades",        A["Arm7"]["ss_evade"],   A["Arm7"]["n"],         C_SS, "o", "fail"),
    ("Arm11A: no literal trigger → Cisco evades", A["Arm11A"]["n"] - A["Arm11A"]["cisco_detect"], A["Arm11A"]["n"], C_CI, "o", "fail"),
    ("Arm10B: tool semantics → Cat evades",  A["Arm10B"]["n"] - A["Arm10B"]["cat_detect"], A["Arm10B"]["n"], C_CA, "o", "fail"),
    ("Arm13: stacked weak mechanisms → SS partial bypass", A["Arm13"]["ss_evade"], A["Arm13"]["n"], C_SS, "o", "fail"),
    ("Arm11B: wild pipeline pattern → SS score 0", A["Arm11B"]["ss_zero"], A["Arm11B"]["n"], C_SS, "o", "fail"),
    ("Arm13: combination → all three miss",  A["Arm13"]["triple_miss"], A["Arm13"]["n"],       GR,  "s", "fail"),
    ("Arm12 (negative control): variant family → SS detects", A["Arm12"]["ss_detect"], A["Arm12"]["n"], "black", "o", "detect"),
]

fig, ax = plt.subplots(figsize=(3.35, 2.5))
ys = np.arange(len(rows))[::-1]
for y, (lab, k, n, col, mk, sem) in zip(ys, rows):
    p = k / n
    lo, hi = w(k, n)
    ax.plot([lo*100, hi*100], [y, y], color=col, lw=1.1, alpha=0.85)
    face = "white" if sem == "detect" else col
    ax.plot(p*100, y, mk, color=col, mfc=face, mec=col, ms=5, mew=1.2, zorder=3)
    ax.text(hi*100 + 3, y, f"{k}/{n}", va="center", fontsize=6.6, color="#444")
ax.set_yticks(ys)
ax.set_yticklabels([r[0] for r in rows], fontsize=6.4)
ax.set_xlim(0, 118)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("rate (%), Wilson 95% CI")
ax.axvline(50, color="#ccc", lw=0.6, ls=":")
ax.set_title("Confirmatory constructions: predicted failures\nwith sample sizes and uncertainty",
             loc="left", fontsize=8)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
