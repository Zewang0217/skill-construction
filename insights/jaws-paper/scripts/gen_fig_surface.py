#!/usr/bin/env python3
"""Fig 4: localized detection surface (wild corpus, one consistent rule).

All 13 wild behavior classes (MalSkillBench WILD stratification), sorted not
by frequency but by *which scanner collapses* -- the sorting is the claim:
disagreement concentrates into scanner-specific failure bands.

Cell = detection % under the uniform rule (from analysis_581.py wild_by_b);
n in the row label. B-class names per week-7 DATA_ANALYSIS_GROUPED.
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stats_581.json")))
OUT = os.path.join(HERE, "..", "latex", "fig_surface.pdf")

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 7.2, "ytick.labelsize": 6.8,
    "figure.dpi": 300, "savefig.dpi": 300,
})

BNAME = {
    "B4": "malware delivery", "B2": "credential theft", "B1": "data exfiltration",
    "B9": "privilege escalation", "B3": "remote code exec", "B14": "goal hijacking",
    "B8": "resource abuse", "B12": "instruction override", "B5": "persistence",
    "B10": "role hijack", "B11": "safety bypass", "B15": "content manipulation",
    "B6": "reverse shell",
}

def row(b):
    d = S["wild_by_b"][b]
    n = d["n"]
    return [d["cisco"] / n * 100, d["ss"] / n * 100, d["cat"] / n * 100]

groups = [
    ("Caterpillar collapses", ["B14", "B12", "B10", "B11"]),
    ("Cisco collapses", ["B3", "B5"]),
    ("SkillSpector collapses", ["B15", "B6"]),
    ("no single collapse", ["B4", "B9", "B2", "B1", "B8"]),
]

rows, bandpos, bands = [], [], []
for gname, bs in groups:
    bandpos.append(len(rows))
    for b in bs:
        rows.append((f"{BNAME[b]}  n={S['wild_by_b'][b]['n']}", row(b)))
    bands.append((gname, len(bs)))
M = np.array([r[1] for r in rows])

fig, ax = plt.subplots(figsize=(3.35, 3.0))
im = ax.imshow(M, cmap="viridis", vmin=0, vmax=100, aspect="auto")
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Cisco", "SkillSpector", "Caterpillar"])
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows])
for i in range(len(rows)):
    for j in range(3):
        v = M[i, j]
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.4,
                color="white" if v < 55 else "black")
for p in bandpos[1:]:
    ax.axhline(p - 0.5, color="white", lw=1.8)
for (gname, cnt), p in zip(bands, bandpos):
    ax.text(-0.78, p + cnt / 2 - 0.5, gname, transform=ax.get_yaxis_transform(),
            rotation=90, va="center", ha="right", fontsize=6.6, fontweight="bold", color="#444")
ax.set_title("detection % by wild behavior class", loc="left", fontweight="bold")
cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
cbar.ax.tick_params(labelsize=6); cbar.set_label("%", fontsize=6.5)
ax.spines[:].set_visible(False); ax.tick_params(length=0)

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
