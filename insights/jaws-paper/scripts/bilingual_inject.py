#!/usr/bin/env python3
"""Inject bilingual toggle into PAPER_SPINE_VIZ.html.

Mechanism: text-node-level swap. JS walks all text nodes; if the stripped
value is a key in the DICT, replace (preserving leading/trailing spaces).
Inner markup (<code>/<b>) untouched since each text run is handled alone.
"""
import json

ZH = json.load(open('/tmp/zh_segments.json'))

# zh -> en dictionary (authored translation; keys must match extracted runs exactly)
D = {
"实证：":"Evidence:",
"与":"and",
"JAWS 2 — 论文主线脉络可视化 · Paper Spine":"JAWS 2 — Paper Spine Visualization",
"① 主线流程":"① Spine",
"② 三层分解":"② Three Layers",
"③ 证据链":"③ Evidence Chain",
"⑤ 数字锚点":"⑤ Anchors",
"浮层地图":"Float Map",
"论文主线脉络可视化 —— 把 8 页正文的叙事骨架、三层分解、证据依赖、预测账本与关键数字一次看清。所有数字、页码、引文均从":"Paper-spine visualization: the narrative skeleton, three-layer decomposition, evidence dependencies, prediction ledger, and key numbers of the 8-page body at a glance. All numbers, page positions, and quotations come from",
"实读核对。":"verified by direct reading.",
"✓ 数字核对通过":"✓ numbers verified",
"✓ 页码核对通过（Fig1→p3 · Fig2→p4 · Fig3/4→p5 · Fig5→p6 · Fig6→p8）":"✓ page positions verified (Fig1→p3 · Fig2→p4 · Fig3/4→p5 · Fig5→p6 · Fig6→p8)",
"581 恶意 skills × 3 scanners":"581 malicious skills × 3 scanners",
"H1–H6 六条锁定假设":"H1–H6 six locked hypotheses",
"纵向主线流程":"Vertical Spine Flow",
"节点带页码与核心句":"nodes carry page numbers and core sentences",
"在威胁空间的何处分歧":"WHERE in the threat space they disagree",
"为何分歧（L1/L2/L3 层）":"WHY they disagree (layers L1/L2/L3)",
"下一个会漏掉什么":"WHAT they will miss next",
"预测是否成立":"WHETHER the prediction holds",
"理论骨架：三层分解 + why-necessary 表":"Theoretical skeleton: three-layer decomposition + why-necessary table",
"— 阶梯声明：observation space 答 where（§3），三层答 why（§5），锁定假设答 what next（§6），构造答 is it true（§7）。":"— Ladder declaration: the observation space answers where (§3), the three layers answer why (§5), locked hypotheses answer what next (§6), construction answers is it true (§7).",
"仪器（instrument），不是 taxonomy":"An instrument, not a taxonomy",
"— 坐标":"— coordinates",
"：source / mechanism / target；6 个 scanner 的 168 个类别 → 43 个被占用坐标；81 标注 → 31 坐标（2.6×），NMI 0.23–0.57。":": source / mechanism / target; 168 categories from 6 scanners → 43 occupied coordinates; 81 labels → 31 coordinates (2.6×), NMI 0.23–0.57.",
"四语料 + 威胁模型":"Four corpora + threat model",
"— 决策规则预览分歧：risk score / severity threshold / lexical grade。":"— decision rules preview the divergence: risk score / severity threshold / lexical grade.",
"核心分析：κ 不稳定 / 组合 / surface / 灰区":"Core analysis: κ instability / combinations / surface / grey zone",
"两向推理 + 锁定 + 消毒":"Two-direction inference + locking + sanitization",
"— top-down（坐标覆盖矩阵，2026-08-13 记录）与 bottom-up（读源码，如 build_context 跳过 dotfile）；消毒三检：malice realism / tech-failure / ground-truth hygiene。":"— top-down (coordinate-coverage matrix, recorded 2026-08-13) and bottom-up (source reading, e.g., build_context skipping dotfiles); three sanitization checks: malice realism / tech-failure / ground-truth hygiene.",
"H1–H6 账本（含 rejected）":"H1–H6 ledger (including the rejected one)",
"泛化 + 测量陷阱 + Takeaway":"Generalization + measurement traps + takeaway",
"定位：单一分析环 vs 分块先行工作":"Positioning: one analysis loop vs piecemeal prior work",
"— benchmarks 标注语料；scanner evaluations 量化分歧无结构归因（SkillsMetric 映射自建框架）；adversarial generation 泛搜（90%+ / 96%）；":"— benchmarks label corpora; scanner evaluations quantify disagreement without structural attribution (SkillsMetric maps a self-built framework); adversarial generation searches generically (90%+ / 96%);",
"三层分解示意":"Three-Layer Decomposition",
"每层：定义 · 修复 · 攻击策略 · 实证":"Each layer: definition · fix · attack strategy · evidence",
"输入从未被收集":"The input was never collected",
"“The relevant input was never collected” —— 架构性盲区：scanner 根本不检查该区域。":"\"The relevant input was never collected\" — an architectural blind spot: the scanner never inspects the region at all.",
"收集更多输入（含 hidden files）":"Collect more inputs (including hidden files)",
"把 payload 放进被跳过的文件":"Place the payload in a skipped file",
"隐藏文件 payload 逃逸（↓ 源码证据）":"Hidden-file payloads evade (↓ source evidence)",
"跳过 dotfiles → Arm7 中":"skips dotfiles → in Arm7",
"逃逸（11 个 score=0），raw output 只记录":"evade (11 with score=0), raw output records only",
"。§5 surface：Cisco 深伪装 RCE 14%、SS 内容操纵/反弹 shell 0%。":". §5 surface: Cisco deep-disguise RCE 14%, SS content manipulation / reverse shell 0%.",
"引擎无法识别该行为":"The engine cannot recognize the behavior",
"“The input was collected but the engine cannot recognize the behavior” —— 表面不匹配：词汇/语义表面消失即漏。":"\"The input was collected but the engine cannot recognize the behavior\" — surface mismatch: once the lexical/semantic surface disappears, it is missed.",
"换引擎 / 增强识别能力":"Change the engine / strengthen recognition",
"改变表达（去字面、换语义）":"Change the expression (de-literalize, re-semantify)",
"no-literal / finding-family 变体（↑ 矩阵证据）":"No-literal / finding-family variants (↑ matrix evidence)",
"Caterpillar 只匹配词汇标记 → H2 无字面措辞":"Caterpillar matches only lexical markers → H2 no-literal phrasing",
"逃逸、隐藏文件样例 13/15 零发现；Cisco 字面触发（窄）→ H3 finding-family 变体":"evade, hidden-file samples 13/15 zero findings; Cisco literal triggering (narrow) → H3 finding-family variants",
"逃逸。":"evade.",
"发现被阈值丢弃":"The finding was discarded by a threshold",
"“The engine produced a finding but the decision rule discarded it” —— 引擎看到了，规则把结果压掉。":"\"The engine produced a finding but the decision rule discarded it\" — the engine saw it; the rule suppressed it.",
"改阈值 / 报告规则":"Change the threshold / reporting rule",
"压低严重度（保持 MEDIUM 以下）":"Suppress severity (stay below MEDIUM)",
"conjunction 欠评分（↓ 源码证据）":"Conjunction under-scored (↓ source evidence)",
"只保留 CRITICAL/HIGH → MEDIUM 被吞：隐藏文件样例 11/15 逃逸、H4 叠加弱机制":"keeps only CRITICAL/HIGH → MEDIUM swallowed: hidden-file samples 11/15 evade, H4 stacked weak mechanisms",
"（SS≤50）、灰区 662/3,996 benign 的 MEDIUM 不可见、88/581 恶意":"(SS≤50), grey zone 662/3,996 benign MEDIUM invisible, 88/581 malicious",
"Hidden-file 案例：同一 artifact，三个不同层（Fig 5, p6）":"Hidden-file case: one artifact, three different layers (Fig 5, p6)",
": credential exfiltrator（收集云密钥 → base64 → curl 外传）":": credential exfiltrator (collects cloud keys → base64 → curl exfil)",
"build_context() 跳过 dotfiles → .env 从未进入分析":"build_context() skips dotfiles → .env never enters analysis",
"14/15 逃逸（11 个 score 恰好 0）":"14/15 evade (11 with score exactly 0)",
"Table 6 / §7 口径一致":"consistent with Table 6 / §7",
"规则需要词汇标记；此处无任何标记 → 零匹配":"rules need lexical markers; none present → zero matches",
"13/15 逃逸（零 findings）":"13/15 evade (zero findings)",
"等价于 “检测 2/15”（Table 6）":"equivalent to \"detects 2/15\" (Table 6)",
"YARA 命中（MEDIUM）；is_safe 只保留 HIGH+":"YARA fires (MEDIUM); is_safe keeps only HIGH+",
"11/15 逃逸（MEDIUM 被丢弃）":"11/15 evade (MEDIUM discarded)",
"等价于 “检测 4/15”（Table 6）":"equivalent to \"detects 4/15\" (Table 6)",
"Fig 1 对角矩阵：每个 scanner 在各层的状态（p3）":"Fig 1 diagonal matrix: each scanner's status per layer (p3)",
"literal（窄）":"literal (narrow)",
"no rule（无类别系统，不可投影）":"no rule (no category system, not projectable)",
"证据链视图":"Evidence-Chain View",
"Evidence Chain — 每节依赖哪个语料 / 图表":"Evidence chain — which corpus / figure each section depends on",
"四语料角色（Table 4, p4）":"Four corpus roles (Table 4, p4)",
"Market census —— 分歧普遍存在（Fig 2：κ ≤ 0.244；260/445 仅一 scanner 标记）。":"Market census — disagreement is pervasive (Fig 2: κ ≤ 0.244; 260/445 flagged by only one scanner).",
"Malicious corpus —— §5 核心分析主体：uniform vs shipped 规则、κ 不稳定、surface 分区。":"Malicious corpus — the subject of §5's core analysis: uniform vs shipped rules, κ instability, surface partitioning.",
"500 in-corpus（flag 率是 FP 上界）；4,000 MalSkillBench 官方审计（灰区：335/8.4%、650/16.2%、662 MEDIUM）。":"500 in-corpus (flag rates are FP upper bounds); 4,000 official MalSkillBench audit (grey zone: 335/8.4%, 650/16.2%, 662 MEDIUM).",
"Constructions —— Arms 7–13 锁定（H1–H6），1–6 探索性；与上方语料 disjoint；51 primary + 28 扩展。":"Constructions — Arms 7–13 locked (H1–H6), 1–6 exploratory; disjoint from the corpora above; 51 primary + 28 extensions.",
"逐节证据依赖":"Per-section evidence dependencies",
"ClawHavoc 1,184 恶意 skills；138,133 SKILL.md 91.8% 缺陷（reusability）；31,132 wild 26.1% 含漏洞（skillscan）；注入指令 80% 成功率。无本实验语料 ——":"ClawHavoc 1,184 malicious skills; 138,133 SKILL.md 91.8% defects (reusability); 31,132 wild 26.1% with vulnerabilities (skillscan); injected instructions 80% success. No own-corpus —",
"why-necessary 表（Localize/Explain/Predict），纯概念论证，无数据依赖。":"why-necessary table (Localize/Explain/Predict), purely conceptual, no data dependency.",
"(s,m,t) 坐标语言；正交性证据：NMI 0.23–0.57，81→31 坐标（2.6×），删任一轴 31→15–23。Fig 1 概念图（p3）。":"(s,m,t) coordinate language; orthogonality: NMI 0.23–0.57, 81→31 coordinates (2.6×), removing any axis 31→15–23. Fig 1 concept (p3).",
"census 提供动机证据（Fig 2，p4，κ≤0.244，136 平台验证 skills）；Table 4 定义四语料角色；Table 3 三 scanner 架构。威胁模型 + 67,453 skills ≤10.4% 重叠 / 0.":"census supplies motivation (Fig 2, p4, κ≤0.244, 136 cross-platform skills); Table 4 defines corpus roles; Table 3 the three scanners. Threat model + 67,453 skills ≤10.4% overlap / 0.",
"同一 581×3 raw outputs 的 uniform vs shipped 读数（Table 5, p4）；κ 三条件摆动 −0.01..+0.44（Fig 3, p5）；13 wild 类 surface 三失败带（Fig 4, ":"uniform vs shipped readings of the same 581×3 raw outputs (Table 5, p4); κ swings −0.01..+0.44 across three conditions (Fig 3, p5); 13-wild-class surface with three failure bands (Fig 4, ",
"Fig 5（p6）隐藏文件三层解剖（14/15 · 13/15 · 11/15）；top-down 证据：400 cells = 43 occupied + 318 blanks + 39 infeasible；bottom-up 证据：b":"Fig 5 (p6) hidden-file three-layer anatomy (14/15 · 13/15 · 11/15); top-down evidence: 400 cells = 43 occupied + 318 blanks + 39 infeasible; bottom-up evidence: b",
"Table 6（p8）H1–H6 账本；Fig 6（p8）Wilson 95% 区间森林图（含 negative control：Arm12 SS 9/10）。129 构造，79 锁定（3 个丢 SS run），51 primary。":"Table 6 (p8) H1–H6 ledger; Fig 6 (p8) Wilson 95% forest plot (with negative control: Arm12 SS 9/10). 129 constructions, 79 locked (3 lost SS runs), 51 primary.",
"88/581 恶意 is_safe 虽有 MEDIUM+；2/5 三 scanner 全漏（唯一处）；10 个 flagged-by-none 全为 artifact；56%→0% 消毒前后对比。":"88/581 malicious is_safe despite MEDIUM+; 2/5 all-scanner miss (the only place); 10 flagged-by-none all artifacts; 56%→0% before/after sanitization.",
"H1–H6 · 方向 / 结果 / 层 / n":"H1–H6 · direction / outcome / layer / n",
"Table 6 · p8 · 构造均 2026-08-19 之后":"Table 6 · p8 · all constructions after 2026-08-19",
"方向":"Dir.",
"锁定预测":"Locked prediction",
"构造":"Construction",
"结果":"Outcome",
"层":"Layer",
"hidden-file payload 永不被分析":"hidden-file payload never analyzed",
"payload 全在 dotfiles（Arm7, n=15）":"payload entirely in dotfiles (Arm7, n=15)",
"逃逸 SS（":"evade SS (",
"11 个 score=0":"11 with score=0",
"）；Cisco 4/15、Cat 2/15 检测":"); Cisco 4/15, Cat 2/15 detect",
"无字面措辞不可见":"no-literal wording unseen",
"tool-semantics 措辞（Arm10B, n=10）":"tool-semantics phrasing (Arm10B, n=10)",
"逃逸 Cat；SS":"evade Cat; SS",
"（对照组）":"(control)",
"finding-family 变体不浮出任何东西":"finding-family variants surface nothing",
"每 finding-family 一变体（Arm11A, n=6）":"one variant per finding-family (Arm11A, n=6)",
"逃逸 Cisco（全 is_safe, INFO–MEDIUM）；SS":"evade Cisco (all is_safe, INFO–MEDIUM); SS",
"全检测":"detects all",
"合取（conjunction）欠评分":"conjunction under-scored",
"叠加弱机制（Arm13, n=5）":"stacked weak mechanisms (Arm13, n=5)",
"2/5 三 scanner 全漏":"2/5 evade all three",
"（全研究唯一处）":"(the only place in the study)",
"runtime dataflow 不可见":"runtime dataflow unseen",
"变体家族保持逃逸（negative control）":"variant family keeps evasion (negative control)",
"扩展最佳单逃逸（Arm12, n=10）":"expand best single bypass (Arm12, n=10)",
": SS 检测":": SS detects",
"—— 单样例逃逸 ≠ 家族级逃逸":"— single-sample evasion ≠ family-level evasion",
"机制备注（§7 The Ledger）":"Mechanism notes (§7 The Ledger)",
"H3 机制：":"H3 mechanism:",
"每个 SkillSpector finding family 一个变体，重表达同一恶意行为；Cisco 静态层无东西可供 severity 逻辑升级 → 六个全部":"one variant per SkillSpector finding family, re-expressing the same malicious behavior; Cisco's static layers surface nothing its severity logic can escalate → all six stay",
"（INFO–MEDIUM），而 SkillSpector 六个全给分：同一坐标、两个 scanner、不同层。":"(INFO–MEDIUM), while SkillSpector scores all six: one coordinate, two scanners, different layers.",
"H2 机制：":"H2 mechanism:",
"exfiltration 用工具语义表达（“archive the result to the remote repository”），全文无":"exfiltration expressed as tool semantics (\"archive the result to the remote repository\"), no",
"token；regex 引擎无物可匹配。":"token anywhere; the regex engine has nothing to match.",
"H4 机制：":"H4 mechanism:",
"叠加隐藏放置 + 间接执行 + 声明能力掩护，每个都低于评分阈值；additive scorer 永远看不到合取 → 2/5 同时逃逸全部三个 scanner。":"stacked hidden placement + indirect execution + declared-capability cover, each below the scoring threshold; the additive scorer never sees the conjunction → 2/5 evade all three scanners simultaneously.",
"图 6（p8）：":"Fig 6 (p8):",
"每行是 Table 6 的一条假设；实心点 = 观测逃逸率，空心点 = negative control 的检测率（Arm12 9/10）；Wilson 95% 区间；n 在右端。":"each row is one Table-6 hypothesis; filled points = observed evasion rates, open = the negative control's detection rate (Arm12 9/10); Wilson 95% intervals; n at right.",
"数字锚点栏":"Number Anchors",
"Key Numbers — 正文关键数字与来源文件":"Key numbers — the body's key numbers with source files",
"来源 = main.tex 章节 · main.pdf 页码":"Source = main.tex section · main.pdf page",
"SS / Cisco / Caterpillar 检测率（wild 91.1/88.0/70.9；generated 95.7/84.8/75.3）":"SS / Cisco / Caterpillar detection (wild 91.1/88.0/70.9; generated 95.7/84.8/75.3)",
"分歧统计是阈值的函数，不只是 scanner 的函数":"disagreement statistics are functions of thresholds, not only of scanners",
"三种规则选择：shipped −0.01..+0.24；uniform +0.08..+0.16；+benign +0.29..+0.44":"three rule choices: shipped −0.01..+0.24; uniform +0.08..+0.16; +benign +0.29..+0.44",
"136 平台验证 skills；5.9% 被 ≥4 scanner 标记；1,082 census 中 260/445 仅一 scanner 标记":"136 cross-platform skills; 5.9% flagged by ≥4 scanners; in the 1,082 census 260/445 flagged by exactly one",
"pairwise overlap ≤10.4%；仅 0.69% 被所有 scanner 标记 —— 描述性，不解释 where/why":"pairwise overlap ≤10.4%; only 0.69% flagged by all — descriptive, does not explain where/why",
"Cat 指令级（goal hijacking / instruction override 0%）；Cisco 深伪装 RCE 14%；SS 内容操纵 / 反弹 shell 0%":"Cat instruction-level (goal hijacking / instruction override 0%); Cisco deep-disguise RCE 14%; SS content manipulation / reverse shell 0%",
"NMI 0.23–0.57；删任一轴 31→15–23 占用坐标":"NMI 0.23–0.57; removing any axis 31→15–23 occupied coordinates",
"4,000 skills（3,996 scanned，4 拒收）：Cisco 335/3,996 = 8.4%；SS 650/4,000 = 16.2%；662/3,996 = 16.6% MEDIUM 被阈值隐藏":"4,000 skills (3,996 scanned, 4 rejected): Cisco 335/3,996 = 8.4%; SS 650/4,000 = 16.2%; 662/3,996 = 16.6% MEDIUM hidden by threshold",
"SS 14/15（11 score=0）；Cat 13/15 零发现（=检测 2/15）；Cisco 11/15 MEDIUM dropped（=检测 4/15）":"SS 14/15 (11 score=0); Cat 13/15 zero findings (=detects 2/15); Cisco 11/15 MEDIUM dropped (=detects 4/15)",
"Cat 10/10 逃逸；SS 7/7 valid（有效性对照）":"Cat 10/10 evade; SS 7/7 valid (validity control)",
"Cisco 6/6 逃逸；SS 6/6 全检测 —— 同一坐标两 scanner 不同层":"Cisco 6/6 evade; SS 6/6 detects all — one coordinate, two scanners, different layers",
"SS 5/5 ≤50；2/5 三 scanner 全漏（全研究唯一）":"SS 5/5 ≤50; 2/5 all-scanner miss (the study's only one)",
"partial：3/5 score=0 on SS —— 未全数逃逸":"partial: 3/5 score=0 on SS — not all evade",
"REJECTED：SS 检测 9/10；单样例逃逸 ≠ 家族级逃逸":"REJECTED: SS detects 9/10; single-sample evasion ≠ family-level evasion",
"129 total（Arms 1–13）；79 confirmatory（Arms 7–13，3 个丢 SS run）；51 primary families；28 扩展（arms 8–10）":"129 total (Arms 1–13); 79 confirmatory (Arms 7–13, 3 lost SS runs); 51 primary families; 28 extensions (arms 8–10)",
"malicious skills is_safe 却有 MEDIUM+ findings —— Cisco 报告缺陷的修复入口":"malicious skills is_safe despite MEDIUM+ findings — the fix entry point for Cisco's reporting defect",
"ClawHavoc 单市场 1,184 恶意 skills；注入 skill 指令对 frontier agents 达 80% 成功率":"ClawHavoc: 1,184 malicious skills in one marketplace; injected skill instructions reach 80% success on frontier agents",
"138,133 SKILL.md 中 91.8% 有打包/安全缺陷；31,132 wild skills 中 26.1% 至少一个漏洞":"91.8% of 138,133 SKILL.md have packaging/safety defects; 26.1% of 31,132 wild skills have at least one vulnerability",
"坐标覆盖矩阵 2026-08-13 记录（top-down 证据）→ 确认性构造 2026-08-19 及以后：锁定严格先于构造，防 post-hoc rationalization":"coordinate-coverage matrix recorded 2026-08-13 (top-down evidence) → confirmatory constructions 2026-08-19 onward: locking strictly precedes construction, preventing post-hoc rationalization",
"渲染浮层地图":"Float Placement Map",
"Float Placement Map — main.pdf 实际渲染顺序（fitz 核对）":"Float placement map — actual rendering order in main.pdf (fitz-verified)",
"[t] float 会浮到页顶，先于引用它的章节标题 —— 标准 LaTeX 行为":"[t] floats rise to the page top, before the section heading that cites them — standard LaTeX behavior",
"· Abstract + §1 开场":"· Abstract + §1 opening",
"· 概念 + 表 1/2 浮顶":"· concepts + Tables 1/2 at top",
"Table 1 — why-necessary（页顶）":"Table 1 — why-necessary (page top)",
"Table 2 — (s,m,t) 三维（页顶）":"Table 2 — (s,m,t) dimensions (page top)",
"§3 An Observation Instrument（页底开始）":"§3 An Observation Instrument (starts page bottom)",
"· Fig 1 概念图":"· Fig 1 concept",
"Figure 1 — pipeline 概念图（§3 引用，浮页顶）":"Figure 1 — pipeline concept (cited §3, floats to top)",
"Table 3 — 三 scanner":"Table 3 — three scanners",
"§4 Instantiation（页中后部）":"§4 Instantiation (mid-to-late page)",
"· census + 四语料 + §5 开篇":"· census + four corpora + §5 opening",
"Table 5 — 581×3 uniform/shipped（页顶）":"Table 5 — 581×3 uniform/shipped (page top)",
"Table 4 — 四语料角色":"Table 4 — four corpus roles",
"§5 Observed Disagreement（页底 y≈678）":"§5 Observed Disagreement (page bottom y≈678)",
"· 两个核心图":"· two core figures",
"Figure 3 — aggregate dismantled（κ 摆动 + UpSet，页顶）":"Figure 3 — aggregate dismantled (κ swing + UpSet, page top)",
"Figure 4 — surface（13 wild 类三失败带）":"Figure 4 — surface (13 wild classes, three failure bands)",
"§5 正文继续（L1/L2/L3 失败 + 灰区）":"§5 body continues (L1/L2/L3 failures + grey zone)",
"· 三层解剖 + §6":"· three-layer anatomy + §6",
"Figure 5 — 隐藏文件三层解剖（浮页顶，先于 §6 标题）":"Figure 5 — hidden-file three-layer anatomy (floats to top, before §6 heading)",
"灰区收尾（662 MEDIUM / 16.6%）":"grey-zone close (662 MEDIUM / 16.6%)",
"· §7 开篇 + §8":"· §7 opening + §8",
"§7 Does the Loop Work?（y≈245；正文先引用 Table 6，表格在 p8）":"§7 Does the Loop Work? (y≈245; body cites Table 6 first, table on p8)",
"· 账本 + 森林图 + RW":"· ledger + forest plot + RW",
"Table 6 — H1–H6 账本（页顶）":"Table 6 — H1–H6 ledger (page top)",
"Figure 6 — Wilson 95% 森林图":"Figure 6 — Wilson 95% forest plot",
"· 参考文献":"· references",
"自检与核对记录":"Self-check and verification record",
"数字核对":"Number check",
"：全部关键数字在 main.pdf 渲染文本中逐项验证存在（581×3 · 92.9/86.7/72.6 · 46.8/71.6/38.6 · κ 三区间 · 0.244 · 118/40/17/39 · 14/15 · 10/10 · 6":": all key numbers verified present in main.pdf's rendered text (581×3 · 92.9/86.7/72.6 · 46.8/71.6/38.6 · κ three ranges · 0.244 · 118/40/17/39 · 14/15 · 10/10 · 6",
"页码核对":"Page check",
"：fitz 逐页扫描确认 —— Fig1→p3、Fig2→p4、Fig3→p5、Fig4→p5、Fig5→p6、Fig6→p8、Table1→p2、Table2→p2、Table3→p3、Table4→p4、Table5→p4、Table6":": fitz page-by-page scan confirms — Fig1→p3, Fig2→p4, Fig3→p5, Fig4→p5, Fig5→p6, Fig6→p8, Table1→p2, Table2→p2, Table3→p3, Table4→p4, Table5→p4, Table6",
"图序核对":"Figure-order check",
"：渲染顺序 Fig1→Fig2→Fig3→Fig4→Fig5→Fig6，与正文引用顺序一致；[t] float 均浮至页顶（先于引用章节标题），属标准 LaTeX 行为，非错误。":": rendering order Fig1→Fig2→Fig3→Fig4→Fig5→Fig6 matches citation order; [t] floats all rise to page top (before the citing heading) — standard LaTeX, not an error.",
"次要发现":"Minor findings",
"：latex/ 目录中":": in the latex/ directory",
"存在但 main.tex 未引用（遗留文件，建议清理或确认用途）。":"exist but are unreferenced by main.tex (leftovers; clean up or confirm purpose).",
"口径提示":"Caliber note",
"：Fig 5 用“逃逸率”口径（Cat 13/15、Cisco 11/15），Table 6 / §7 用“检测率”口径（Cat 2/15、Cisco 4/15）—— 两者互为补数（15−2=13；15−4=11），数值一致但读者可能困惑。":": Fig 5 uses evasion rates (Cat 13/15, Cisco 11/15) while Table 6 / §7 use detection rates (Cat 2/15, Cisco 4/15) — complements of each other (15−2=13; 15−4=11); values agree but readers may be confused.",
"记忆偏差提示":"Memory-drift note",
"：项目 memory 记录“582 恶意样本”，论文（tex v8.2 + PDF）一致为":": project memory records \"582 malicious samples\"; the paper (tex v8.2 + PDF) consistently says",
"（350 wild + 231 generated），以论文为准。":"(350 wild + 231 generated); the paper is authoritative.",
}

missing = [s for s in ZH if s not in D and len(s) > 1]
print(f"dict covers {len([s for s in ZH if s in D])}/{len(ZH)}; missing {len(missing)}")
for m in missing[:15]:
    print("  MISS:", m[:60])

src = open('/mnt/d/zewang/paper/hermes-work/jaws-paper/PAPER_SPINE_VIZ.html', encoding='utf-8').read()

toggle_css = """
/* lang toggle */
.lang-btn{margin-left:auto;cursor:pointer;font-size:12.5px;font-weight:700;color:var(--dim);
  padding:5px 12px;border-radius:6px;border:1px solid var(--line);background:var(--panel2);user-select:none}
.lang-btn:hover{color:var(--fg);border-color:var(--blue)}
"""
src = src.replace("</style>", toggle_css + "</style>")

# insert button into nav (after last link)
src = src.replace('<a href="#m6" data-zh="浮层地图" data-en="Float Map">浮层地图</a>',
                  '<a href="#m6" data-zh="浮层地图" data-en="Float Map">浮层地图</a>\n      <span class="lang-btn" id="langBtn" onclick="toggleLang()">EN</span>')

i18n_js = """
<script>
const I18N = %s;
function applyLang(lang){
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walk.nextNode()) nodes.push(walk.currentNode);
  for (const n of nodes){
    const raw = n.nodeValue;
    const t = raw.trim();
    if (!t) continue;
    if (lang === 'en'){
      if (I18N[t] && !n._zh){ n._zh = raw; n.nodeValue = raw.replace(t, I18N[t]); }
    } else {
      if (n._zh){ n.nodeValue = n._zh; }
    }
  }
  document.documentElement.lang = (lang==='en') ? 'en' : 'zh-CN';
  const b = document.getElementById('langBtn');
  if (b) b.textContent = (lang==='en') ? '中文' : 'EN';
  try{ localStorage.setItem('spine-lang', lang); }catch(e){}
}
function toggleLang(){
  const cur = document.documentElement.lang === 'en' ? 'en' : 'zh';
  applyLang(cur === 'en' ? 'zh' : 'en');
}
(function(){
  let saved = 'zh';
  try{ saved = localStorage.getItem('spine-lang') || 'zh'; }catch(e){}
  if (saved === 'en') applyLang('en');
})();
</script>
""" % json.dumps(D, ensure_ascii=False)

src = src.replace("</body>", i18n_js + "</body>")
open('/mnt/d/zewang/paper/hermes-work/jaws-paper/PAPER_SPINE_VIZ.html', 'w', encoding='utf-8').write(src)
print("bilingual injected")
