#!/usr/bin/env python3
"""Fig 4: localized detection surface (v7.3).

All 13 wild behavior classes grouped by which scanner collapses.
Group headers as dedicated label rows (no left strip -> no width inflation).
White->deep-blue sequential colormap; adaptive annotation colors.
"""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import apply, INK

apply(scale=1.5)
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stats_581.json")))
OUT = os.path.join(HERE, "..", "latex", "fig_surface.pdf")

BNAME = {
    "B4": "malware delivery", "B2": "cred. theft", "B1": "data exfil.",
    "B9": "priv. escalation", "B3": "remote code exec", "B14": "goal hijacking",
    "B8": "resource abuse", "B12": "instr. override", "B5": "persistence",
    "B10": "role hijack", "B11": "safety bypass", "B15": "content manip.",
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
    ("held by all three", ["B4", "B9", "B2", "B1", "B8"]),
]

labels, M, ns, header_rows = [], [], [], []
gi = 0
for gname, bs in groups:
    header_rows.append(len(labels))   # row index where header sits
    labels.append(gname)
    M.append([0, 0, 0]); ns.append(0)
    for b in bs:
        labels.append(BNAME[b])
        M.append(row(b))
        ns.append(S["wild_by_b"][b]["n"])
M = np.array(M, dtype=float)
ns = np.array(ns)

cmap = LinearSegmentedColormap.from_list(
    "blues75", ["#FFFFFF", "#C6DBEF", "#6BAED6", "#2171B5", "#08306B"])

fig, ax = plt.subplots(figsize=(3.4, 3.55))
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=100, aspect="auto")
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Cisco", "SkillSpector", "Caterpillar"])
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels)

# style header rows (group names) vs data rows
for h in header_rows:
    ax.get_yticklabels()[h].set_fontstyle("italic")
    ax.get_yticklabels()[h].set_fontsize(8.0)
    ax.get_yticklabels()[h].set_color("#5A6A75")
    ax.get_yticklabels()[h].set_fontweight("bold")
# annotate data cells
for i in range(len(labels)):
    if i in header_rows:
        continue
    for j in range(3):
        v = M[i, j]
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9.2,
                color="white" if v > 62 else ("#9AA7B0" if v == 0 else INK),
                fontweight="bold" if v == 0 else "normal")
# separators
for h in header_rows[1:]:
    ax.axhline(h - 0.5, color="white", lw=2.6)

ax.set_title("detection % by wild behavior class", loc="left")
cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.015)
cbar.ax.tick_params(labelsize=7.6, colors=INK); cbar.set_label("%", fontsize=9.2, color=INK)
cbar.outline.set_edgecolor("#C9D2D8")
ax.spines[:].set_visible(False); ax.tick_params(length=0)

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
