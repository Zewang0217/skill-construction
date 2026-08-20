# GPT 反馈全文落盘（2026-08-20，针对 v6 稿）

> 来源：用户转交 GPT 对 paper_v6 的长篇评审。本文件逐字保留原意见，供 v7 重构对照。
> 状态标记（Zewang 侧批注，落盘时加）：
> [ADOPT] 采纳 | [ADOPT-MOD] 采纳但修改 | [DECLINE] 不采纳（含理由）| [ALREADY] v6 已做

---

## 总判断

> 这篇现在已经有一个不错的 research idea 了，而且 "Disagreement → Structure → Hypothesis → Validation" 这条主线是成立的。
> 但目前最大的问题不是"idea 不够"，而是你把一个应该非常尖锐的 JAWS idea paper，写成了一篇同时想做 taxonomy / benchmark / scanner evaluation / adversarial benchmark / source analysis 的小型 full paper。
> 三个症状：内容多但核心被稀释；数据多但证明核心 idea 的证据不集中；图表多但没有共同服务一个 narrative，甚至功能重叠。
> 现在不是"继续加数据、加实验"的阶段，而是应该先做一次 paper identity 的重新收束。

[ADOPT] 与七-agent 盘点结论一致（三类研究单位混用）。v6 已部分收束，但 taxonomy 篇幅仍超仪器定位。

## 一、贴不贴 JAWS

> 已经贴了 60~70%，但还可以明显更贴。核心 idea 是 methodological reframing：不是提出新 scanner，而是提出一种新的研究 automated analysis disagreement 的方法。
> "The object is timely; the methodology is the contribution." 这句写了，但文章本身还没完全做到。

[ADOPT]

## 二、重新定义唯一中心

> **We turn disagreement among automated analyses from a scalar evaluation outcome into a structured object that can generate falsifiable hypotheses about analysis blind spots.**
> 关键词不是 disagreement measurement / taxonomy / benchmark / adversarial generation，而是 **disagreement → hypothesis generation**。别人可以跑三个 scanner 算 kappa 报 overlap；我们提出 scanner disagreement → semantic alignment → localization → structural interpretation → blind-spot prediction → pre-locked validation。

[ADOPT] thesis 句直接采用。

## 三、文章里有"四个 Paper"

> Paper A：Disagreement as Evidence（最强，应是主角）。
> Paper B：Agent Skill Threat Taxonomy（168 categories / 43 coordinates / 1253 statements / 84 sources / NMI / gold standard——太像另一篇 paper；reviewer 会拖进 taxonomy debate：为什么三维、为什么不是 MITRE、17.9% full triple 为什么低、318 blanks 怎么来）。
> 建议：保留 coordinate space，但从 "Contribution #1: 我提出 taxonomy" 变成 "An observation instrument needed to make disagreement comparable"。

[ADOPT] v6 已做仪器定位，但 §2 仍有 NMI/2.6×/45% 炫技段（v6 已压缩过一轮，还需再压）。

## 四、Section 3 "数据炫技化"

> 建议压成：We need a common observation language... 只保留一两个必要性数字（56.5% partial triples 可留）。NMI、2.6x、45% 弱化或放 appendix。

[ADOPT]

## 五~七、图的问题

### fig_pipeline（Fig 1）
> 概念好，画法有问题：文字太多（把 paragraph 塞进 box）；左右信息密度不平衡；与 fig_oneload 功能重叠。
> Figure 1 应该是整篇 paper 的理论模型，不需要解释具体 attack。重新设计为 CURRENT PRACTICE（artifact→3 scanners→κ→STOP）vs OUR VIEW（artifact→observation space→decomposition→hypotheses→locked validation）。

[ADOPT] 重画。

### fig_disagreement 拆分
> 三联图像"我做了三个实验所以拼一张"。(a) κ instability → dot-range plot 更像论文；(b) flag combination → **UpSet Plot**（不要普通柱状图）；(c) detection by class → heatmap 保留。
> 建议 Fig2 κ instability / Fig3 UpSet / Fig4 heatmap，或压缩为 4 张强图：Fig1 Concept / Fig2 Empirical / Fig3 Prediction→validation / Fig4 Mechanism trace。

[ADOPT-MOD] 页数预算（≤8页）下：Fig 2 保留全宽但重做面板（κ dot-range + UpSet + heatmap 三面板改为排版统一），不拆成三张独立图。

### fig_oneload 重画
> 概念是全文最重要的 demonstration，但现在是 PPT 式 box→box。改为 Three-layer failure anatomy 横向三列：SAME ARTIFACT（SKILL.md benign + .env payload）→ SkillSpector=FILE COLLECTION / Cisco=DECISION POLICY / Caterpillar=DETECTION SURFACE → 各自 ✗ + 比率 → 底部一行 failure mechanism 分类。

[ADOPT] 与"三层分解"（见 §十三）统一后重画。

## 八、颜色系统

> 现在 gray/blue/green/orange/red 混用是 TikZ 默认彩色 box 风格，显廉价。建立 semantic palette：Gray=existing/input，Blue=analytical structure，Orange=predicted issue，Red=observed failure，Green=validated evidence。颜色必须 encode semantics。

[ADOPT]

## 九~十、数据组织

> 样本量不是问题（581/500/129/79 都够），问题是数据没有全部围绕一个 hypothesis test 来组织。reviewer 真正想看的是 **Prediction Power Table**：Hypothesis Source / Prediction / n / Predicted Failure / Observed Failure / Mechanism Confirmed。比"我有 581 samples"更重要，因为核心 claim 是 "The structure predicts blind spots"。

[ADOPT] v6 的 tab:cases 升级为 prediction ledger。

## 十一、增加"失败的 prediction"

> Arm12: 9/10 detected 很好，进一步强化。reader 看到"全部命中"会怀疑 post-hoc rationalization。报告 5 hypotheses: 4 confirmed, 1 partial, 1 rejected（含 ✗ 行），并说 "The framework does not guarantee bypasses. It generates falsifiable hypotheses." 卖的不是"我能找到 bypass"而是"我能从 disagreement 中产生可证伪的 hypotheses"。

[ADOPT] 已有真 rejection 素材：Arm12（家族级绕过未成立）、Arm10 初版（载荷时序假设被净化推翻）、Arm11B partial (3/5)。

## 十二、"非我们不可"还差一步：Baseline 对比表

> | 方法 | Can localize? | Can explain? | Can predict before test? |
> | Recall/κ | ✗✗✗ | | |
> | Manual post-hoc | ✓✓✗ | | |
> | Ours | ✓✓✓ | | |
> 这张表回答 Why is this idea necessary。

[ADOPT] 新增小表。

## 十三、结构重组

> 1 Intro（只做"我们测分歧但不用它"+running example，数字后置）
> 2 The Core Idea: From disagreement statistics to disagreement structure
> **三层 disagreement decomposition：Layer1 Coverage（scanner 看了吗）/ Layer2 Detection（检测机制认得出吗）/ Layer3 Decision（系统把 finding 转成 block 了吗）**——比 coverage gap + operational divergence 更完整；hidden-file 图正好证明 SS=Coverage failure / Cisco=Decision failure / Caterpillar=Detection failure。"你现在 paper 里面实际上已经有这个东西了，只是你自己还没有把它提炼出来。"
> 3 Shared Observation Language（缩短，只是 localization instrument）
> 4 Method（Step1 observe → Step2 localize → Step3 decompose → Step4 hypothesize → Step5 lock → Step6 construct → Step7 validate）
> 5 Instantiation（数据集/tool 放这里）
> 6 Does the methodology work?（按 H1/H2/H3 组织 + prediction table + validation plot）
> 7 What does this change?

[ADOPT] 三层分解是本次反馈最高价值建议，与数据天然对齐（SS=Coverage/Cisco=Decision/Cat=Detection，benign-4000 的 662 MEDIUM 不可见也是 Decision 层）。v7 理论骨架采用。

## 十四~十六、工具与流程

> TikZ 适合简单概念图；建议 Figma→SVG/PDF（Fig1/anatomy）、Python+matplotlib（κ/heatmap/forest/UpSet）、Graphviz（pipeline）。建立 Figure Pipeline：先写 Figure question（ONE thing），再画 information architecture（ASCII），再视觉设计。缺的是 art direction 不是 draw skill。

[ADOPT-MOD] Figma 工作流在 08-22 deadline 前不现实；采用 matplotlib（数据图）+ 重写简化 TikZ（概念图，语义色）替代。

## 十七、优先级

> 1 paper identity surgery（taxonomy/benchmark/evaluation/adversarial 全部降级为 evidence）
> 2 提炼 Coverage/Detection/Decision 三层分解
> 3 增加 prediction capability 证据（positive/partial/negative + prediction precision）
> 4 重新设计全部 Figure（4-5 张：The Idea / Why Metrics Insufficient / Prediction Pipeline / Validation / One Failure Anatomy）
> 5 最后再判断缺什么数据。先不要动实验。

[ADOPT] 执行顺序即此。

## 附：用户补充线索（Zewang）

- `D:\Zewang\paper\skills-scanner-study\reports\data_explorer.html`：项目第 0 周的 wild 扫描全景（1082 市场技能 × SS/Snyk/Socket/ATH），κ≈0 跨平台、260/445 单家独占、0.6% 四家共识——项目起源数据，此前未被任何盘点覆盖（在 hermes-work/ 之外）。v7 用作 §1/§5 motivation 证据（标注与主实验 scanner 集不同）。
