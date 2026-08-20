#!/usr/bin/env python3
"""Rewrite main.tex part 2: kill tab:kappa, insert fig_disagreement, fix §4.2/4.3,
hypothesis-locking timeline, arm intro, Arm11A mechanism, tab:cases, implications."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)} expected {count}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. §4.2 Coverage Gaps: replace kappa-table prose with aligned-kappa prose + figure ----
old = """\\subsection{Coverage Gaps}
The first structural cause of disagreement is a \\emph{coverage gap}: a scanner does not inspect a coordinate at all. The per-dimension agreement pattern (Table~\\ref{tab:kappa}) localizes where. This analysis runs on the finding-level corpus from our taxonomy-mapping stage (three scanners with declarable category systems that surfaced shared findings: SkillSpector, Snyk, and ATH), since $\\kappa$ requires comparable per-finding labels. After mapping those findings onto coordinates, agreement splits by axis. The pre-taxonomy baseline is near-zero ($\\kappa\\approx0.13$ on shared binary flags). After mapping, agreement on \\emph{target} rises to $+0.223$---the shared language unifies what an attack wants---while \\emph{mechanism} stays near zero ($-0.025$) and \\emph{source} turns negative ($-0.137$): scanners report behavior, not provenance, and two of them read provenance in systematically opposite ways (Snyk external-content vs.\\ ATH supply-chain, $\\kappa=-0.395$ on shared findings). The split is the point: one third of the disagreement is a language problem the coordinate space solves, and the rest is structural, which is what the decomposition next isolates.
"""
new = """\\subsection{The Statistic Itself Is Unstable}
Before decomposing disagreement, we must be able to measure it---and the standard statistic turns out to be corpus- and rule-dependent on our own data. Figure~\\ref{fig:disagg}a computes pairwise Cohen's $\\kappa$ from the \\emph{same} $581\\times3$ raw outputs under three defensible choices: malicious-only with shipped rules ($\\kappa$ from $-0.01$ to $+0.24$), malicious-only with the uniform rule ($+0.08$ to $+0.16$), and malicious-plus-benign with the uniform rule ($+0.29$ to $+0.44$). The benign corpus dominates the third condition because agreement on easy negatives inflates $\\kappa$; the shipped-rule condition collapses because thresholds disagree more than detections do. No scalar in this range says \\emph{where} the scanners differ or \\emph{why}---which is precisely the statistic view's blind spot, now demonstrated on real data rather than asserted.
"""
rep(old, new)

# ---- 2. remove tab:kappa table + trailing sentence, keep coordinate-gap content ----
old = """\\begin{table}[t]
\\caption{Inter-scanner agreement by dimension, on 793 deduplicated shared findings across SkillSpector, Snyk, and ATH (finding-level Cohen's $\\kappa$; pairs evaluated on skills both scanners flag). The pre-taxonomy baseline on shared binary flags is $\\kappa\\approx0.13$.}
\\label{tab:kappa}
\\small
\\begin{tabular}{@{}lrrr@{}}
\\toprule
Dimension & mean $\\kappa$ & best pair & worst pair \\\\
\\midrule
target & $+0.223$ & SS$\\times$Snyk $0.550$ & SS$\\times$ATH $-0.130$ \\\\
mechanism & $-0.025$ & SS$\\times$ATH $0.131$ & Snyk$\\times$ATH $-0.222$ \\\\
source & $-0.137$ & SS$\\times$ATH $-0.015$ & Snyk$\\times$ATH $-0.395$ \\\\
\\bottomrule
\\end{tabular}
\\end{table} Coordinates whose source is the runtime environment or user input are systematically less covered than supply-chain coordinates: a payload whose malice lives in a runtime dataflow (user input interpolated into a command pipeline) has no static surface in the skill text, and scanners that do not model that flow cannot see it at all.
"""
new = """\\subsection{Coverage Gaps}
The first structural cause of disagreement is a \\emph{coverage gap}: a scanner does not inspect a region at all. Figure~\\ref{fig:disagg}c localizes them empirically: wild behavior classes and generated source slices where one scanner collapses while others hold (remote-code-execution class: Cisco 14\\% vs.\\ SkillSpector 57\\%; runtime-environment sources: Cisco 33\\%). The pattern behind the gaps is architectural: a payload whose malice lives in a runtime dataflow (user input interpolated into a command pipeline) has no static surface in the skill text, and scanners that do not model that flow cannot see it at all.
"""
rep(old, new)

# ---- 3. insert fig_disagreement after tab:disagg ----
old = """\\subsection{The Statistic Itself Is Unstable}"""
new = """\\begin{figure*}[t]
\\centering
\\includegraphics[width=\\textwidth]{fig_disagreement.pdf}
\\caption{\\textbf{Empirical disagreement structure on $581$ malicious skills $\\times$ three scanners, from one reproducible rule.} (a)~Pairwise Cohen's $\\kappa$ computed from the same raw outputs under three corpus/rule choices: the statistic swings from $-0.01$ to $+0.44$; none of these scalars localizes the disagreement. (b)~Flag-combination distribution: misses concentrate in reproducible combinations, not noise. (c)~Detection rate by wild behavior class and generated source axis (cell $n$ in labels): per-class detection spans 0--100\\%, the spread that aggregate recall conceals.}
\\label{fig:disagg}
\\end{figure*}

\\subsection{The Statistic Itself Is Unstable}"""
rep(old, new)

# ---- 4. §4.3 operational divergence: drop structure-map figure, verbalize bands ----
old = """Figure~\\ref{tab:forms} shows where the two production scanners' declared coverage diverges, coordinate by coordinate. The map separates two kinds of disagreement that a $\\kappa$ conflates. In the 10 \\emph{both-declare} coordinates, disagreement is operational: both scanners cover the region but instantiate detection differently, SkillSpector via script-level semantic evidence and Cisco via literal command triggers. An attack that removes the literal surface evades Cisco while SkillSpector may still catch it; attacks that hide the script do the reverse. In the 16+4 \\emph{single-coverage} coordinates, the disagreement is a coverage gap: one scanner simply has no category that maps there. The 13 \\emph{neither} coordinates are collectively unguarded by both prod"""
# tail truncated in source view; use a shorter unique anchor
rep("Figure~\\ref{tab:forms} shows where the two production scanners' declared coverage diverges, coordinate by coordinate.",
    "Projecting each scanner's mapped categories onto the space separates the two kinds of disagreement that a $\\kappa$ conflates (declared-coverage matrix, \\S\\ref{sec:hypotheses}): among the 43 occupied coordinates, 10 are declared by both production scanners, 16 only by SkillSpector, 4 only by Cisco, and 13 by neither.")

# remove the structure-map figure block
old_fig = """\\begin{figure}[t]
\\centering
\\includegraphics[width=0.92\\columnwidth]{fig_structure_map.pdf}
\\caption{\\textbf{The structure of declared coverage across 43 occupied threat coordinates.} Rows are coordinates (IDs at left); filled cells are categories the scanner maps onto that coordinate. The four bands are four disagreement states: 10 coordinates where both production scanners declare coverage (candidate operational divergence), 16 covered only by SkillSpector, 4 only by Cisco, and 13 covered by neither (several only by external reference taxonomies). A regex tool with no category system appears in no column; it cannot be mapped at all. Color encodes \\emph{disagreement type}, not detection rate.}
\\label{tab:forms}
\\end{figure}

"""
assert old_fig in src
src = src.replace(old_fig, "")

# ---- 5. §5 hypothesis-locking timeline fix ----
rep("Our timeline is explicit and reproducible: the coordinate-coverage matrix and blind-spot hypotheses were recorded on 2026-08-13; confirmatory construction began 2026-08-19. The hidden-file hypothesis, for instance, was derived by reading SkillSpector's build-context source \\emph{before} any hidden-file sample existed. Arms~1--6 preceded the matrix and are labeled exploratory: they establish that coordinate-driven construction is feasible, and none of their outcomes enters the hypothesis table.",
    "Our timeline is explicit: the coordinate-coverage matrix was recorded on 2026-08-13; each Type-B hypothesis was derived from source reading before its construction existed (the hidden-file hypothesis, from SkillSpector's build-context source, before any hidden-file sample was built); confirmatory constructions ran on 2026-08-19 and later. Arms~1--6 ran outside the locking protocol and are labeled exploratory: they establish that coordinate-driven construction is feasible, and none of their outcomes enters the hypothesis table.")

# ---- 6. §6 arm intro ----
rep("We validate locked hypotheses through coordinate-driven adversarial construction: 129 constructed samples across 13 experiment arms, each scanned by all three scanners.",
    "We validate locked hypotheses through coordinate-driven adversarial construction: 129 samples across arm groups 1--13, of which the 79 in Arms 7--13 test the locked hypotheses; three of those lost their SkillSpector run to scanner-side failures and are excluded from its denominators.")

# ---- 7. exploratory arms wording ----
rep("Arms~1--6 preceded hypothesis locking and serve two feasibility roles only.",
    "Arms~1--6 ran outside the locking protocol and serve two feasibility roles only.")

# ---- 8. Arm11A mechanism fix (slice-based; source uses \_\_import\_\_) ----
anchor = "Three deserve mechanism notes. The expression-variant construction (0/6 on Cisco)"
i = src.find(anchor)
assert i >= 0, "anchor not found"
j = src.find("The no-literal construction", i)
assert j > i, "end anchor not found"
new_head = ("Three deserve mechanism notes. The finding-specialized construction (0/6 on Cisco) "
            "builds one variant per SkillSpector finding family (sensitive-data instructions, "
            "sensitive-data disclosure, exfiltration, AST-level execution), each re-expressing the same "
            "malicious behavior so that Cisco's static layers surface nothing its severity logic escalates: "
            "all six stay \\texttt{is\\_safe} with INFO--MEDIUM severities, while SkillSpector scores all six "
            "(its LLM layer reasons over script semantics)---a clean instance of operational divergence on a "
            "coordinate both scanners declare. ")
src = src[:i] + new_head + src[j:]

open('main.tex', 'w').write(src)
print("part 2 applied OK")
