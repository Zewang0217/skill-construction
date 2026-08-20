#!/usr/bin/env python3
"""Fig 3 v7.1: two panels only (c was split into its own figure).

(a) kappa instability dot-range (3 pairs x 3 corpus/rule conditions).
(b) UpSet-style flag-combination matrix (n=581).

Data: stats_581.json.
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import apply, C_SS, C_CISCO, C_CAT, GREY, INK
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stats_581.json")))
OUT = os.path.join(HERE, "..", "latex", "fig_disagreement.pdf")

apply()
C_SS, C_CI, GREY = C_SS, C_CISCO, GREY

fig = plt.figure(figsize=(7.0, 2.1))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.15], wspace=0.34)

# ---------- (a) kappa dot-range ----------
ax = fig.add_subplot(gs[0, 0])
pairs = ["Cisco–SS", "Cisco–Cat", "SS–Cat"]
keys = ["cisco_ss", "cisco_cat", "ss_cat"]
conds = [("shipped rule", "mal_shipped", GREY, "o"),
         ("uniform rule", "mal_recovered", C_CI, "s"),
         ("+ benign corpus", "all_recovered", C_SS, "^")]
for y, pair in enumerate(pairs[::-1]):
    vals = [S["kappa"][k][keys[y]] for _, k, _, _ in conds]
    lo, hi = min(vals), max(vals)
    ax.plot([lo, hi], [y, y], color="#ccc", lw=1.4, zorder=1)
    for (lab, key, col, mk), v in zip(conds, vals):
        ax.plot(v, y, mk, color=col, ms=5.5, mec="white", mew=0.5, zorder=3)
ax.axvline(0, color="#333", lw=0.7)
ax.set_yticks(range(3)); ax.set_yticklabels(pairs[::-1])
ax.set_xlim(-0.1, 0.52)
ax.set_xlabel("pairwise Cohen's κ")
ax.set_title("(a) same outputs, three κ values", loc="left", fontweight="bold")
handles = [Line2D([], [], color=c, marker=m, ls="", label=l, ms=5) for l, _, c, m in conds]
ax.legend(handles=handles, loc="lower right", frameon=False, handletextpad=0.2)
ax.text(0.0, -0.36, "581 malicious ×3; third condition adds 500 benign", transform=ax.transAxes,
        fontsize=6.2, color="#666", style="italic")

# ---------- (b) UpSet ----------
ax = fig.add_subplot(gs[0, 1])
combos = S["combos_recovered"]
rows = [("CSP", [1, 1, 1]), ("CS", [1, 1, 0]), ("SP", [0, 1, 1]), ("CP", [1, 0, 1]),
        ("S", [0, 1, 0]), ("C", [1, 0, 0]), ("P", [0, 0, 1]), ("none", [0, 0, 0])]
vals = [combos[k] for k, _ in rows]
order = np.argsort(vals)[::-1]
rows = [rows[i] for i in order]; vals = [vals[i] for i in order]

axm = ax.inset_axes([0.0, 0.30, 0.60, 0.70])
axb = ax.inset_axes([0.0, 0.02, 0.60, 0.24])
axh = ax.inset_axes([0.66, 0.30, 0.32, 0.70])
ax.axis("off")

n = len(rows)
for r, (name, bits) in enumerate(rows):
    y = n - 1 - r
    if all(b == 0 for b in bits):
        axm.plot(range(3), [y] * 3, "o", ms=3.4, mfc="none", mec="#B0BEC5", mew=0.8)
    else:
        on = [i for i, b in enumerate(bits) if b]
        off = [i for i, b in enumerate(bits) if not b]
        if len(on) > 1:
            axm.plot(on, [y] * len(on), color="#333", lw=1.1, zorder=1)
        axm.plot(on, [y] * len(on), "o", ms=4.2, color=C_SS, mec="white", mew=0.5, zorder=3)
        axm.plot(off, [y] * len(off), "o", ms=3.4, mfc="none", mec="#B0BEC5", mew=0.8, zorder=2)
axm.set_xlim(-0.5, 2.5); axm.set_ylim(-0.6, n - 0.4)
axm.set_xticks(range(3)); axm.set_xticklabels(["Cisco", "SS", "Cat"], fontsize=7)
axm.set_yticks([]); axm.tick_params(length=0)
for s in axm.spines.values(): s.set_visible(False)
for r, v in enumerate(vals):
    axb.text(n - 1 - r - (n - 1) / 2, 0.5, str(v), ha="center", va="center", fontsize=6.4, color="#444")
axb.set_xlim(-0.5, n - 0.5); axb.set_ylim(0, 1); axb.axis("off")

axh.barh(range(n), vals[::-1], color=[C_SS if v == max(vals) else GREY for v in vals[::-1]],
         edgecolor="white", linewidth=0.4, height=0.62)
for y, v in enumerate(vals[::-1]):
    axh.text(v + 8, y, str(v), va="center", fontsize=6.6, color="#444")
axh.set_yticks([]); axh.set_xlim(0, 430)
axh.tick_params(axis="x", labelsize=6.2)
axh.set_xlabel("skills", fontsize=7)
for s in ["top", "right"]: axh.spines[s].set_visible(False)
ax.set_title("(b) who flags what (n=581)", loc="left", fontweight="bold")
ax.text(0.0, -0.10, "222/581 (38.2%) missed by at least one scanner", transform=ax.transAxes,
        fontsize=6.2, color="#666", style="italic")

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
