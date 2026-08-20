#!/usr/bin/env python3
"""v7.1 part B (robust): extract blocks, delete originals, reassemble §6."""
src = open('main.tex').read()

def cut(s, start_marker, end_marker):
    i = s.find(start_marker)
    assert i >= 0, start_marker[:60]
    j = s.find(end_marker, i)
    assert j > i, end_marker[:60]
    return s[i:j + len(end_marker)], s[:i] + s[j + len(end_marker):]

# ---- extract movable blocks ----
ledger_tab, src = cut(src,
    "\\begin{table*}[t]\n\\caption{\\textbf{Prediction ledger",
    "\\end{table*}")
fig_val, src = cut(src,
    "\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{fig_validation.pdf}",
    "\\end{figure}")
oneload_fig, src = cut(src,
    "\\begin{figure*}[t]\n\\centering\n\\begin{tikzpicture}[\n  box/.style={draw=black!40, rounded corners=1pt, font=\\scriptsize, align=center, inner sep=3.5pt},",
    "\\end{figure*}")

# ---- replace Centerpiece subsection with representative-case voice ----
i_c = src.find("\\subsection{Centerpiece: Hidden-File Payloads}")
i_e = src.find("\\subsection{Role of the Exploratory Arms}")
assert 0 < i_c < i_e
new_case = r"""\subsection{A Representative Case, End to End}
The hidden-file hypothesis is the ledger's cleanest full traversal---bottom-up evidence, one locked prediction, one construction family, three different failure layers.
\emph{Derived from (bottom-up):} SkillSpector's build-context source skips dotfiles; Cisco's is-safe rule keeps CRITICAL/HIGH only; the regex engine matches lexical markers only.
\emph{Locked prediction:} payloads placed entirely in hidden files (\texttt{.env}, \texttt{.profile}) evade SkillSpector's analysis.
\emph{Construction:} 15 skills whose SKILL.md is a benign ``environment inspector''; the bundled \texttt{.env} (a shell script despite its name) collects cloud keys, base64-encodes them, and exfiltrates them via \texttt{curl}.
\emph{Validation:} \textbf{14/15 evade} SkillSpector (score $\le$50; 11 exactly 0); Cisco detects 4/15, Caterpillar 2/15.
\emph{Mechanism (Fig.~\ref{fig:oneload}):} the scanner's raw output records the analyzed components as exactly \texttt{['SKILL.md']}---the dotfile never entered analysis (L1). The other two scanners fail on the same samples at different layers: Cisco's YARA rules fire on the hidden content but the MEDIUM findings are discarded by the is-safe threshold (L3, 4/15); the regex engine sees the same bytes and matches nothing (L2, 2/15). One artifact, three layers: coverage, detection, decision.

""" + oneload_fig + "\n\n"
src = src[:i_c] + new_case + src[i_e:]

# ---- replace Confirming Cases prose with ledger-first subsection ----
i_conf = src.find("\\subsection{Confirming Cases}")
i_after = src.find("% ============================================================", i_conf)
assert i_conf > 0 and i_after > i_conf
ledger_prose = r"""\subsection{The Ledger}
Table~\ref{tab:cases} is the paper's payoff: six locked hypotheses with their evidence direction, construction, outcome, and failure layer; Fig.~\ref{fig:validation} shows each outcome as a rate with Wilson 95\% intervals, the rejected control included. Three rows deserve mechanism notes. The finding-specialized construction (H3, 6/6 on Cisco) builds one variant per SkillSpector finding family, each re-expressing the same malicious behavior so that Cisco's static layers surface nothing its severity logic escalates: all six stay \texttt{is\_safe} with INFO--MEDIUM severities, while SkillSpector scores all six---one coordinate, two scanners, different layers. The no-literal construction (H2) expresses exfiltration as tool semantics (``archive the result to the remote repository'') with no \texttt{curl}/\texttt{base64} token anywhere; the regex engine has nothing to match. The combined-strategy construction (H4) stacks independently weak mechanisms---hidden placement, indirect execution, declared-capability cover---each below the scoring threshold; the additive scorer never sees the conjunction, and 2/5 samples evade all three scanners simultaneously, the only place in the study where that happens.

""" + ledger_tab + "\n\n" + fig_val + "\n\n"
src = src[:i_conf] + ledger_prose + src[i_after:]

# ---- ledger caption + rows: direction arrows ----
src = src.replace("Evidence type A = coordinate-coverage matrix (recorded 2026-08-13); type B = scanner source reading that preceded its construction.",
    "Evidence direction: $\\uparrow$~top-down (coordinate-coverage matrix, recorded 2026-08-13); $\\downarrow$~bottom-up (scanner source reading that preceded its construction).")
for a, b in [("H1 & B: build context skips dotfiles", "H1 & $\\downarrow$ build context skips dotfiles"),
             ("H2 & A: regex matches lexical markers", "H2 & $\\uparrow$ regex matches lexical markers"),
             ("H3 & A: Cisco escalates only surfaced findings", "H3 & $\\uparrow$ Cisco escalates only surfaced findings"),
             ("H4 & B: additive scoring of independent checks", "H4 & $\\downarrow$ additive scoring of independent checks"),
             ("H5 & A: wild pipeline precedent", "H5 & $\\uparrow$ wild pipeline precedent"),
             ("H & Evidence & Locked prediction", "H & Dir. & Locked prediction")]:
    assert src.count(a) == 1, a
    src = src.replace(a, b)

open('main.tex', 'w').write(src)
print("v7.1 part B OK")
