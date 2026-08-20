#!/usr/bin/env python3
"""Fig: real-market disagreement census (project origin data, week-0).

Panel (a): 6-scanner pairwise kappa matrix on 136 cross-platform verified
           skills -- every pair <= 0.244, most ~0.
Panel (b): consensus distribution: how many scanners flag a wild skill.

Data: skills-scanner-study/data/views/stats/{cohen_kappa_verified,
consensus_distribution_verified}.csv  (raw, no ground truth).
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

STATS = "/mnt/d/zewang/paper/skills-scanner-study/data/views/stats"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "latex", "fig_census.pdf")

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.titlesize": 8.5,
    "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "figure.dpi": 300, "savefig.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
})

SHORT = {"skillspector": "SS", "virustotal": "VT", "static_analysis": "Static",
         "snyk": "Snyk", "socket": "Socket", "agent_trust_hub": "ATH"}
ORDER = ["skillspector", "virustotal", "static_analysis", "snyk", "socket", "agent_trust_hub"]

# ---- (a) kappa matrix ----
K = np.full((6, 6), np.nan)
seen = {}
with open(os.path.join(STATS, "cohen_kappa_verified.csv")) as f:
    for row in csv.DictReader(f):
        a, b, k = row["scanner_a"], row["scanner_b"], float(row["kappa"])
        seen[(a, b)] = k
for i, a in enumerate(ORDER):
    for j, b in enumerate(ORDER):
        if (a, b) in seen:
            K[i, j] = seen[(a, b)]

# ---- (b) consensus ----
labels, counts, pcts = [], [], []
with open(os.path.join(STATS, "consensus_distribution_verified.csv")) as f:
    for row in csv.DictReader(f):
        labels.append(int(row["n_scanners_flagged"]))
        counts.append(int(row["n_skills"]))
        pcts.append(float(row["pct"]))

fig = plt.figure(figsize=(3.4, 2.75))
gs = fig.add_gridspec(2, 1, height_ratios=[1.15, 1.0], hspace=0.62)

ax = fig.add_subplot(gs[0])
im = ax.imshow(np.ma.masked_invalid(K), cmap="RdYlBu_r", vmin=-0.1, vmax=0.35)
ax.set_xticks(range(6)); ax.set_yticks(range(6))
ax.set_xticklabels([SHORT[s] for s in ORDER], fontsize=6.8)
ax.set_yticklabels([SHORT[s] for s in ORDER], fontsize=6.8)
for i in range(6):
    for j in range(6):
        if not np.isnan(K[i, j]):
            v = K[i, j]
            ax.text(j, i, f"{v:.2f}".replace("0.", "."), ha="center", va="center",
                    fontsize=6.0, color="white" if v > 0.28 or v < -0.02 else "black")
ax.set_title("(a) pairwise κ, 136 skills × 6 scanners", loc="left", fontweight="bold")
ax.spines[:].set_visible(False)
ax.tick_params(length=0)
cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
cbar.ax.tick_params(labelsize=6)

ax = fig.add_subplot(gs[1])
cols = ["#B0BEC5"] + ["#7B8794"] * 3 + ["#0072B2", "#0072B2"]
bars = ax.bar([str(l) for l in labels], pcts, color=cols, edgecolor="white", linewidth=0.4, width=0.62)
for b, p, c in zip(bars, pcts, counts):
    ax.text(b.get_x() + b.get_width() / 2, p + 1.2, f"{p:.0f}%", ha="center", fontsize=6.4, color="#444")
ax.set_xlabel("scanners flagging the same wild skill")
ax.set_ylabel("% of skills")
ax.set_ylim(0, 48)
ax.set_title("(b) consensus distribution (n=136)", loc="left", fontweight="bold")
ax.text(0.02, 0.88, "only 5.9% flagged by ≥4\n16.2% flagged by none",
        transform=ax.transAxes, fontsize=6.2, color="#666", style="italic")

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
