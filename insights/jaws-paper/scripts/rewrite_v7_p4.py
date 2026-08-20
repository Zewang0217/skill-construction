#!/usr/bin/env python3
"""v7 step 4: page-diet compressions (Orthogonality, grey zone, Paper identity,
exploratory arms) to return to 8 pages."""
src = open('main.tex').read()

def rep(old, new, count=1):
    global src
    assert src.count(old) == count, f"count={src.count(old)}: {old[:70]!r}"
    src = src.replace(old, new)

# ---- 1. Orthogonality compress ----
i = src.find("\\subsection{Orthogonality}")
j = src.find("\n\n", src.find("flat lists cannot express", i))
assert i >= 0 and j > i
new_orth = """\\subsection{Orthogonality}
The dimensions carry complementary information: on an 81-category human-verified gold standard, pairwise normalized mutual information stays moderate (0.23--0.57), no axis is redundant (removing any one collapses its 31 occupied coordinates to 15--23), and its 81 native labels compress into 31 coordinates ($2.6\\times$) as synonymous scanner vocabularies merge while distinctions survive."""
src = src[:i] + new_orth + src[j:]

# ---- 2. Grey zone compress ----
i = src.find("\\subsection{Misclassification and the Grey Zone}")
j = src.find("\\section{The Loop:")
assert i >= 0 and j > i
new_grey = """\\subsection{The Grey Zone: Capability Read as Intent}
A third finding, orthogonal to misses: scanners can detect a behavior but misclassify its intent. On the official MalSkillBench benign audit (4{,}000 marketplace skills, static runs), Cisco's shipped rule challenges 335 of 3996 (8.4\\%, each a HIGH or CRITICAL veto) and SkillSpector 16.2\\%, through three mechanism classes: \\emph{capability read as intent} (reading one's own \\texttt{OPENAI\\_API\\_KEY} to call the vendor's official API scored as exfiltration), \\emph{defense documentation quoted as payload} (all 22 prompt-injection regex hits are skills that teach injection defense), and \\emph{severity amplification} (one legitimate OAuth flow split into three CRITICALs). And 662 benign skills (16.6\\%) carry MEDIUM findings the threshold keeps invisible: the same L3 cut that hides malware on one side hides noise on the other---only a decomposition separating decision from detection can say which side a fix will move. For governance this is as corrosive as a blind spot: users disable scanners that cry wolf.

"""
src = src[:i] + new_grey + src[j:]

# ---- 3. Paper identity delete ----
rep("\n\\noindent\\textbf{Paper identity.} Disagreement is not merely a number: it reveals structure that can be hypothesized about and tested.\n", "\n")

# ---- 4. Exploratory arms compress ----
i = src.find("\\subsection{Role of the Exploratory Arms}")
j = src.find("\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{fig_validation.pdf}")
assert i >= 0 and j > i
new_expl = """\\subsection{Role of the Exploratory Arms}
Arms~1--6 ran outside the locking protocol and serve two feasibility roles only: they showed that detectability tracks the operational \\emph{surface} (direct \\texttt{eval} is caught everywhere; indirect construction is missed by Cisco), and they calibrated the generator (semantic re-wrapping of descriptions changes nothing at SkillSpector, whose evidence comes from code; false capability declarations are counterproductive, tripping the description-code contradiction detector).

"""
src = src[:i] + new_expl + src[j:]

open('main.tex','w').write(src)
print("v7 step 4 OK")
