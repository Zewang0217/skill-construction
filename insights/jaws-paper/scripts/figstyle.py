"""Shared figure style for the JAWS paper.

One scanner = one color, everywhere (Okabe-Ito, colorblind-safe):
  Cisco  #D55E00 vermillion
  SS     #0072B2 blue
  Cat    #009E73 green
Neutral greys for baselines; semantic accents reserved.

All matplotlib figures import this module; all single-column figures are
3.35in wide, full-width 7.0in, fonts >=6pt at final size.
"""
import matplotlib

C_CISCO = "#D55E00"
C_SS = "#0072B2"
C_CAT = "#009E73"
GREY = "#8C9AA5"      # neutral baseline
GREY_D = "#5A6A75"    # darker grey (annotation)
INK = "#1F2833"       # near-black text
BAND = ["#C9D2D8", "#A9B7C0", "#8C9AA5", "#6E818C"]  # group strip (light->dark)

SCANNER_COLORS = {"cisco": C_CISCO, "ss": C_SS, "cat": C_CAT}

def apply():
    matplotlib.rcParams.update({
        "font.family": "serif",
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 8,
        "xtick.labelsize": 7.2,
        "ytick.labelsize": 7.2,
        "legend.fontsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": INK,
        "axes.linewidth": 0.7,
        "xtick.color": INK, "ytick.color": INK,
        "text.color": INK, "axes.labelcolor": INK,
    })
