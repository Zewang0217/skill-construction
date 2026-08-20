# JAWS Claim 定稿讨论（GPT 反馈 + 我的评估）

> 2026-08-21 | 状态：讨论中
> 输入：GPT 对 claim 的详细反馈 + 我的评估 + 待讨论问题

---

## 一、GPT 反馈核心（我认同的部分）

### 1. Headline 调整 ✅
- ❌ 不是"我们提出了三维 taxonomy"
- ✅ 是"统一坐标空间让 scanner disagreement 变得可解释、可预测"
- Taxonomy 是 instrument，不是最终贡献

### 2. 论文逻辑链 ✅
```
Scanner outputs heterogeneous → disagreement uninterpretable
→ unified coordinate space → disagreement decomposable
→ coverage gap vs operational divergence
→ coordinate-level hypothesis → adversarial construction
→ prediction validated → blind spots are structural
```

### 3. 两个措辞修正 ✅
- "不是随机" → "A substantial class of scanner blind spots can be explained—and in some cases predicted—by their structural coverage and operationalization of the attack space"
- "预测全部命中" → 需要定义 prediction protocol（pre-construction hypothesis locking）

### 4. C2 是主贡献 ✅
- κ tells you *that* scanners disagree
- We tell you *where* and *why*
- 术语：**Structural Disagreement Analysis**

### 5. 贡献重排 ✅
- C1 = Shared Measurement Space（不是 taxonomy invention）
- C2 = Structural Disagreement Analysis（主贡献）
- C3 = Predictive Adversarial Construction
- C4 = Architecture-grounded Explanation（不说"独有"）

### 6. Conceptual Model ✅
**Measure → Explain → Predict → Validate**（直接是 Abstract 骨架）

### 7. 术语 ✅
- "Descriptive categorization vs Constructive attack space"（不用"generative taxonomy"，风险大）
- "attack-space operationalization"（reviewer 更容易接受）

### 8. GPT 最终 Claim 版本
> Existing evaluations can measure whether agent-skill security scanners disagree, but cannot explain where the disagreement originates or predict unseen blind spots. We introduce a shared three-dimensional attack-coordinate space that maps heterogeneous scanner languages into a common measurement framework. This enables structural disagreement analysis, distinguishing coverage gaps from within-coordinate operational divergence. We then use these structural gaps to formulate blind-spot hypotheses and validate them through coordinate-driven adversarial construction. Across three production scanners and 582 real malicious skills, the predicted blind spots consistently manifest in 129 constructed samples, with source-level analysis linking selected failures to concrete detection mechanisms.

---

## 二、我的评估：认同 + 补充

### 完全认同
1. Headline 调整（taxonomy 是工具不是贡献）
2. C2 是主贡献（structural disagreement analysis）
3. Measure → Explain → Predict → Validate 框架
4. "Descriptive vs Constructive" 术语
5. 不说"独有"，改成 "we trace..."
6. 贡献重排（C1 = measurement space 不是 taxonomy invention）

### 需要讨论的关键问题：Hypothesis Locking 的诚实性

GPT 最关键的提醒：**"预测的盲区全部命中"需要 pre-construction hypothesis locking**。

我们的实际时间线：
- 8/14-16：主实验 582（检出率 85/93/73）
- 8/17：Arm1-6（原语/攻击面探索）—— **exploratory，不是 hypothesis-driven**
- 8/17-18：Arm7-9（隐藏文件/manifest）—— **Arm7 满足 hypothesis locking**（先分析 SS 源码 build_context.py 发现跳 dotfile → 预测隐藏文件是盲区 → 构造验证）
- 8/19-20：Arm10-13（执行阶段/组合）—— **部分满足**（基于 Arm7/11 发现预测）

**诚实处理方案（三选一）**：

**方案 A：两阶段叙事**
- Phase 1 (Exploratory)：Arm1-6 探索坐标空间，发现"原语决定可检测性"等模式
- Phase 2 (Confirmatory)：Arm7-13 沿坐标构造，验证 Phase 1 推导的 hypothesis
- 论文里明确标注哪些是 exploratory、哪些是 confirmatory

**方案 B：重组叙事（推荐）**
- Step 1 (Measure)：582 真实恶意 × 3 扫描器 → 坐标映射 → 发现覆盖轮廓
- Step 2 (Explain)：分歧定因（coverage gap vs operational divergence）
- Step 3 (Predict)：从覆盖轮廓推导盲区 hypothesis（"SS 不扫 dotfile → 隐藏文件应绕过"）
- Step 4 (Validate)：Arm7/10/11/13 构造验证
- Arm1-6 作为"方法验证"（证明坐标驱动构造可行），不作为"预测验证"

**方案 C：最诚实**
- 承认 iterative（发现→假设→验证循环）
- 强调 Arm7 的 hypothesis locking（源码分析 → 预测 → 构造）
- Arm10-13 标注为"基于 Phase 1 发现的 confirmatory construction"

### 我的倾向：方案 B
- 最干净：Measure → Explain → Predict → Validate 四步直接对应 GPT 的框架
- Arm1-6 变成"方法可行性验证"（坐标驱动构造能生成有效恶意样本）
- Arm7/10/11/13 变成"预测验证"（沿坐标构造，验证盲区 hypothesis）
- 不需要撒谎，只需要重组叙事顺序

---

## 三、待讨论

1. **Hypothesis locking 方案选 A/B/C？**
2. **GPT 的 claim 版本是否直接用作 Abstract 核心？**（我觉得可以，稍作压缩）
3. **标题确认**：GPT 没给标题，我之前推荐 "Predictable Blind Spots: ..."——是否用这个？
4. **8 页结构**：按 Measure → Explain → Predict → Validate 组织？
5. **Arm1-6 在论文里的角色**：方法验证 or 省略？（8 页空间有限）

---

## 四、下一步

Claim 定稿后，立即进入：
1. 标题 + Abstract（基于 GPT claim 版本）
2. 8 页结构大纲
3. 我起草英文 LaTeX
4. 你审阅改内容
