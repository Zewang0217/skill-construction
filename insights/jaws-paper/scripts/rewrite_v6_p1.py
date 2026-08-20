#!/usr/bin/env python3
"""Rewrite main.tex part 1: numbers, claims, table rebuild. Idempotent-unsafe: run once."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)} expected {count}: {old[:70]!r}"
    src = src.replace(old, new)

B = '\\' * 2  # LaTeX row terminator

# ---- 1. Abstract ----
rep("Across 582 real malicious skills and three heterogeneous scanners",
    "Across 581 malicious skills (350 wild, 231 coordinate-generated) and three heterogeneous scanners")

# ---- 2. Intro honesty point ----
rep("In aggregate the scanners are strong: across 582 real malicious skills, SkillSpector detects 92.8\\%, Cisco 85.2\\%, Caterpillar 72.5\\%.",
    "In aggregate the scanners are strong: across 581 malicious skills, SkillSpector flags 92.9\\%, Cisco 86.7\\%, Caterpillar 72.6\\% under a uniform reading of their outputs.")

# ---- 3. Contributions ----
rep("\\item \\textbf{Early evidence.} 582 real malicious skills, three scanners, 129 locked adversarial constructions, and source-level mechanism tracing.",
    "\\item \\textbf{Early evidence.} 581 malicious skills and 500 benign references under three scanners; 79 confirmatory constructions (of 129 built) testing hypotheses specified before construction; source-level mechanism tracing.")

# ---- 4. §2 mapping derivation ----
rep("We mapped 67 scanner-native categories into the space, producing 43 coordinates.",
    "We mapped the documented category systems of six scanners (168 threat categories in total) into the space; the occupied cells consolidate into 43 distinct threat coordinates.")

# ---- 5. Orthogonality ----
rep("""\\subsection{Orthogonality}
The dimensions carry complementary information. On an 81-row human-verified gold standard, pairwise normalized mutual information is 0.565 (source$\\times$mechanism), 0.492 (mechanism$\\times$target), and 0.232 (source$\\times$target): the axes correlate but do not collapse into each other. Ablating any single axis destroys 21\\% (source), 38\\% (target), or 41\\% (mechanism) of coordinate resolution, and full three-dimensional coordinates resolve threats $2.6\\times$ more finely than the best pair. The space therefore carries non-redundant information and serves as the observation layer for all subsequent analysis.""",
"""\\subsection{Orthogonality}
The dimensions carry complementary information. On an 81-category human-verified gold standard, pairwise normalized mutual information is 0.565 (source$\\times$mechanism), 0.492 (mechanism$\\times$target), and 0.232 (source$\\times$target): the axes correlate but do not collapse into each other, and removing any single axis collapses that standard's 31 occupied coordinates to between 15 and 23. Practically, its 81 native labels compress into 31 coordinates ($2.6\\times$) because the space merges synonymous vocabularies across scanners---45\\% of coordinates carry multiple native labels---while keeping distinctions flat lists cannot express.""")

# ---- 6. §4 opening ----
rep("This is the paper's core analysis, measured on 582 real malicious skills (350 wild samples stratified by behavior, 232 coordinate-generated).",
    "This is the paper's core analysis, measured on 581 malicious skills (350 wild samples stratified by behavior, 231 coordinate-generated) plus 500 benign marketplace skills as a false-positive reference, under one decision rule fixed before analysis.")

# ---- 7. §4.1 prose ----
rep("""\\subsection{Aggregate Detection Conceals the Structure}
Table~\\ref{tab:disagg} shows what the aggregate view sees---and what it hides. In aggregate the scanners are strong: SkillSpector detects 92.8\\%, Cisco 85.2\\%, Caterpillar 72.5\\%. Stopping here, one would conclude detection is largely solved. Yet the per-sample flag distribution shows 39.2\\% of malicious skills are missed by at least one scanner, and the \\emph{combination} column shows the misses are not random: Caterpillar alone accounts for the largest missed group (C+S, 118), Cisco is the sole miss in 45, SkillSpector in only 16. The blind spots are invisible at this level of abstraction; they emerge only when the attack space is partitioned.""",
"""\\subsection{Aggregate Detection Conceals the Structure}
Table~\\ref{tab:disagg} shows what the aggregate view sees---and what it hides. Under the uniform reading, SkillSpector flags 92.9\\%, Cisco 86.7\\%, Caterpillar 72.6\\% of the 581 malicious skills. Under each product's \\emph{shipped} decision rule the same raw outputs yield 46.8\\%, 71.6\\%, and 38.6\\%: the disagreement statistics are functions of thresholds, not only of scanners. Stopping at any of these numbers, one concludes detection is largely solved or largely broken depending on the rule chosen. The structure emerges one level down: 222 skills (38.2\\%) are missed by at least one scanner; misses concentrate in reproducible combinations (Caterpillar the sole miss on 118, Cisco 40, SkillSpector 23); and per-class detection spans 0--100\\% (Fig.~\\ref{fig:disagg}c).""")

# ---- 8. tab:disagg caption ----
rep("""\\caption{Observed disagreement on 582 real malicious skills (350 wild + 232 coordinate-generated). Readings recover what each product's shipped decision rule discards: Cisco counts MEDIUM-or-higher (recovers 80 threshold-swallowed findings), SkillSpector any nonzero risk score, Caterpillar any finding. Completion: Cisco 564/582, SkillSpector 541/582, Caterpillar 582/582 (scanner-side failures excluded).}""",
"""\\caption{Observed disagreement under one reproducible decision rule fixed before analysis: Cisco flagged iff \\texttt{is\\_safe=false} or any MEDIUM-or-higher finding; SkillSpector iff risk score $>0$; Caterpillar iff any finding. Cisco returned null verdicts on 17 malicious skills (counted as non-detections); SkillSpector completed all 581. ``Shipped rules'' rows show what the same raw outputs say under each product's own threshold (Cisco CRITICAL/HIGH; SkillSpector score $>50$; Caterpillar grade $\\neq$A). Benign reference: 500 marketplace skills, unaudited; flag rates are upper bounds on false positives.""")

# ---- 9. tab:disagg panel (a) rows ----
old_a = ("Wild (350) & 87.4\\% & 91.1\\% & 70.9\\% \\\\" + "\n" +
         "Generated (232) & 82.3\\% & 95.3\\% & 75.0\\% \\\\" + "\n" +
         "All (582) & 85.2\\% & 92.8\\% & 72.5\\% \\\\")
new_a = ("Wild (350) & 88.0\\% & 91.1\\% & 70.9\\% \\\\" + "\n" +
         "Generated (231) & 84.8\\% & 95.7\\% & 75.3\\% \\\\" + "\n" +
         "All malicious (581) & 86.7\\% & 92.9\\% & 72.6\\% \\\\" + "\n" +
         "\\quad same outputs, shipped rules & 71.6\\% & 46.8\\% & 38.6\\% \\\\" + "\n" +
         "Benign ref.\\ (500) & 35.2\\% & 44.2\\% & 28.6\\% \\\\" + "\n" +
         "\\quad same outputs, shipped rules & 11.2\\% & 2.8\\% & 16.4\\% \\\\")
rep(old_a, new_a)

# ---- 10. panel (b) rows ----
old_b = ("3 (all) & 354 & 60.8\\% & \\\\" + "\n" +
         "2 & 179 & 30.8\\% & \\\\" + "\n" +
         "1 & 39 & 6.7\\% & \\\\" + "\n" +
         "0 & 10 & 1.7\\% & \\\\")
new_b = ("3 (all) & 359 & 61.8\\% & \\\\" + "\n" +
         "2 & 175 & 30.1\\% & \\\\" + "\n" +
         "1 & 39 & 6.7\\% & \\\\" + "\n" +
         "0 & 8 & 1.4\\% & \\\\")
rep(old_b, new_b)

# ---- 11. panel (c) rows ----
old_c = ("Cisco + SkillSpector & 118 & Caterpillar & \\\\" + "\n" +
         "SkillSpector + Caterpillar & 45 & Cisco & \\\\" + "\n" +
         "Cisco + Caterpillar & 16 & SkillSpector & \\\\" + "\n" +
         "Single-scanner flags & 39 & SS 23 / Cisco 8 / Cat 7 & \\\\")
new_c = ("Cisco + SkillSpector & 118 & Caterpillar & \\\\" + "\n" +
         "SkillSpector + Caterpillar & 40 & Cisco & \\\\" + "\n" +
         "Cisco + Caterpillar & 17 & SkillSpector & \\\\" + "\n" +
         "Single-scanner flags & 39 & SS 23 / Cisco 10 / Cat 6 & \\\\")
rep(old_c, new_c)

open('main.tex', 'w').write(src)
print("part 1 applied OK")
