#!/usr/bin/env python3
"""Rewrite §4.4 grey zone with the official benign-4000 audit evidence."""
src = open('main.tex').read()

old = """\\subsection{Misclassification and the Grey Zone}
A third, orthogonal finding: scanners can detect a behavior but misclassify its intent. In a pilot audit of 30 SkillSpector findings, every one described a real capability that was in fact a legitimate, declared tool behavior: ``dangerous but legal.'' Detection fired; the verdict was wrong. This is the false-positive side of the same structural story: the scanners' vocabularies have no slot for ``declared, justified capability,'' so a skill that legitimately reads credentials for its stated purpose lands in the same category as one that exfiltrates them. For governance, an unchecked false-positive rate is as corrosive as a blind spot: users disable scanners that cry wolf, and the blind spot then inherits the whole pipeline. Our decomposition treats the grey zone as a first-class object: the misclassification rate is a property of the operational divergence, not of the corpus."""

new = """\\subsection{Misclassification and the Grey Zone}
A third, orthogonal finding: scanners can detect a behavior but misclassify its intent. On the official MalSkillBench benign set (4{,}000 marketplace skills, static-only runs), Cisco's shipped rule challenges 335/3996 (8.4\\%) officially-benign skills---every challenge a HIGH/CRITICAL one-vote veto---and SkillSpector's challenge rate is 16.2\\% (650/4000, with 7.3\\% rated do-not-install). Every audited challenge decomposes into three mechanism classes: \\emph{capability misread as intent} (reading one's own \\texttt{OPENAI\\_API\\_KEY} and calling the vendor's official API scores as credential exfiltration), \\emph{documentation quoted as payload} (a prompt-injection regex firing on skills that \\emph{teach defense against} injection: 22/22 hits flagged unsafe), and \\emph{severity-policy amplification} (a legitimate OAuth flow split into three CRITICAL findings from one file). Our own pilot audit of 30 findings agrees: every finding described a real, legitimately declared capability. The benign-side mirror of Cisco's MEDIUM swallowing is visible here too: 662 benign skills (16.6\\%) carry MEDIUM findings that the threshold keeps invisible---the same cut hides malware on one side and noise on the other. For governance this is as corrosive as a blind spot: users disable scanners that cry wolf, and the blind spot then inherits the whole pipeline."""

assert src.count(old) == 1
src = src.replace(old, new)
open('main.tex', 'w').write(src)
print("grey zone rewritten")
