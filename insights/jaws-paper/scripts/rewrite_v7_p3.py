#!/usr/bin/env python3
"""v7 step 3: Loop section rename, prediction ledger T4, fig:oneload redraw
as three-layer anatomy, merge Related Work into Discussion."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. §5 rename -> The Loop ----
rep("\\section{From Analysis to Blind-Spot Hypotheses}\n\\label{sec:hypotheses}",
    "\\section{The Loop: From Disagreement to Locked Hypotheses}\n\\label{sec:hypotheses}")
rep("It is a common observation layer through which two kinds of evidence are turned into explicit, pre-specified hypotheses, which we lock \\emph{before} building any adversarial sample.",
    "It is a common observation layer through which two kinds of evidence are turned into explicit, per-layer hypotheses, which we lock \\emph{before} building any adversarial sample. The loop runs: observe disagreement, localize it in the space, decompose it into L1/L2/L3, hypothesize which layer fails for which scanner, lock, construct, validate, and trace the mechanism.")

# ---- 2. §6 rename + ledger framing ----
rep("\\section{Early Evidence: Adversarial Validation}\n\\label{sec:validate}",
    "\\section{Does the Loop Work? A Prediction Ledger}\n\\label{sec:validate}")
rep("We now demonstrate that the loop works end-to-end. This is early evidence, proof of feasibility for the idea and the methodology, rather than a claim of benchmark completeness. We validate locked hypotheses through coordinate-driven adversarial construction: 129 samples across arm groups 1--13, of which the 79 in Arms 7--13 test the locked hypotheses; three of those lost their SkillSpector run to scanner-side failures and are excluded from its denominators.",
    "We demonstrate the loop end-to-end as a ledger: six locked hypotheses, their constructions, outcomes, and the layer each failure lives in (Table~\\ref{tab:cases}). This is early evidence, proof of feasibility rather than benchmark completeness. Of 129 constructed samples across arm groups 1--13, the 79 in Arms 7--13 test the locked hypotheses (three lost their SkillSpector run to scanner-side failures and are excluded from its denominators); Arms 1--6 were exploratory. The ledger reports confirmed, partial, and \\emph{rejected} predictions alike: the framework does not guarantee bypasses; it generates falsifiable hypotheses.")

# ---- 3. tab:cases rebuild as ledger ----
old_tab = src[src.find("\\begin{table*}[t]\n\\caption{\\textbf{The prediction chain"):src.find("\\end{table*}", src.find("label{tab:cases}")) + len("\\end{table*}")]
assert old_tab, "tab:cases not found"
new_tab = r"""\begin{table*}[t]
\caption{\textbf{Prediction ledger: locked hypothesis $\rightarrow$ construction $\rightarrow$ outcome $\rightarrow$ failure layer.} Evidence type A = coordinate-coverage matrix (recorded 2026-08-13); type B = scanner source reading that preceded its construction. All constructions ran 2026-08-19 or later. Outcomes carry Wilson 95\% intervals in Fig.~\ref{fig:validation}. The ledger includes a partial and a rejected prediction: the framework does not guarantee bypasses, it generates falsifiable hypotheses.}
\label{tab:cases}
\small
\begin{tabular}{@{}llp{4.1cm}p{2.6cm}p{2.9cm}c@{}}
\toprule
H & Evidence & Locked prediction & Construction & Outcome & Layer \\
\midrule
H1 & B: build context skips dotfiles & hidden-file payload never analyzed & payload entirely in dotfiles (Arm7, $n{=}15$) & \textbf{14/15} evade SS (11 score 0); Cisco 4/15, Cat 2/15 & L1 \\
H2 & A: regex matches lexical markers & no-literal wording unseen & tool-semantics phrasing (Arm10B, $n{=}10$) & \textbf{10/10} evade Cat; SS 7/7 valid & L2 \\
H3 & A: Cisco escalates only surfaced findings & finding-family variants surface nothing & per-family variants (Arm11A, $n{=}6$) & \textbf{6/6} evade Cisco; SS 6/6 & L2$\to$L3 \\
H4 & B: additive scoring of independent checks & conjunction under-scored & stacked weak mechanisms (Arm13, $n{=}5$) & \textbf{5/5} $\le$50 on SS; 2/5 evade all three & L3 \\
H5 & A: wild pipeline precedent & runtime dataflow unseen & variable-injection pipelines (Arm11B, $n{=}5$) & \emph{partial}: 3/5 score 0 on SS & L2 \\
H6 & --- (stability check) & variant family keeps evasion & expand best single bypass (Arm12, $n{=}10$) & \emph{rejected}: SS detects 9/10 & --- \\
\bottomrule
\end{tabular}
\end{table*}"""
src = src.replace(old_tab, new_tab)

# ---- 4. fig:oneload redraw: three-layer anatomy ----
old_fig = src[src.find("\\begin{figure*}[t]\n\\centering\n\\begin{tikzpicture}[node distance=2.5mm and 4mm,"):src.find("\\label{fig:oneload}\n\\end{figure*}") + len("\\label{fig:oneload}\n\\end{figure*}")]
assert old_fig, "fig:oneload not found"
new_fig = r"""\begin{figure*}[t]
\centering
\begin{tikzpicture}[node distance=3mm and 9mm,
  box/.style={draw=black!40, rounded corners=1pt, font=\scriptsize, align=center, inner sep=3.5pt},
  arrow/.style={-{Stealth[length=2mm]}, thick, black!60}]

% artifact bar
\node[box, fill=black!5, minimum width=118mm, inner sep=4pt] (art) {\textbf{ONE ARTIFACT}\quad \texttt{SKILL.md}: benign ``environment inspector'' \quad+\quad \texttt{.env}: credential exfiltrator (a shell script despite its name)};

% three scanner columns
\node[box, below=7mm of art.west, anchor=west, fill=blue!8, text width=33mm] (ss)
  {\textbf{SkillSpector}\\[1pt] \textbf{L1 coverage}\\ \texttt{build\_context()} skips dotfiles\\ \texttt{.env} never analyzed\\ raw output: \texttt{['SKILL.md']}};
\node[box, fill=blue!8, text width=33mm] at ($(ss.east)+(0.59\textwidth-16mm,0)$) (cat)
  {\textbf{Caterpillar}\\[1pt] \textbf{L2 detection}\\ reads the bytes, but rules need \texttt{curl|bash} / \texttt{base64} markers\\ no lexical surface $\to$ no match};
\node[box, fill=blue!8, text width=33mm] at ($(cat.east)+(0.59\textwidth-16mm,0)$) (ci)
  {\textbf{Cisco}\\[1pt] \textbf{L3 decision}\\ YARA fires, severity = MEDIUM\\ \texttt{is\_safe} keeps CRITICAL/HIGH only\\ finding discarded};

\draw[arrow] ($(art.south)+(0.25\textwidth-38mm,0)$) -- (ss.north);
\draw[arrow] ($(art.south)+(0.01\textwidth,0)$) -- (cat.north);
\draw[arrow] ($(art.south)-(0.25\textwidth-38mm,0)$) -- (ci.north);

% outcomes
\node[box, below=3mm of ss, fill=red!12, text width=33mm] (sso) {\textbf{14/15 evade}\\ 11 score exactly 0};
\node[box, fill=red!12, text width=33mm] at ($(sso.east)+(0.59\textwidth-16mm,0)$) (cato) {\textbf{13/15 evade}\\ grade A, zero findings};
\node[box, fill=red!12, text width=33mm] at ($(cato.east)+(0.59\textwidth-16mm,0)$) (cio) {\textbf{11/15 evade}\\ \texttt{is\_safe}=true at MEDIUM};
\draw[arrow] (ss) -- (sso); \draw[arrow] (cat) -- (cato); \draw[arrow] (ci) -- (cio);

% bottom line
\node[box, below=4.5mm of sso.south, anchor=west, fill=black!5, minimum width=118mm, inner sep=4pt] (bot)
  at (sso.west) {\textbf{One artifact, three scanners, three different failure layers} --- a scalar $\kappa$ records the disagreement and cannot say which layer, which scanner, or why};
\end{tikzpicture}
\caption{\textbf{Three-layer failure anatomy of one hidden-file payload.} The same artifact fails three scanners for three architecturally different reasons: SkillSpector never collects the dotfile (L1), the regex engine collects everything but matches nothing (L2), Cisco's engine fires but its decision rule discards the MEDIUM finding (L3). Source-level mechanisms: \texttt{build\_context.py} file walk; lexical rule families; \texttt{models.py} severity threshold.}
\label{fig:oneload}
\end{figure*}"""
src = src.replace(old_fig, new_fig)

# ---- 5. Arm7 outcome paragraph -> layer terms ----
rep("The two production scanners fail on the same samples for different reasons, which is the decomposition in action: Cisco's YARA rules do read hidden-file content (credential-harvesting signatures fire), but the resulting MEDIUM-severity findings are discarded by the is-safe threshold, for 4/15 detections; the regex engine, which sees the same bytes, detects 2/15. One payload, three failure layers: file collection, severity threshold, lexical matching.",
    "The other two scanners fail on the same samples at different layers (Fig.~\\ref{fig:oneload}): Cisco's YARA rules do read hidden-file content (credential-harvesting signatures fire), but the resulting MEDIUM findings are discarded by the is-safe threshold---an L3 failure at 4/15 detections; the regex engine sees the same bytes but matches nothing---an L2 failure at 2/15. One payload, three layers: coverage, detection, decision.")

open('main.tex','w').write(src)
print("v7 step 3 OK")
