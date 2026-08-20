#!/usr/bin/env python3
"""v7 step 1: Abstract terms, Intro running example, new fig:pipeline (2-layer
concept + L1/L2/L3), new Section 'The Core Idea' with why-necessary table."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)} expected {count}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. Abstract: three-layer terminology ----
rep("We develop a methodology for this conversion: a shared observation language that makes disagreement localizable, a decomposition into \\emph{coverage gaps} and \\emph{operational divergence}, blind-spot hypotheses locked before construction, and adversarial validation.",
    "We develop a methodology for this conversion: a shared observation language that makes disagreement localizable, a three-layer decomposition---a miss can originate in \\emph{coverage} (the input was never collected), \\emph{detection} (the engine cannot recognize it), or \\emph{decision} (the finding was thresholded away)---blind-spot hypotheses locked before construction, and adversarial validation.")

# ---- 2. Intro conversion paragraph: three layers ----
rep("Second, a \\emph{structural decomposition}: localized disagreement separates into \\emph{coverage gaps} (a scanner does not inspect a region at all) and \\emph{operational divergence} (scanners cover the same region but instantiate detection differently).",
    "Second, a \\emph{three-layer decomposition}: every miss originates in exactly one architectural layer---\\emph{coverage} (the input was never collected), \\emph{detection} (the engine cannot recognize the behavior), or \\emph{decision} (the finding exists but is thresholded away).")

# ---- 3. Contributions methodology wording ----
rep("\\item \\textbf{Methodology.} A conversion pipeline: shared observation language $\\rightarrow$ structural decomposition $\\rightarrow$ locked hypotheses $\\rightarrow$ adversarial validation (\\S\\ref{sec:measure}--\\S\\ref{sec:validate}).",
    "\\item \\textbf{Methodology.} A conversion loop: shared observation language $\\rightarrow$ three-layer decomposition (coverage / detection / decision) $\\rightarrow$ locked hypotheses $\\rightarrow$ adversarial validation (\\S\\ref{sec:idea}--\\S\\ref{sec:validate}).")

# ---- 4. New fig:pipeline (Fig 1): concept + three layers ----
old_fig = src[src.find("\\begin{figure*}[t]\n\\centering\n\\begin{tikzpicture}[node distance=3mm and 5mm,"):src.find("\\label{fig:pipeline}\n\\end{figure*}") + len("\\label{fig:pipeline}\n\\end{figure*}")]
assert old_fig, "fig:pipeline block not found"
new_fig = r"""\begin{figure*}[t]
\centering
\begin{tikzpicture}[node distance=4mm and 7mm,
  box/.style={draw=black!40, rounded corners=1pt, font=\scriptsize, align=center, inner sep=3pt},
  plain/.style={font=\scriptsize, align=center},
  arrow/.style={-{Stealth[length=2mm]}, thick, black!60},
  inflow/.style={draw, rounded corners=1pt, font=\scriptsize, align=center, inner sep=3pt, fill=black!5}]

% ============ LEFT: current practice ============
\node[plain, font=\scriptsize\bfseries, black!55] (lp) at (0,4.35) {CURRENT PRACTICE};
\node[inflow, minimum width=16mm] (art) {artifact $X$};
\node[inflow, above right=4mm and 4mm of art] (sa) {Scanner A};
\node[inflow, right=4mm of art] (sb) {Scanner B};
\node[inflow, below right=4mm and 4mm of art] (sc) {Scanner C};
\draw[arrow] (art.east) -- (sa.west); \draw[arrow] (art.east) -- (sb.west); \draw[arrow] (art.east) -- (sc.west);
\node[plain, right=1.5mm of sa] {$\checkmark$};
\node[plain, right=1.5mm of sb] {$\times$};
\node[plain, right=1.5mm of sc] {$\times$};
\node[box, right=9mm of sb, fill=black!5, minimum width=14mm] (kap) {$\kappa$, overlap};
\draw[arrow] (sb.east) -- (kap.west);
\node[box, below=4mm of kap, fill=black!12, text width=30mm] (stop) {``they disagree.''\\ \emph{Evaluation ends here.}};
\draw[arrow] (kap) -- (stop);

% ============ divider ============
\draw[dashed, black!30] ($(art.north west)+(0,1.5mm)$) -- ($(stop.south east)+(0,-1.5mm)$);

% ============ RIGHT: our view ============
\node[inflow, right=36mm of art, minimum width=16mm] (art2) {artifact $X$};
\node[box, right=5mm of art2, fill=blue!8, text width=21mm] (coord) {\textbf{observation space}\\ $(s,m,t)$ coordinate};
\draw[arrow] (art2) -- (coord);

% three layers column
\node[box, right=6mm of coord, fill=orange!12, text width=21mm] (l1) {\textbf{L1 coverage}\\ did it collect the input?};
\node[box, below=2.5mm of l1, fill=orange!12, text width=21mm] (l2) {\textbf{L2 detection}\\ can the engine see it?};
\node[box, below=2.5mm of l2, fill=orange!12, text width=21mm] (l3) {\textbf{L3 decision}\\ is the finding kept?};
\draw[arrow] (coord.east) -- (l1.west);
\draw[arrow] (coord.east) -- ($(l2.west)+(0,0)$);
\draw[arrow] (coord.east) -- (l3.west);

% per-scanner diagnoses
\node[plain, right=4mm of l1, text width=16mm] (d1) {A: \textcolor{green!50!black}{collects}\\ B: \textcolor{red!70!black}{skips dotfiles}\\ C: \textcolor{red!70!black}{n/a}};
\node[plain, right=4mm of l2, text width=16mm] (d2) {A: \textcolor{green!50!black}{semantic}\\ B: \textcolor{red!70!black}{literal only}\\ C: \textcolor{red!70!black}{regex only}};
\node[plain, right=4mm of l3, text width=16mm] (d3) {A: \textcolor{green!50!black}{score kept}\\ B: \textcolor{red!70!black}{MEDIUM dropped}\\ C: \textcolor{red!70!black}{markers dropped}};

\node[box, below=13mm of d2, fill=blue!8, text width=40mm] (hyp) {\textbf{blind-spot hypothesis per scanner, per layer}};
\draw[arrow] (d1.south) -- (hyp.north);
\draw[arrow] (d2.south) -- (hyp.north);
\draw[arrow] (d3.south) -- (hyp.north);
\node[box, below=3mm of hyp, fill=green!10, text width=40mm] (val) {\textbf{locked construction $\rightarrow$ validation $\rightarrow$ mechanism}};
\draw[arrow] (hyp) -- (val);
\node[plain, font=\scriptsize\bfseries, black!55] at ($(coord.north)+(0,4.5mm)$) {OUR VIEW};
\end{tikzpicture}
\caption{\textbf{The same disagreement, read two ways.} Current practice collapses three verdicts on artifact $X$ into a scalar and stops. Our view localizes $X$ in a shared observation space, decomposes each scanner's failure into one architectural layer---coverage (L1), detection (L2), or decision (L3)---derives per-scanner blind-spot hypotheses, and validates them by construction locked before the fact.}
\label{fig:pipeline}
\end{figure*}"""
src = src.replace(old_fig, new_fig)

# ---- 5. New Section 2: The Core Idea (inserted after Intro, before Background) ----
core_idea = r"""
% ============================================================
\section{The Core Idea: Disagreement as Evidence}
\label{sec:idea}

An automated security analysis is a pipeline: it \emph{collects} an input, \emph{detects} patterns in it, and \emph{decides} what to report. Each stage can fail independently, and the stages fail differently across analyses. This gives the paper's central object a precise shape:

\begin{quote}
\textbf{Three-layer decomposition.} Every miss originates in exactly one layer:
\emph{L1 coverage} --- the relevant input was never collected;
\emph{L2 detection} --- the input was collected but the engine cannot recognize the behavior;
\emph{L3 decision} --- the engine produced a finding but the decision rule discarded it.
\end{quote}

The layers are not metaphorical; they are separable by construction. A payload placed in a file the collector skips evades at L1 regardless of engine strength. A behavior expressed without the lexical or semantic surface an engine matches evades at L2. A finding demoted below a severity threshold evades at L3. Each layer implies a different fix (collect more inputs; change engines; change thresholds), a different attack strategy (hide the file; change the expression; suppress the severity), and therefore a different, falsifiable blind-spot hypothesis.

Why is a new instrument needed to reach this decomposition? Because the standard tools operate at the wrong level of aggregation (Table~\ref{tab:why}):

\begin{table}[t]
\caption{What each approach can do with disagreement. ``Localize'' = say where in the threat space the disagreement arises; ``explain'' = attribute it to a mechanism in the analysis; ``predict'' = derive the failure before any new artifact is built.}
\label{tab:why}
\small
\begin{tabular}{@{}lccc@{}}
\toprule
 & Localize & Explain & Predict \\
\midrule
Aggregate recall & $\times$ & $\times$ & $\times$ \\
Pairwise $\kappa$ / overlap & $\times$ & $\times$ & $\times$ \\
Manual post-hoc audit & \checkmark & \checkmark & $\times$ \\
\textbf{Our loop} & \checkmark & \checkmark & \checkmark\ (locked) \\
\bottomrule
\end{tabular}
\end{table}

Recall and $\kappa$ compress disagreement to a scalar; scalar differences cannot say \emph{where} the analyses diverge. A manual audit can, after seeing the failures---but post-hoc explanation cannot distinguish prediction from rationalization. The loop we instantiate---observe, localize, decompose by layer, hypothesize, lock, construct, validate---is the minimal pipeline that does all three, and its predictions are checkable against a locking protocol that fixes hypotheses before construction.

"""
rep("\n% ============================================================\n\\section{Background and Motivation}",
    "\n" + core_idea + "% ============================================================\n\\section{Instantiation: Agent-Skill Scanners}")

open('main.tex','w').write(src)
print("v7 step 1 OK")
