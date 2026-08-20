"""Shared figure style for the JAWS paper.

One scanner = one color, everywhere (Okabe-Ito, colorblind-safe):
  Cisco  #D55E00 vermillion
  SS     #0072B2 blue
  Cat    #009E73 green

apply(scale) sizes fonts for the *display* size: full-width figures are
rendered ~1.13x their source size when placed at textwidth, single-column
figures ~0.75x at columnwidth. Call with scale=1.0 for full-width figures
and scale=1.3 for single-column so all figures render at the same
effective point size.
"""
import matplotlib

C_CISCO = "#D55E00"
C_SS = "#0072B2"
C_CAT = "#009E73"
GREY = "#8C9AA5"
GREY_D = "#5A6A75"
INK = "#1F2833"
BAND = ["#C9D2D8", "#A9B7C0", "#8C9AA5", "#6E818C"]

SCANNER_COLORS = {"cisco": C_CISCO, "ss": C_SS, "cat": C_CAT}


def apply(scale=1.0):
    f = scale
    matplotlib.rcParams.update({
        "font.family": "serif",
        "font.size": 8 * f,
        "axes.titlesize": 8.5 * f,
        "axes.titleweight": "bold",
        "axes.labelsize": 8 * f,
        "xtick.labelsize": 7.2 * f,
        "ytick.labelsize": 7.2 * f,
        "legend.fontsize": 7 * f,
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
