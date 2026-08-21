#!/usr/bin/env python3
"""v8: submission fixes — dedup sentence, denominators, 4th bucket, em-dash
reduction, overfull >5pt, Fig1 colorblind, headheight, Description, medskip."""
import re
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- MAJOR-1: dedup L326 ----
i = src.find("Projecting each scanner's mapped categories onto the space separates the two kinds of disagreement that a $\\kappa$ conflates")
assert i >= 0
# the duplicated sentence later in same paragraph
dup = "The map separates two kinds of disagreement that a $\\kappa$ conflates."
j = src.find(dup, i)
assert j > i
src = src[:j] + src[j+len(dup):]

# ---- MAJOR-2: denominators in grey zone ----
rep("and SkillSpector 16.2\\%, through three mechanism classes",
    "and SkillSpector 650 of 4{,}000 (16.2\\%), through three mechanism classes")
rep("662 benign skills (16.6\\%) carry MEDIUM findings the threshold keeps invisible",
    "662 of the 3{,}996 benign skills (16.6\\%) carry MEDIUM findings the threshold keeps invisible")

# ---- MAJOR-3: §3.2 fourth bucket ----
rep("and 20.3\\% fall into genuine gaps",
    "5.3\\% are compound, and 20.3\\% fall into genuine gaps")

# ---- MAJOR-4: em-dash reduction (31 -> keep definitional only) ----
# Replace connective em-dashes with colons/commas/periods. Keep: the L1/L2/L3
# definitional dashes in the §2 quote (3), ledger arrows, none else.
keep = [
    "Every miss originates in one layer, or in a short chain through adjacent layers:",  # no dash here
]
swaps = [
    ("as a statistic---Cohen's $\\kappa$, pairwise overlap, per-tool recall---and treat",
     "as a statistic (Cohen's $\\kappa$, pairwise overlap, per-tool recall) and treat"),
    ("---a fact about tool quality, or noise to be averaged away.",
     ": a fact about tool quality, or noise to be averaged away."),
    ("disagreement remains global---a $\\kappa$---but never localizable",
     "disagreement remains global (a $\\kappa$) but never localizable"),
    ("a \\emph{shared observation language}---a coordinate space over the threat space---into which",
     "a \\emph{shared observation language} (a coordinate space over the threat space) into which"),
    ("skills---packages of instructions and scripts---and malicious skills",
     "skills (packages of instructions and scripts), and malicious skills"),
    ("its structure becomes evidence about the analyses themselves---from which falsifiable",
     "its structure becomes evidence about the analyses themselves, from which falsifiable"),
    ("a three-layer decomposition---coverage, detection, decision (\\emph{why}?)---locked hypotheses",
     "a three-layer decomposition, coverage/detection/decision (\\emph{why}?), locked hypotheses"),
    ("after seeing the failures---but post-hoc explanation",
     "after seeing the failures; but post-hoc explanation"),
    ("\\emph{L1 coverage} --- the relevant input was never collected;\n\\emph{L2 detection} --- the input was collected but the engine cannot recognize the behavior;\n\\emph{L3 decision} --- the engine produced a finding but the decision rule discarded it.",
     "\\emph{L1 coverage}: the relevant input was never collected;\n\\emph{L2 detection}: the input was collected but the engine cannot recognize the behavior;\n\\emph{L3 decision}: the engine produced a finding but the decision rule discarded it."),
    ("(collect more inputs; change engines; change thresholds), a different attack strategy (hide the file; change the expression; suppress the severity), and therefore a different, falsifiable blind-spot hypothesis.",
     "(collect more inputs; change engines; change thresholds), a different attack strategy (hide the file; change the expression; suppress the severity), and therefore a different falsifiable blind-spot hypothesis."),
    ("The structure emerges one level down: 222 skills (38.2\\%) are missed by at least one scanner; misses concentrate in reproducible combinations---when two scanners agree, the third is the sole miss",
     "The structure emerges one level down: 222 skills (38.2\\%) are missed by at least one scanner; misses concentrate in reproducible combinations. When two scanners agree, the third is the sole miss"),
    ("$\\kappa\\le 0.244$ with most near zero (a), and only 5.9\\% of skills are flagged by four or more scanners (b).",
     "$\\kappa\\le 0.244$ with most near zero (a); only 5.9\\% of skills are flagged by four or more scanners (b)."),
    ("Disagreement at this scale is not noise to average away; it is the ecosystem's default output.",
     "Disagreement at this scale is not noise to average away; it is the ecosystem's default output."),
    ("This direction is what the observation space uniquely enables; no amount of source reading enumerates the space of unoccupied coordinates.",
     "This direction is what the observation space uniquely enables: no amount of source reading enumerates the space of unoccupied coordinates."),
    ("This direction finds \\emph{specific} mechanisms but does not, by itself, say where else to look.",
     "This direction finds \\emph{specific} mechanisms but does not by itself say where else to look."),
    ("The directions converge at the same protocol: hypothesis $\\rightarrow$ lock $\\rightarrow$ construction $\\rightarrow$ validation.",
     "The directions converge at the same protocol: hypothesis, lock, construction, validation."),
    ("\\emph{Validation:} \\textbf{14/15 evade} SkillSpector (score $\\le$50; 11 exactly 0); Cisco detects 4/15, Caterpillar 2/15.",
     "\\emph{Validation:} \\textbf{14/15 evade} SkillSpector (score $\\le$50; 11 exactly 0); Cisco detects 4/15; Caterpillar 2/15."),
    ("records the analyzed components as exactly \\texttt{['SKILL.md']}---the dotfile never entered analysis (L1)",
     "records the analyzed components as exactly \\texttt{['SKILL.md']}: the dotfile never entered analysis (L1)"),
    ("\\textbf{One artifact, three scanners, three different failure layers} --- a scalar $\\kappa$ records the disagreement, and cannot say which layer, which scanner, or why",
     "\\textbf{One artifact, three scanners, three different failure layers:} a scalar $\\kappa$ records the disagreement and cannot say which layer, which scanner, or why"),
    ("shows SkillSpector detecting 9/10---single-sample evasion is not family-level evasion, which disciplines every positive row",
     "shows SkillSpector detecting 9/10; single-sample evasion is not family-level evasion, which disciplines every positive row"),
    ("each below the scoring threshold; the additive scorer never sees the conjunction, and 2/5 samples evade all three scanners simultaneously, the only place in the study where that happens.",
     "each below the scoring threshold; the additive scorer never sees the conjunction, and 2/5 samples evade all three scanners simultaneously (the only place in the study where that happens)."),
    ("the regex engine sees the same bytes and matches nothing (L2, 2/15). One artifact, three layers: coverage, detection, decision.",
     "the regex engine sees the same bytes and matches nothing (L2, 2/15). One artifact, three layers: coverage, detection, decision."),
    ("they showed that detectability tracks the operational \\emph{surface} (direct \\texttt{eval} is caught everywhere; indirect construction is missed by Cisco), and they calibrated the generator",
     "they showed that detectability tracks the operational \\emph{surface}: direct \\texttt{eval} is caught everywhere, indirect construction is missed by Cisco. They also calibrated the generator"),
    ("(semantic re-wrapping of descriptions changes nothing at SkillSpector, whose evidence comes from code; false capability declarations are counterproductive, tripping the description-code contradiction detector)",
     "(semantic re-wrapping of descriptions changes nothing at SkillSpector, whose evidence comes from code; false capability declarations are counterproductive, tripping the description-code contradiction detector)"),
    ("Locked construction $\\rightarrow$ validation $\\rightarrow$ mechanism",
     "Locked construction $\\rightarrow$ validation $\\rightarrow$ mechanism"),
    ("is as corrosive as a blind spot: users disable scanners that cry wolf, and the blind spot then inherits the whole pipeline.",
     "is as corrosive as a blind spot: users disable scanners that cry wolf, and the blind spot then inherits the whole pipeline."),
    ("defense-in-depth fails at the conjunction, not at any single mechanism",
     "defense-in-depth fails at the conjunction, not at any single mechanism"),
    ("Caterpillar folds on instruction-level classes (goal hijacking, instruction override: 0\\%), Cisco folds on deep-disguise remote code execution (14\\%), SkillSpector folds on content manipulation and reverse shell (0\\%)",
     "Caterpillar folds on instruction-level classes (goal hijacking, instruction override: 0\\%); Cisco folds on deep-disguise remote code execution (14\\%); SkillSpector folds on content manipulation and reverse shell (0\\%)"),
    ("The benign-side mirror of Cisco's MEDIUM swallowing is visible here too",
     "The benign-side mirror of Cisco's MEDIUM swallowing is visible here too"),
    ("One anonymity point frames our results.", "One anonymity point frames our results."),
    ("---a coverage defect", ": a coverage defect"),
    ("---an L3 failure", ": an L3 failure"),
    ("---an L2 failure", ": an L2 failure"),
    ("---a clean instance", ", a clean instance"),
    ("---one coordinate, two scanners, different layers", ": one coordinate, two scanners, different layers"),
    ("---hide the file; change the expression; suppress the severity---", " (hide the file; change the expression; suppress the severity) "),
    ("---the input to everything that follows", ", the input to everything that follows"),
    ("---the same 10 semantic variants", "; the same 10 semantic variants"),
    ("A regex-only reference tool is blind to all 10 semantic variants, showing blind spots deepen as detection grows more primitive.",
     "A regex-only reference tool is blind to all 10 semantic variants, showing that blind spots deepen as detection grows more primitive."),
]
applied = 0
for a, b in swaps:
    if a in src:
        src = src.replace(a, b, 1)
        applied += 1
print(f"em-dash swaps applied: {applied}/{len(swaps)}")

# ---- MINOR: overfull hotspots ----
rep("one hypothesis was partially confirmed and one was rejected by its own control experiment.",
    "one hypothesis was partially confirmed and one rejected by its own control experiment.")

# ---- MINOR: headheight ----
rep("\\usepackage{tikz}", "\\usepackage{tikz}\n\\setlength{\\headheight}{16.36pt}")

# ---- MINOR: medskip ----
rep("\\medskip\n\\noindent\\textbf{Takeaway.}", "\\vspace{\\medskipamount}\n\\noindent\\textbf{Takeaway.}")

# ---- MINOR: image Descriptions ----
rep("\\includegraphics[width=\\columnwidth]{fig_census.pdf}",
    "\\includegraphics[width=\\columnwidth]{fig_census.pdf}%\n\\Description{Two stacked panels: a six-by-six heatmap of pairwise kappa values, all at most 0.24, and a bar chart of consensus showing most skills flagged by zero to two scanners.}")
rep("\\includegraphics[width=0.87\\textwidth]{fig_disagreement.pdf}",
    "\\includegraphics[width=0.87\\textwidth]{fig_disagreement.pdf}%\n\\Description{Left: dot-range plot of pairwise kappa under three rules spanning minus 0.01 to plus 0.44. Right: UpSet matrix of flag combinations with all-three 359 dominant.}")
rep("\\includegraphics[width=\\columnwidth]{fig_surface.pdf}",
    "\\includegraphics[width=\\columnwidth]{fig_surface.pdf}%\n\\Description{Heatmap of thirteen wild behavior classes by three scanners, grouped into bands by which scanner collapses.}")
rep("\\includegraphics[width=0.62\\textwidth]{fig_validation.pdf}",
    "\\includegraphics[width=0.62\\textwidth]{fig_validation.pdf}%\n\\Description{Forest plot of seven hypothesis outcomes with Wilson intervals; the negative control is an open marker.}")

open('main.tex','w').write(src)
print("v8 text fixes applied; remaining em-dashes:", src.count('---'))
