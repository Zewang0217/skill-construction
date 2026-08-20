#!/usr/bin/env python3
"""v7 step 2: T3 datasets table + census figure into Instantiation;
L1/L2/L3 terminology through §4-§6; ledger upgrade."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. Instantiation: datasets table + census fig after scanner table ----
rep("""\\begin{table}[t]
\\caption{The three studied scanners. ``Decision rule'' is what the raw output reduces to for an allow/block decision: each rule is later implicated in a distinct blind spot.}""",
"""\\begin{figure}[t]
\\centering
\\includegraphics[width=\\columnwidth]{fig_census.pdf}
\\caption{\\textbf{Disagreement is the norm in the wild.} A market census (project week-0 data, no ground truth; scanner set distinct from \\S\\ref{sec:explain}): on 136 skills verified across platforms, all six public scanners' pairwise Cohen's $\\kappa\\le 0.244$ with most near zero (a), and only 5.9\\% of skills are flagged by four or more scanners (b). On the full 1{,}082-skill census, 260 of 445 flagged skills are flagged by exactly one scanner. Disagreement at this scale is not noise to average away; it is the ecosystem's default output.}
\\label{fig:census}
\\end{figure}

\\begin{table}[t]
\\caption{The three studied scanners. ``Decision rule'' is what the raw output reduces to for an allow/block decision: each rule is later implicated in a distinct blind spot.}""")

# datasets table appended after scanner table block
rep("""\\bottomrule
\\end{tabular}
\\end{table}

\\textbf{Threat model.}""",
"""\\bottomrule
\\end{tabular}
\\end{table}

\\begin{table}[t]
\\caption{Four corpora, four roles. Each row is a distinct evidential unit; no number crosses rows. Census scanners: SkillSpector, Snyk, Socket, ATH, VirusTotal, static analysis. Main-loop scanners: the three of Table~\\ref{tab:scanners}.}
\\label{tab:datasets}
\\small
\\begin{tabular}{@{}p{2.7cm}p{1.5cm}p{3.6cm}@{}}
\\toprule
Corpus & $n$ & Role in this paper \\
\\midrule
Market census (wild, unlabeled) & 1{,}082 & Motivation: disagreement is pervasive (Fig.~\\ref{fig:census}) \\\\
Malicious corpus & 581 & Observed disagreement: 350 wild + 231 coordinate-generated \\\\
Benign references & 500 + 4{,}000 & False-positive mirror (500 in-corpus; 4{,}000 official MalSkillBench audit) \\\\
Constructions & 129 (79 conf.) & Prediction validation: Arms 7--13 locked; 1--6 exploratory \\\\
\\bottomrule
\\end{tabular}
\\end{table}

\\textbf{Threat model.}""")

# ---- 2. §3 heading: measure -> instrument ----
rep("\\section{A Shared Observation Language}\n\\label{sec:measure}",
    "\\section{An Observation Instrument}\n\\label{sec:measure}")

# ---- 3. §4 heading + subsections to layers ----
rep("\\section{Structural Disagreement Analysis}\n\\label{sec:explain}",
    "\\section{Observed Disagreement, Layer by Layer}\n\\label{sec:explain}")
rep("\\subsection{Coverage Gaps}\nThe first structural cause of disagreement is a \\emph{coverage gap}: a scanner does not inspect a region at all.",
    "\\subsection{L1: Coverage Failures}\nA coverage failure is architectural: the scanner does not inspect the region at all.")
rep("The pattern behind the gaps is architectural: a payload whose malice lives in a runtime dataflow (user input interpolated into a command pipeline) has no static surface in the skill text, and scanners that do not model that flow cannot see it at all.",
    "The canonical instance is a payload whose malice lives in a runtime dataflow (user input interpolated into a command pipeline): no static surface in the skill text, invisible to any scanner that does not model that flow.")

rep("\\subsection{Operational Divergence}\nThe second cause is subtler. Scanners can \\emph{semantically agree} that a coordinate matters while \\emph{operationally diverging} on how to detect it. Consider the coordinate (credential access $\\times$ code execution $\\times$ data exfiltration): all three scanners nominally cover it, yet SkillSpector instantiates detection through script-level semantic evidence, Cisco through literal command triggers, and Caterpillar through lexical regex patterns. Same coordinate, same semantic intent, three different operational surfaces. An attack that removes the literal surface evades Cisco and Caterpillar while SkillSpector may still catch it, and vice versa for attacks that hide the script.",
    "\\subsection{L2/L3: Detection and Decision Failures}\nScanners can \\emph{semantically agree} that a coordinate matters yet fail on different layers underneath. On the credential-exfiltration coordinate, all three nominally cover it; SkillSpector instantiates detection through script-level semantic evidence (L2 strong), Cisco through literal command triggers (L2 narrow) plus a severity threshold (L3 discarding), Caterpillar through lexical regex (L2 lexical only). An attack that removes the literal surface fails Cisco's L2 and Caterpillar's L2; an attack whose findings stay MEDIUM fails Cisco's L3 while the engines saw everything.")

# grey zone: MEDIUM mirror -> L3 language
rep("The benign-side mirror of Cisco's MEDIUM swallowing is visible here too: 662 benign skills (16.6\\%) carry MEDIUM findings the threshold keeps invisible. The same cut hides malware on one side and noise on the other.",
    "This is the benign-side mirror of the L3 cut: 662 benign skills (16.6\\%) carry MEDIUM findings the threshold keeps invisible. The same decision layer that hides malware on one side hides noise on the other---and only a decomposition that separates L3 from detection can say which side a fix will move.")

open('main.tex','w').write(src)
print("v7 step 2 OK")
