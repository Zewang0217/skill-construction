# JAWS 2026 Idea Paper — 8 页结构大纲 v2

> 状态：大纲 v2（GPT 反馈收缩后）| 2026-08-21
> 核心转变：从"四个并列贡献"→"一个核心发现 + 方法链"
> Paper identity: **A methodology for structural analysis of security scanner disagreement**

---

## Paper Identity（一句话定位）

> **We introduce a coordinate-based methodology for analyzing why agent-skill security scanners disagree and for converting the resulting structural gaps into testable blind-spot hypotheses.**

不是：malicious skill generation / 不是 new taxonomy / 不只是 benchmark。
是：**把 scanner disagreement 从统计症状变成可分析、可验证的对象。**

## 贡献结构（收缩后）

```
                 CORE CLAIM
                      │
      Scanner blind spots have structure;
      disagreement is analyzable, not just observable
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        C1            C2          C3
   measurement    explanation   validation
    space         (★ 主贡献)    methodology
   (instrument)                 (construction)
                                  │
                                  ▼
                                 C4
                          mechanism evidence
                          (causal, source-level)
```

- **C2 是 paper**。C1 是仪器（没有它无法比较异构扫描器）、C3 是验证方法（证明不是 post-hoc）、C4 是因果证据（证明不是 correlation）。

## Title 候选（待选）

1. "From Symptom to Structure: Coordinate-Based Structural Analysis of Agent-Skill Security Scanner Disagreement"
2. "Where and Why Scanners Disagree: A Coordinate-Based Methodology for Agent-Skill Security Scanners"
3. "Turning Scanner Disagreement into Testable Blind-Spot Hypotheses"

---

## 正文结构（8 页，方案：主线优先 + 收缩）

### §1 Introduction（1 页）
- **Hook**：扫描器分歧（κ≈0）是症状，不是诊断。现有评测量化"是否分歧"，无法回答"在哪、为什么、能否预测"。
- **Intellectual hook**（GPT 认可句）：
  > Existing evaluations can measure whether scanners disagreed, but cannot explain where the disagreement originates or predict unseen blind spots.
- **Our approach**：
  > We turn disagreement from an observable symptom into an analyzable structure.
  方法链：symptom → structure → hypothesis → validation
- **Contributions**（收缩为一条链）：
  - Core：Structural Disagreement Analysis（C2）
  - Enabling：C1 measurement space / C3 hypothesis-driven construction / C4 mechanistic tracing
- **Key results 一句话**：hidden-file payloads bypass SS 93%；expression variants evade Cisco 100%；combined strategies evade SS 100%（5/5）。

### §2 Shared Attack-Coordinate Space（1 页）【原 Measure，去理论化】
- **Framing**：measurement instrument，不是 taxonomy paper。
  > Existing scanners describe threats using incompatible vocabularies. We operationalize these heterogeneous labels into a compositional coordinate space for cross-scanner comparison.
- 三维：来源×方式×目标 → 43 坐标（67 类翻译表）
- **一个关键数字**：56.5% 部分三元组（现有体系连完整表达都做不到）
- 理论出处（Dolev-Yao/ATT&CK/CIA）**砍到 1 句**；NMI **砍到 1 句或删**

### §3 Structural Disagreement Analysis（1.5 页）【★ 主贡献章节】
- **方法**：把三家扫描器检出映射到坐标 → 逐坐标对比
- **Discovery 1 — Coverage Gap**：扫描器不覆盖的坐标
  - 582 真实恶意 × 3 家：SS 92.8% / Cisco 85.2% / Cat 72.5%
  - 按坐标分解 + **来源轴集体失明**（post-taxonomy κ_source = −0.137）
- **Discovery 2 — Operational Divergence**：同坐标但判法不同
  - SS 从脚本代码取证 / Cisco 依赖字面命令 / Cat 纯正则
- **（压缩 1-2 句）Misclassification**：S3 试点 30 findings 全「危险但合法」

### §4 From Analysis to Blind-Spot Hypotheses（0.75 页）【新增·方法论新颖性】
- **Hypothesis generation protocol**：
  ```
  Evidence → Hypothesis → Lock → Construction spec → Validation
  ```
- **两类证据源（诚实拆分，GPT 关键修正）**：
  - **Type A — Coordinate coverage evidence**：覆盖矩阵 → 坐标 X 未覆盖 → 预测漏检
  - **Type B — Scanner architecture evidence**：读实现（如 build_context.py 跳 dotfile）→ 预测隐藏文件盲区
  - **不宣称**"taxonomy magically predicts everything"，而是 **evidence-driven blind-spot hypothesis workflow**，坐标空间是统一 observation layer
- **Hypothesis locking**：时间线证明（08-13 盲区矩阵先于 08-19 构造；Arm7 源码分析在先）

### §5 Validation and Mechanistic Analysis（2 页）
- **Centerpiece — Arm7 hidden-file → SS**（完整因果链详讲）：
  ```
  implementation property (build_context.py skips dotfiles)
      → hypothesis → lock → construction → 14/15 bypass → mechanism confirmed
  ```
- **Confirming cases table**（其余压成一张表）：
  | Scanner | Predicted weakness | Construction | Result | Mechanism |
  |---|---|---|---|---|
  | Cisco | expression layer | Arm11A finding 特化 | 0/6 (100% 绕) | 无字面无触发面 |
  | Cat | regex layer | Arm10B 无字面 | 0/10 (100% 盲) | 纯正则无语义 |
  | SS | composition | Arm13 组合策略 | 5/5 绕 + 2 全漏 | 多策略叠加 |
  | SS | wild mechanism | Arm11B 变量注入管道 | SS=0 | wild 机制复现 |
- **Honest scoping**：Arm1-6 exploratory；Arm7-13 confirmatory；Arm12 扩样不可复现（单样本绕过≠稳定绕过）

### §6 Discussion & Related Work（0.75 页）
- **三个 implications**：
  1. scanner evaluation should be coordinate-aware
  2. single-scanner governance inherits blind spots
  3. hypothesis locking for adversarial evaluation
- **Related work 叙事段落**（不用能力矩阵表）：
  > Prior work addresses individual parts: benchmarks provide corpora but not a shared measurement space; scanner evaluations quantify disagreement but do not structurally attribute it; adversarial generation exposes failures but is not driven by an explicit attack-space hypothesis; implementation analyses identify individual bugs but do not connect them to a cross-scanner attack model. **Our approach connects these steps into a single analysis loop.**
- **Future**：TOSEM/TSE 扩展（完整 benchmark + 新防御原型）

**页数核算**：1 + 1 + 1.5 + 0.75 + 2 + 0.75 = 7 页正文 + 参考文献 → 留 1 页缓冲（图表/溢出）

---

## 数据引用索引（不变）

| 数字 | 来源 |
|---|---|
| 582 检出率 85.2/92.8/72.5 | verdict_all.csv + FINAL_REPORT |
| 56.5% 部分三元组 | COVERAGE_TEST_V1.md |
| κ_source −0.137 | S1_RESULTS.md |
| 43 坐标 / 67 类翻译表 | s4-slots-full.csv + SCANNER_VERDICT_TRANSLATION.csv |
| Arm7 SS 93% 绕 | verdict_arm7.csv |
| Arm11A Cisco 0/6 | verdict_arm11.csv |
| Arm10B Cat 0/10 | verdict_arm10b.csv |
| Arm13 SS 5/5 绕 | verdict_arm1213.csv |
| Arm11B SS=0 | verdict_arm11.csv |
| build_context.py / models.py:226 | 扫描器源码 |

## 图表计划（收缩）

| 图 | 内容 | 位置 |
|---|---|---|
| Fig 1 | 方法链：symptom→structure→hypothesis→validation | §1 |
| Fig 2 | 582 × 3 家坐标覆盖热力图 | §3 |
| Table 1 | Confirming cases（Cisco/Cat/Arm13/Arm11B） | §5 |
| Fig 3（可选） | Arm7 centerpiece 因果链 | §5 |
