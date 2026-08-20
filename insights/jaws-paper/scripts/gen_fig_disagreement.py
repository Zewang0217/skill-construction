#!/usr/bin/env python3
"""Fig: empirical disagreement structure on 581 malicious x 3 scanners.

Panel (a): pairwise Cohen's kappa under three corpus/rule conditions
           -> the statistic itself is unstable; structure is not.
Panel (b): flag-combination distribution (recovered rule, n=581).
Panel (c): detection rate by behavior class (wild) / source axis (generated),
           annotated with cell n -- the 0-100% spread aggregate recall hides.

Data: stats_581.json (from analysis_581.py, itself from verdict_all.csv).
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stats_581.json")))
OUT = os.path.join(HERE, "..", "latex", "fig_disagreement.pdf")

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.titlesize": 8.5,
    "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "figure.dpi": 300, "savefig.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
})
C_SS, C_CI, C_CA = "#0072B2", "#D55E00", "#009E73"
GREY = "#7B8794"

fig = plt.figure(figsize=(7.0, 2.55))
gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.25], wspace=0.42)

# ---------- (a) kappa ----------
ax = fig.add_subplot(gs[0, 0])
pairs = ["Cisco–SS", "Cisco–Cat", "SS–Cat"]
keys = ["cisco_ss", "cisco_cat", "ss_cat"]
conds = [("malicious only, shipped rule", "mal_shipped", GREY, "//"),
         ("malicious only, recovered rule", "mal_recovered", C_CI, None),
         ("mal.+benign, recovered rule", "all_recovered", C_SS, None)]
x = np.arange(len(pairs)); w = 0.26
for i, (lab, key, col, hat) in enumerate(conds):
    vals = [S["kappa"][key][k] for k in keys]
    ax.bar(x + (i - 1) * w, vals, w * 0.92, color=col, hatch=hat,
           edgecolor="white", linewidth=0.4, label=lab)
    for xx, v in zip(x + (i - 1) * w, vals):
        ax.text(xx, v + (0.012 if v >= 0 else -0.03), f"{v:+.2f}",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=6.3, color="#444")
ax.axhline(0, color="#333", lw=0.7)
ax.set_xticks(x); ax.set_xticklabels(pairs)
ax.set_ylabel("pairwise Cohen's κ")
ax.set_ylim(-0.12, 0.58)
ax.set_title("(a) κ depends on corpus and rule", loc="left", fontweight="bold")
ax.legend(loc="upper left", frameon=False, handlelength=1.4, borderpad=0.1)
ax.text(0.0, -0.32, "same 581×3 raw outputs throughout", transform=ax.transAxes,
        fontsize=6.3, color="#666", style="italic")

# ---------- (b) combinations ----------
ax = fig.add_subplot(gs[0, 1])
order = [("CSP", "all three"), ("CS", "Cisco+SS"), ("SP", "SS+Cat"),
         ("S", "SS only"), ("CP", "Cisco+Cat"), ("C", "Cisco only"),
         ("none", "none"), ("P", "Cat only")]
cb = S["combos_recovered"]
labels = [l for _, l in order][::-1]
vals = [cb[k] for k, _ in order][::-1]
cols = [C_SS if l == "all three" else ("#B0BEC5" if l == "none" else GREY)
        for l in labels]
bars = ax.barh(labels, vals, color=cols, edgecolor="white", linewidth=0.4, height=0.62)
for b, v in zip(bars, vals):
    ax.text(v + 5, b.get_y() + b.get_height() / 2, f"{v}", va="center", fontsize=6.8, color="#444")
ax.set_xlabel("skills (n=581)")
ax.set_xlim(0, 430)
ax.set_title("(b) who flags what", loc="left", fontweight="bold")
ax.text(0.0, -0.32, "222/581 (38.2%) missed by ≥1 scanner", transform=ax.transAxes,
        fontsize=6.3, color="#666", style="italic")

# ---------- (c) heatmap ----------
ax = fig.add_subplot(gs[0, 2])
rows = []
for b, v in sorted(S["wild_by_b"].items(), key=lambda kv: -kv[1]["n"]):
    n = v["n"]
    rows.append((f"B{b[1:]} (wild, n={n})",
                 [v["cisco"] / n * 100, v["ss"] / n * 100, v["cat"] / n * 100]))
for s, v in sorted(S["gen_by_src"].items(), key=lambda kv: -kv[1]["n"]):
    n = v["n"]
    rows.append((f"{s.replace('_', ' ')} (gen, n={n})",
                 [v["cisco"] / n * 100, v["ss"] / n * 100, v["cat"] / n * 100]))
M = np.array([r[1] for r in rows])
im = ax.imshow(M, cmap="viridis", vmin=0, vmax=100, aspect="auto")
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Cisco", "SS", "Cat"])
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=6.2)
for i in range(len(rows)):
    for j in range(3):
        pct = M[i, j]
        ax.text(j, i, f"{pct:.0f}", ha="center", va="center", fontsize=6.0,
                color="white" if pct < 55 else "black")
ax.set_title("(c) detection % by class / source", loc="left", fontweight="bold")
cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cbar.ax.tick_params(labelsize=6)
cbar.set_label("%", fontsize=6.5)
ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
