#!/usr/bin/env python3
"""Fig census (v7.2 redesign): aligned two-panel layout.

(a) pairwise kappa matrix (values annotated; no colorbar squeezing the panel)
(b) consensus distribution bars
Both panels equal width, titles aligned at the same height.
"""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import apply, GREY, C_SS, INK

apply(scale=1.15)
STATS = "/mnt/d/zewang/paper/skills-scanner-study/data/views/stats"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "latex", "fig_census.pdf")

SHORT = {"skillspector": "SS", "virustotal": "VT", "static_analysis": "Static",
         "snyk": "Snyk", "socket": "Socket", "agent_trust_hub": "ATH"}
ORDER = ["skillspector", "virustotal", "static_analysis", "snyk", "socket", "agent_trust_hub"]

K = np.full((6, 6), np.nan)
with open(os.path.join(STATS, "cohen_kappa_verified.csv")) as f:
    for row in csv.DictReader(f):
        K[ORDER.index(row["scanner_a"]), ORDER.index(row["scanner_b"])] = float(row["kappa"])

labels, pcts, counts = [], [], []
with open(os.path.join(STATS, "consensus_distribution_verified.csv")) as f:
    for row in csv.DictReader(f):
        labels.append(int(row["n_scanners_flagged"]))
        pcts.append(float(row["pct"]))
        counts.append(int(row["n_skills"]))

fig = plt.figure(figsize=(3.35, 3.2))
gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.78,
                      left=0.13, right=0.99, top=0.94, bottom=0.10)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])

# ---- (a) kappa matrix, annotated, colorbar-free ----
im = ax1.imshow(K, cmap="RdBu_r", vmin=-0.15, vmax=0.35, aspect="auto")
ax1.set_xticks(range(6)); ax1.set_yticks(range(6))
ax1.set_xticklabels([SHORT[s] for s in ORDER], fontsize=7.7)
ax1.set_yticklabels([SHORT[s] for s in ORDER], fontsize=7.7)
for i in range(6):
    for j in range(6):
        if not np.isnan(K[i, j]):
            v = K[i, j]
            ax1.text(j, i, f"{v:.2f}".replace("0.", "."), ha="center", va="center",
                     fontsize=7.2, color="white" if v > 0.24 or v < -0.05 else INK)
ax1.set_title("(a)  pairwise κ  (136 skills × 6 scanners)", loc="left")
ax1.spines[:].set_visible(False); ax1.tick_params(length=0)

# ---- (b) consensus distribution ----
cols = [GREY] * 6
cols[4] = C_SS; cols[5] = C_SS
bars = ax2.bar([str(l) for l in labels], pcts, color=cols, edgecolor="white",
               linewidth=0.5, width=0.62)
for b, p, c in zip(bars, pcts, counts):
    ax2.text(b.get_x() + b.get_width() / 2, p + 1.4, f"{p:.0f}%", ha="center",
             fontsize=7.4, color=INK)
ax2.set_xlabel("scanners flagging the same wild skill", fontsize=7.3)
ax2.set_ylabel("% of skills", fontsize=7.3)
ax2.set_ylim(0, 50)
ax2.set_title("(b)  consensus distribution  (n = 136)", loc="left")
ax2.text(0.30, 0.70, "only 5.9% flagged by ≥4\n16.2% flagged by none",
         transform=ax2.transAxes, fontsize=7.3, color="#5A6A75", style="italic")

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
