#!/usr/bin/env python3
"""Fig 4: localized detection surface (v7.2 redesign).

All 13 wild behavior classes, grouped by which scanner collapses.
- Blues sequential (0-100% monotone quantity; no fluorescent viridis)
- left group strip in neutral grey bands, group names rotated alongside
- white separators between bands; cell values annotated adaptively
"""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import apply, BAND, INK

apply()
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stats_581.json")))
OUT = os.path.join(HERE, "..", "latex", "fig_surface.pdf")

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
    ("held by all", ["B4", "B9", "B2", "B1", "B8"]),
]

rows, bandpos, bands = [], [], []
for gname, bs in groups:
    bandpos.append(len(rows))
    for b in bs:
        rows.append((BNAME[b], row(b), S["wild_by_b"][b]["n"]))
    bands.append((gname, len(bs)))
M = np.array([r[1] for r in rows])

# white -> deep blue, capped before full saturation for readable annotations
cmap = LinearSegmentedColormap.from_list("blues75", ["#FFFFFF", "#C6DBEF", "#6BAED6", "#2171B5", "#08306B"])

fig, ax = plt.subplots(figsize=(3.05, 2.85))
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=100, aspect="auto")
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Cisco", "SkillSpector", "Caterpillar"])
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([f"{r[0]}  ({r[2]})" for r in rows])
for i in range(len(rows)):
    for j in range(3):
        v = M[i, j]
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.4,
                color="white" if v > 62 else ("#9AA7B0" if v == 0 else INK),
                fontweight="bold" if v == 0 else "normal")

# band separators + left strip
for p in bandpos[1:]:
    ax.axhline(p - 0.5, color="white", lw=2.2)
for (_, cnt), p, c in zip(bands, bandpos, BAND):
    ax.add_patch(plt.Rectangle((-0.55, p - 0.5), 0.09, cnt, color=c,
                               transform=ax.get_yaxis_transform(), clip_on=False))
ax.set_title("detection % by wild behavior class", loc="left")
# bands (top->bottom, grey strip): Cat / Cisco / SS collapses / held by all
cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cbar.ax.tick_params(labelsize=6, colors=INK); cbar.set_label("%", fontsize=6.5, color=INK)
cbar.outline.set_edgecolor("#C9D2D8")
ax.spines[:].set_visible(False); ax.tick_params(length=0)

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
