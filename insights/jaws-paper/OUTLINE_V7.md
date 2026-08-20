# JAWS v7 设计 — Paper Architecture Surgery（2026-08-20）

> 依据：GPT_FEEDBACK_V6.md + 七-agent 全周盘点 + data_explorer.html 资产核查。
> Thesis（GPT §二，直接采用）：
> **We turn disagreement among automated analyses from a scalar evaluation outcome into a structured object that generates falsifiable blind-spot hypotheses.**

---

## 1. 理论骨架：三层分解（替代 coverage gap / operational divergence）

| 层 | 问题 | 实例锚点 | 证据 |
|---|---|---|---|
| **L1 Coverage** | scanner 的输入收集包含该行为所在的位置吗？ | SS `build_context.py` 跳 dotfile → `.env` 从未进分析 | Arm7: 14/15 evade, 11 score=0, raw 记录 analyzed=['SKILL.md'] |
| **L2 Detection** | 检测机制（regex/YARA/AST/LLM）能识别该行为吗？ | Cat 纯正则，无字面标记即盲 | Arm10B: 0/10；Cat 单家独漏 118 |
| **L3 Decision** | finding 被判定规则转成 block 了吗？ | Cisco `models.py:226` 只认 HIGH/CRITICAL，MEDIUM 被吞 | Arm7: YARA 命中但 4/15 detect；主实验 88 skill `is_safe`+MEDIUM+；benign-4000 的 662 MEDIUM 不可见（同一刀的良性侧） |

- 旧 taxonomy 术语映射：coverage gap ≈ L1；operational divergence ≈ L2+L3 混合 → 拆开。
- Arm11A（Cisco 0/6）读作 L2→L3 链：构造让静态层无可升级的 finding。
- 每个确认的 miss 归到恰好一层 → 这就是"disagreement 有结构"的操作化表述。

## 2. 章节结构（7 节，正文 ~7p）

| § | 内容 | 页 | 图表 |
|---|---|---|---|
| 1 | Introduction：running example（`.env` payload，三家三个结果）→ disagreement as evidence → thesis → 贡献链 | 0.9 | **Fig 1** |
| 2 | The Core Idea：statistic view vs structural view；三层分解定义；为什么非此方法不可 | 0.8 | **T2 why-necessary** |
| 3 | Shared Observation Language（压缩）：56.5% partial triples 一个数字 + 43 coordinates + 仪器定位；NMI 等一句话 | 0.6 | T1 dims（可并入正文） |
| 4 | Method — The Loop：observe → localize → decompose(L1/L2/L3) → hypothesize → lock → construct → validate；sanitization + locking protocol | 0.7 | — |
| 5 | Instantiation：四个语料各司其职 | 0.8 | **Fig 2 wild census** + **T3 datasets** |
| 6 | Does It Work? Prediction Ledger：H1–H6 逐条 ✓/partial/✗ + 机制；Arm12 rejection；Arm11B partial | 1.8 | **Fig 3** **Fig 4** **Fig 5** + **T4 ledger** |
| 7 | Discussion + Related Work | 0.9 | — |

## 3. 图（5 张，语义色：Gray=existing/input，Blue=analysis，Orange=predicted，Red=observed failure，Green=validated）

- **Fig 1 (§1, 全宽, TikZ 重画)** — *Figure question: disagreement 如何从 outcome 变成 hypothesis 生成过程？*
  左 CURRENT PRACTICE（artifact → 3 scanners → κ=0.1 → STOP）vs 右 OUR VIEW（artifact → observation space (s,m,t) → 三层分解 L1/L2/L3 → per-scanner hypothesis → locked validation）。无具体攻击细节，左右密度平衡。
- **Fig 2 (§5, 单栏, matplotlib, 新增)** — *Q: 真实生态里分歧是常态吗？*
  data_explorer 数据：(a) 6-scanner κ 矩阵热图（全部 ≤0.24，多数 ≈0）；(b) 共识分布（verified 136：仅 4.4%+1.5% 达 4-5 家共识）。标注：市场普查、无 ground truth、scanner 集合与主实验不同（census 角色）。
  数据源：`skills-scanner-study/data/views/stats/cohen_kappa_verified.csv` + `consensus_distribution_verified.csv`。
- **Fig 3 (§5/§6, 全宽, matplotlib 重排)** — *Q: aggregate 指标掩盖了什么结构？*
  (a) κ 不稳定性 dot-range（3 pairs × 3 corpus/rule，重做 v6 柱状为 dot-range）；(b) UpSet（8 组合，重做条形）；(c) heatmap（保留）。
- **Fig 4 (§6, 单栏, matplotlib 微调)** — *Q: 锁定的假设预测了失败吗？*
  v6 forest + outcome 语义色（Green=confirmed, Orange=partial, Red=rejected/Arm12 开放点黑色保留）。
- **Fig 5 (§6, 单栏, TikZ 重画)** — *Q: 同一个 miss 能起源于不同层吗？*
  Three-layer failure anatomy：顶部 SAME ARTIFACT（SKILL.md benign + .env payload）→ 三列 SkillSpector/L1 FILE COLLECTION ✗ 14/15、Caterpillar/L2 DETECTION ✗ 13/15、Cisco/L3 DECISION ✗ 11/15 → 底部一行层标签。替代 v6 fig:oneload。

## 4. 表

- **T1 scanners**（保留）。
- **T2 why-necessary（§2 新增）**：Recall/κ（localize✗ explain✗ predict✗）| Manual post-hoc（✓✓✗）| Ours（✓✓✓ pre-locked）。
- **T3 datasets（§5 新增）**：四个语料 × 单位/规模/scanner 集/角色——1082 wild census（motivation）/ 581 malicious（observed disagreement）/ 500+4000 benign（FP 参照）/ 129→79 confirmatory（validation）。这张表就是"研究单位分离"的落地。
- **T4 prediction ledger（tab:cases 升级）**：列 = H# / 证据类型(A/B) / locked prediction / construction (Arm, n) / outcome (✓/partial/✗ + 比率 + Wilson CI) / mechanism 层 (L1/L2/L3)。行：H1 dotfile→SS L1 ✓14/15；H2 no-literal→Cat L2 ✓10/10；H3 finding-specialized→Cisco L2→L3 ✓6/6；H4 combination→SS L3 ✓5/5 (2/5 全漏注记)；H5 wild pipeline→SS partial 3/5；H6 variant-family→SS ✗ 9/10 detected（rejected，诚实行）。脚注：lock 日期链（matrix 08-13 / source reading before construction / constructions 08-19+）。

## 5. 删除 / 降级

- NMI/2.6×/45% → 一句话（"the axes carry complementary information; removing any axis collapses the 31 occupied coordinates to 15–23"）。
- tab:disagg (a) 检出率面板 → 并入 T3/Fig 3（heatmap 已承载）；保留 (b)(c) 组合分布。
- grey zone 段 → 压至 3 句（保留 335/3996、16.2%、662 三个数 + 三机制列举）。
- 401-cell feasibility 细节 → §4 一句（43 occupied / 318 credible blanks / 39 infeasible）。
- `Paper identity` 段（与 thesis 重复）删除。

## 6. 保留不动（v6 已正确）

- 全部 581/38/86.7 等口径修正数字；Arm 机制叙事（finding-specialized）；Arm13 2/5 triple-miss 披露；"ran outside the locking protocol"；benign-4000 三层证据；scripts/ 可复现管线。

## 7. 执行顺序（deadline 08-22 20:00）

1. 重写 main.tex：§1-§7 新结构 + 三层分解术语贯穿（本轮）
2. Fig 1/5 TikZ 重画 + Fig 2 新建 + Fig 3/4 重排（matplotlib 脚本入库）
3. T2/T3/T4 新表
4. 编译 + 数字自查（stats_581.json + census CSV）+ pre-submission 检查
5. 镜像 commit
