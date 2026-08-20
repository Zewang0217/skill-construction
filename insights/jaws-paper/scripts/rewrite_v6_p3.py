#!/usr/bin/env python3
"""Rewrite main.tex part 3: tab:cases caption+rows, fig_validation insert,
§7 implications fixes (triple-miss honesty, 80->88, ≤27% removal)."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)} expected {count}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. tab:cases caption ----
rep("\\caption{\\textbf{The prediction chain: structural evidence $\\rightarrow$ locked blind-spot hypothesis $\\rightarrow$ pre-locked construction $\\rightarrow$ validation $\\rightarrow$ mechanism.} All hypotheses were locked on 2026-08-13 (coverage matrix + source reading); all constructions ran on 2026-08-19 or later. Read left to right: each row is one full traversal of the loop.}",
    "\\caption{\\textbf{The prediction chain: structural evidence $\\rightarrow$ locked blind-spot hypothesis $\\rightarrow$ pre-locked construction $\\rightarrow$ validation $\\rightarrow$ mechanism.} The coverage matrix was recorded 2026-08-13; each Type-B hypothesis derives from source reading that preceded its construction; all constructions ran 2026-08-19 or later. Read left to right: each row is one full traversal of the loop. Rates carry Wilson 95\\% intervals in Fig.~\\ref{fig:validation}; Arm13's row includes 2/5 samples that evaded all three scanners simultaneously.}")

# ---- 2. tab:cases row 2 (Cisco mechanism wording) ----
rep("Cisco requires literal command triggers & indirect execution unseen & indirect construction variants & \\textbf{6/6} evade Cisco & trigger surface \\\\",
    "Cisco escalates only findings its layers surface & behavior invisible to its finding families & finding-specialized variants (per SkillSpector family) & \\textbf{6/6} evade Cisco & severity escalation \\\\")

# ---- 3. tab:cases row 4 add triple-miss note ----
rep("Independent checks, additive scoring & conjunction under-scored & stacked weak mechanisms & \\textbf{5/5} partial bypass SS & score composition \\\\",
    "Independent checks, additive scoring & conjunction under-scored & stacked weak mechanisms & \\textbf{5/5} partial bypass SS; 2/5 all three & score composition \\\\")

# ---- 4. insert fig_validation before Confirming Cases subsection ----
rep("\\subsection{Confirming Cases}",
    """\\begin{figure}[t]
\\centering
\\includegraphics[width=\\columnwidth]{fig_validation.pdf}
\\caption{\\textbf{Confirmatory constructions as rates with uncertainty.} Each row is one locked hypothesis from Table~\\ref{tab:cases}; points are observed evasion rates (filled) or, for the negative control, the detection rate (open); bars are Wilson 95\\% intervals; $n$ at right. The negative control (Arm12: expanding the best single bypass into a 10-variant family) shows SkillSpector detecting 9/10---single-sample evasion is not family-level evasion, which disciplines every positive row.}
\\label{fig:validation}
\\end{figure}

\\subsection{Confirming Cases}""")

# ---- 5. §7 ecosystem: replace falsified claim ----
rep("\\emph{For the skill ecosystem.} Single-scanner governance inherits that scanner's blind spots wholesale. The coverage matrix quantifies the case for defense-in-depth: after sanitization, no single attack form evades all three scanners simultaneously, yet each scanner has a form on which its detection collapses ($\\le$27\\%). Complementary operational surfaces are not redundancy; they are coverage.",
    "\\emph{For the skill ecosystem.} Single-scanner governance inherits that scanner's blind spots wholesale. In the 581-skill corpus, no all-scanner miss survived sanitization (10 flagged-by-none candidates, each attributed to data-quality, scanner-failure, or threshold artifacts). Locked construction nonetheless found the exception class: stacking independently weak mechanisms evaded all three scanners on 2/5 samples---defense-in-depth fails at the conjunction, not at any single mechanism. Conversely each scanner has a family where its own shipped detection collapses: hidden files for SkillSpector (14/15 evade), finding-specialized variants for Cisco (6/6), no-literal semantics for the regex engine (10/10).")

# ---- 6. 80 -> 88 (two places, consistent-rule number) ----
rep("surface MEDIUM findings instead of discarding them (80 of them in our corpus alone).",
    "surface MEDIUM findings instead of discarding them (88 skills in our corpus are \\texttt{is\\_safe} with MEDIUM-or-higher findings).")
rep("threshold swallowing (80 MEDIUM findings silently discarded by a safe/unsafe threshold in the main experiment)",
    "threshold swallowing (88 skills whose MEDIUM-or-higher findings are silently discarded by the safe/unsafe verdict)")

open('main.tex', 'w').write(src)
print("part 3 applied OK")
