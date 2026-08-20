#!/usr/bin/env python3
"""v7.1 (GPT round 2): contribution hierarchy, Where-Why-WhatNext-IsItTrue
backbone, inferential positioning, top-down/bottom-up inference, §6 flip
(ledger first, hidden-file as representative case), surface figure."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. Contribution block: three levels ----
old = """\\noindent\\textbf{Contributions.} This is an idea paper: one general claim, a methodology, an instantiation, and early evidence.
\\begin{itemize}
  \\item \\textbf{Idea.} Disagreement among automated security analyses is analytical evidence, not merely an evaluation outcome.
  \\item \\textbf{Methodology.} A conversion loop: shared observation language $\\rightarrow$ three-layer decomposition (coverage / detection / decision) $\\rightarrow$ locked hypotheses $\\rightarrow$ adversarial validation (\\S\\ref{sec:idea}--\\S\\ref{sec:validate}).
  \\item \\textbf{Instantiation.} Agent-skill security scanners, studied via a three-dimensional attack-coordinate space.
  \\item \\textbf{Early evidence.} 581 malicious skills and 500 benign references under three scanners; 79 confirmatory constructions (of 129 built) testing hypotheses specified before construction; source-level mechanism tracing.
\\end{itemize}"""
new = """\\noindent\\textbf{Contributions.} Three, in strict hierarchy:
\\begin{itemize}
  \\item \\textbf{Core idea.} Disagreement among automated security analyses is not merely an evaluation outcome: projected into a shared observation space, its structure becomes evidence about the analyses themselves---from which falsifiable blind-spot predictions can be derived.
  \\item \\textbf{Methodology.} A loop that converts disagreement into such predictions: shared observation language (\\emph{where} do they disagree?) $\\rightarrow$ three-layer decomposition, coverage/detection/decision (\\emph{why}?) $\\rightarrow$ locked hypotheses (\\emph{what will they miss next?}) $\\rightarrow$ adversarial construction (\\emph{is the prediction true?}).
  \\item \\textbf{Demonstration.} An end-to-end instantiation on agent-skill security scanners: 581 malicious skills, 500 benign references, three scanners, six locked hypotheses with confirmed, partial, and rejected outcomes, traced to source-level mechanisms.
\\end{itemize}"""
rep(old, new)

# Results paragraph: demote bypass numbers to evidence voice
rep("""\\noindent\\textbf{Results.} Hidden-file payloads evade SkillSpector on 14/15 samples (its build context skips dotfiles). Expression-layer variants evade Cisco on 6/6 (its pipeline requires literal command surfaces). Combined strategies evade SkillSpector on 5/5.
A regex-only reference tool is blind to all 10 semantic variants, showing blind spots deepen as detection grows more primitive.""",
"""\\noindent\\textbf{Results.} The loop's predictions held where its evidence was architectural: locked hypotheses predicted hidden-file evasion of SkillSpector (observed 14/15), regex blindness to semantic phrasing (10/10), and Cisco's failure on finding-family variants (6/6); one hypothesis was partially confirmed and one was rejected by its own control experiment. Each confirmed prediction traces to a named source-level mechanism. The bypasses are not the contribution; they are the evidence that the conversion works.""")

# ---- 2. §2 backbone sentence ----
rep("Why is a new instrument needed to reach this decomposition? Because the standard tools operate at the wrong level of aggregation (Table~\\ref{tab:why}):",
    "The paper's progression is the same ladder: the observation space answers \\emph{where} scanners disagree (\\S\\ref{sec:measure}), the three layers answer \\emph{why} (\\S\\ref{sec:explain}), locked hypotheses answer \\emph{what they will miss next} (\\S\\ref{sec:hypotheses}), and construction answers \\emph{whether the prediction is true} (\\S\\ref{sec:validate}). Why is a new instrument needed to climb it? Because the standard tools operate at the wrong level of aggregation (Table~\\ref{tab:why}):")

# ---- 3. §3 inferential positioning at end of Orthogonality ----
rep("as synonymous scanner vocabularies merge while distinctions survive.",
    "as synonymous scanner vocabularies merge while distinctions survive. The point of the space is not taxonomic completeness; its role here is \\emph{inferential}: once scanner outputs are projected into a common coordinate system, disagreement becomes evidence from which hypotheses about missing coverage and operational boundaries can be derived---the input to everything that follows.")

# ---- 4. §5.1 Two Evidence Sources -> top-down / bottom-up ----
rep("""\\subsection{Two Evidence Sources}
\\emph{Type A (coordinate-coverage evidence).} Projecting every mapped category onto the space yields a scanner-by-coordinate coverage matrix. The matrix makes absence explicit: of the 400 cells in the cross-product of our observed dimension values, only 43 are occupied by any documented threat, 318 are credible blanks (constructible but undocumented), and 39 are infeasible. A coordinate uncovered or weakly covered by a scanner's mapped categories yields the hypothesis that the scanner will miss attacks occupying that coordinate, and the 318 credible blanks delimit exactly where such hypotheses can be tested.

\\emph{Type B (scanner-architecture evidence).} An implementation property produces a mechanistic limitation. Reading SkillSpector's source shows that its build context skips dotfiles; this produces the hypothesis that hidden-file payloads escape analysis.""",
"""\\subsection{Two Directions of Inference}
The loop draws blind-spot hypotheses from two directions, and both are needed.

\\emph{Top-down (coordinate-space evidence).} Projecting every mapped category onto the space yields a scanner-by-coordinate coverage matrix. The matrix makes absence explicit: of the 400 cells in the cross-product of our observed dimension values, only 43 are occupied by any documented threat, 318 are credible blanks (constructible but undocumented), and 39 are infeasible. A coordinate uncovered or weakly covered by a scanner yields the hypothesis that it will miss attacks there---and the blanks delimit exactly where such hypotheses can be tested. This direction is what the observation space uniquely enables; no amount of source reading enumerates the space of unoccupied coordinates.

\\emph{Bottom-up (architecture evidence).} An implementation property produces a mechanistic limitation. Reading SkillSpector's source shows that its build context skips dotfiles; this produces the hypothesis that hidden-file payloads escape analysis. This direction finds \\emph{specific} mechanisms but does not, by itself, say where else to look.

The directions converge at the same protocol: hypothesis $\\rightarrow$ lock $\\rightarrow$ construction $\\rightarrow$ validation. Neither is privileged; the ledger (\\S\\ref{sec:validate}) reports each prediction's provenance.""")

# Type B reference in §4 step list

# ---- 5. fig:disagg caption: drop panel (c) ----
rep("\\caption{\\textbf{Empirical disagreement structure on $581$ malicious skills $\\times$ three scanners, from one reproducible rule.} (a)~Pairwise Cohen's $\\kappa$ computed from the same raw outputs under three corpus/rule choices: the statistic swings from $-0.01$ to $+0.44$; none of these scalars localizes the disagreement. (b)~Flag-combination distribution: misses concentrate in reproducible combinations, not noise. (c)~Detection rate by wild behavior class and generated source axis (cell $n$ in labels): per-class detection spans 0--100\\%, the spread that aggregate recall conceals.}",
    "\\caption{\\textbf{The aggregate view, dismantled.} (a)~Pairwise Cohen's $\\kappa$ from the \\emph{same} $581{\\times}3$ raw outputs under three corpus/rule choices: the statistic swings from $-0.01$ to $+0.44$; no scalar in this range localizes the disagreement. (b)~Flag combinations: misses concentrate in reproducible patterns (Caterpillar sole miss: 118), not noise. Where those misses live in the threat space is Fig.~\\ref{fig:surface}'s question.}")

# ---- 6. refs to panel (c) -> surface figure ----
rep("and per-class detection spans 0--100\\% (Fig.~\\ref{fig:disagg}c).",
    "and across the 13 wild behavior classes, per-class detection spans 0--100\\% (Fig.~\\ref{fig:surface}).")
rep("Figure~\\ref{fig:disagg}c localizes them empirically: wild behavior classes and generated source slices where one scanner collapses while others hold (remote-code-execution class: Cisco 14\\% vs.\\ SkillSpector 57\\%; runtime-environment sources: Cisco 33\\%).",
    "Figure~\\ref{fig:surface} localizes them empirically: all 13 wild behavior classes, sorted not by frequency but by \\emph{which scanner collapses}---Caterpillar folds on instruction-level classes (goal hijacking, instruction override: 0\\%), Cisco folds on deep-disguise remote code execution (14\\%), SkillSpector folds on content manipulation and reverse shell (0\\%), while the mass of the corpus (malware delivery) is held by all three.")

# insert surface figure after tab:disagg block
rep("""\\begin{figure}[t]
\\centering
\\includegraphics[width=\\columnwidth]{fig_validation.pdf}""",
"""\\begin{figure}[t]
\\centering
\\includegraphics[width=\\columnwidth]{fig_surface.pdf}
\\caption{\\textbf{Localized detection surface: disagreement is structured.} Detection rate per wild behavior class (all 13 classes, uniform rule, $n$ in labels), sorted by which scanner collapses rather than by frequency. Three scanner-specific failure bands appear---Caterpillar on instruction-level classes, Cisco on deep-disguise RCE, SkillSpector on content manipulation and reverse shell---above a base of classes all three hold. An aggregate recall number averages over these bands and erases them.}
\\label{fig:surface}
\\end{figure}

\\begin{figure}[t]
\\centering
\\includegraphics[width=\\columnwidth]{fig_validation.pdf}""")

open('main.tex','w').write(src)
print("v7.1 part A OK")
