# Agent Skill 安全扫描评测 — 最终报告

> 版本：2026-08-17 终版 | 数据：582 恶意 + 519 良性 × 3 家扫描器
> 仓库：github.com/Zewang0217/skill-construction（main 分支）

---

## 一、数据集

| 数据集 | 数量 | 来源 |
|---|---|---|
| 真实恶意 wild | 350 | MalSkillBench 官方 WILD（B1-B15 分层抽样）|
| 构造恶意 gen | 232 | 本工作 taxonomy 43 坐标生成 |
| 良性 benign | 519 | MalSkillBench benign 对照 |
| **恶意合计** | **582** | 三家扫描完成 |

**taxonomy**：43 唯一坐标（source×mechanism×target），行为模板 211 条（mapping-db 证据 + ATTACK_SEEDS + 手写）。

---

## 二、检出率

| 组 | 样本 | Cisco | SkillSpector | Caterpillar |
|---|---|---|---|---|
| wild | 350 | **87.4%** | 91.1% | 70.9% |
| gen | 232 | **82.3%** | 95.3% | 75.0% |
| **total** | **582** | **85.2%** | **92.8%** | **72.5%** |

- **Cisco 口径**：真实检测（is_safe==False 或 MEDIUM 及以上危险 finding）
- **SS 口径**：score > 0；**Cat 口径**：n_findings > 0
- 数据完整度：Cisco 564/582、SS 541/582、Cat 582/582（其余为 LLM 服务失败，见 §五）

---

## 三、标记分布（582 恶意）

| 被标记数 | 数量 | 占比 |
|---|---|---|
| 3 家全检出 | 354 | 60.8% |
| 2 家 | 179 | 30.8% |
| 1 家 | 39 | 6.7% |
| 0 家 | 10 | 1.7% |

**组合分布**：

| 组合 | 数量 | 含义 |
|---|---|---|
| 三家全检出 | 354 | 强信号恶意 |
| C+S（Cat 漏）| 118 | Cat 纯正则盲区 |
| S+P（Cisco 漏）| 45 | Cisco 语义盲区 |
| C+P（SS 漏）| 16 | SS 最少漏 |
| 仅 SS | 23 | SS 独强（指令型）|
| 仅 Cisco / 仅 Cat | 8 / 7 | 极少 |

---

## 四、三家全漏 10 个归因

| 归因 | 数量 | 样本 |
|---|---|---|
| 数据污染（21MB 垃圾文件）| 1 | klaviyoapi |
| 数据质量（脚本剥离/重复/误分类/生成失败）| 5 | better-polymarket、polymarket-all-in-one、get-weather、rankaj、skill-privilege |
| 扫描执行失败 | 2 | novafon、rbtc |
| 阈值放行 | 2 | dex-arbitrage、project-init |

**结论**：无"三家均判安全且确认真恶意"的样本。全部 10 个全漏可归因于数据质量、扫描器执行失败、或阈值设计。

---

## 五、扫描器机制与局限

### Cisco（LLM + 静态规则）— 真实检测 85.2%
- 检出类别：供应链攻击 396、命令注入 208、混淆 157、数据外泄 141、提示注入 74
- **局限**：① `is_safe` 阈值只认 HIGH/CRITICAL，80 个 MEDIUM 危险检出被吞（数据已按真实检测口径修正）；② 无 YAML frontmatter 的样本拒绝加载（17 个）；③ 外部内容/运行时来源坐标检出率低（42-45%）
- **定位**：供应链检测器（偏科）

### SkillSpector（LLM 语义 + AST + 正则 + YARA）— 检出 92.8%
- 检出规则：SQP-2 语义质量、LP3 MCP 权限、PE3 凭证访问、AST4 危险代码
- **局限**：① flat 输出格式不携带执行状态（score=0 无法区分"安全"与"LLM 失败"）；② 跨次扫描不稳定（同样本 score 100→0）；③ 41 个样本 LLM 服务失败无有效判定
- **定位**：全能语义分析，最平衡

### Caterpillar（纯正则离线）— 检出 72.5%
- 检出类别：Obfuscation 291、Supply Chain 213、Data Exfil 134、Persistence 37
- **局限**：① 指令型恶意全盲（118 个 C+S 组合零命中）；② 无 Python/JS API 规则（requests/subprocess 不可见）；③ 关键词窄化规避（npm i≠npm install）；④ 误报（ncat 缺词边界匹配）
- **定位**：代码字面证据检测，能力上限明确

---

## 六、核心发现（论文 S4 素材）

1. **检出率排序**：SS 92.8% > Cisco 85.2% > Cat 72.5%
2. **60.8% 恶意样本三家全检出**；单家独有检出 38 个（6.5%）
3. **评测方法 4 陷阱**：
   - 扫描器技术失败不能计入"漏检"（需重跑验证 + 标注）
   - 判定阈值会吞检出（Cisco is_safe 只认 HIGH/CRITICAL）
   - ground-truth 泄漏污染检出率（Caterpillar 直接扫原目录）
   - 输出格式掩盖执行失败（flat 无执行状态字段）
4. **扫描器定位**：Cisco=供应链偏科、SS=全能语义、Cat=代码字面正则
5. **构造样本价值**：坐标级覆盖暴露扫描器盲区（gen 单家标 19% vs wild 7%）
6. **数据集需清洗**：MalSkillBench wild 含 21MB 垃圾样本、md5 重复（582→577 唯一）

---

## 七、良性 FP 基线（519 良性）

| 指标 | 值 |
|---|---|
| 良性样本 | 519（19 旧 + 500 新）|
| 扫描状态 | 已扫（verdict_all.csv）|
| FP 完整矩阵 | 见 verdict_all.csv 良性侧 |

---

## 八、附录：数据可信度与成本

### 可信度
- LLM 分析依赖 DeepSeek API（v4-flash）。**41 个 SS 样本因 LLM 服务失败无有效 score**（§二 数据完整度已标注），其余数据有效。
- 所有报告基于最终判定表 `verdict_all.csv`（582 恶意 + 519 良性）。

### 成本
- LLM 调用约 7,600 次，消耗约 ¥60-90（deepseek-v4-flash 定价）。

---

## 九、文档索引

| 文档 | 内容 |
|---|---|
| **本文件** | 最终报告（数据总览）|
| week-7/OVERALL_STATS_2026-08-17.md | 分组检出统计 |
| week-7/SCANNER_MISS_ANALYSIS_SUMMARY.md | 漏检根因汇总 |
| week-7/ANALYSIS_NONE_DETECTED.md | 全漏样本归因 |
| week-7/ANALYSIS_SINGLE_SS.md | 仅 SS 检出分析 |
| week-7/ANALYSIS_SINGLE_CISCO_CAT.md | 仅 Cisco/Cat 检出分析 |
| week-7/ANALYSIS_DOUBLE_SC.md | S+P 组（Cisco 漏）分析 |
| week-7/ANALYSIS_DOUBLE_CS_CC.md | C+S / C+Cat 组分析 |
| scanners/eval_results/verdict_all.csv | 全量判定表（1101 行）|
| scanners/eval_results/raw/ | 1761+ 份原始扫描报告 |
