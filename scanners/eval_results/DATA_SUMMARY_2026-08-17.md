# Agent Skill 安全扫描评测 — 数据总结（2026-08-17 终版）

> 本文是全部实验数据的权威总结，替代/整合此前多份报告。详细分析见各 ANALYSIS_*.md。
> 项目：Agent Skill 安全 SoK 论文 S4（scanner re-eval）+ S5（原型）
> 仓库：github.com/Zewang0217/skill-construction（main 分支）

---

## 一、数据集

| 数据集 | 数量 | 来源 | 性质 |
|---|---|---|---|
| 真实恶意 wild | 350 | MalSkillBench 官方 703 WILD 分层抽样（B1-B15 标签）| 真实恶意（沙箱验证）|
| 构造恶意 gen | 232 | 本工作 taxonomy 43 坐标生成（COORD_SEEDS）| 模拟恶意（坐标语义内）|
| 良性 benign | 519 | MalSkillBench benign（19 旧 + 500 新）| 良性对照 |
| **恶意合计** | **582** | — | 三家扫描完成 |

**taxonomy 坐标**：43 唯一坐标（source×mechanism×target），来源无关 23 / 供应链 15 / 外部内容 3 / 用户输入 1 / 来源不明 1。
每坐标 2-9 个构造样本，行为来自 mapping-db 证据 + ATTACK_SEEDS + 手写（211 条）。

---

## 二、检出率（三家，582 恶意）

| 组 | Cisco (is_safe) | SS (score>0) | Caterpillar (findings>0) |
|---|---|---|---|
| wild 350 | 296 (84.6%) | 319 (91.1%) | 248 (70.9%) |
| gen 232 | 120 (51.7%) | 221 (95.3%) | 174 (75.0%) |
| **total 582** | **416 (71.5%)** | **540 (92.8%)** | **422 (72.5%)** |

**Cisco 修正口径**（含阈值放行 MEDIUM 危险 finding）：真实检测 **496 (85.2%)**
- gen: 51.7% → **82.3%**（70 个阈值放行）
- wild: 84.6% → 87.4%

> ⚠️ 数据可信度：DeepSeek 余额 8-17 晚耗尽。SS 41 个 score=0 中 **30 个确认是 LLM 调用失败**（非判定）。余额充足期间扫的 540 SS + 416 Cisco 检出可信。

---

## 三、标记分布（582 恶意）

| 被标记数 | 数量 | 占比 |
|---|---|---|
| 3 家全检出 | 354 | 60.8% |
| 2 家 | 179 | 30.8% |
| 1 家 | 39 | 6.7% |
| 0 家 | 10 | 1.7% |

**组合**（修正后 Cisco 口径）：all3=354 / C+S=118 / S+P=45 / C+P=16 / S_only=23 / C_only=8 / P_only=7 / none=10

---

## 四、三家全漏 10 个归因（复核后）

| 归因 | 数量 | 样本 |
|---|---|---|
| 数据污染（21MB 垃圾）| 1 | klaviyoapi |
| 数据质量（脚本剥离/重复/误分类/生成失败）| 5 | better-polymarket、polymarket-all-in-one、get-weather、rankaj、skill-privilege |
| 扫描执行失败（Cisco 空壳 + SS LLM 失败）| 2+ | novafon、rbtc、kh3rwa1 |
| 阈值放行 | 2 | dex-arbitrage、project-init |

**结论：无"三家真判安全且确认真恶意"样本**——全漏可归因于数据质量 + 扫描器技术失败 + 阈值放行。

---

## 五、扫描器机制对比

### Cisco（LLM + 静态规则）
- **检出**：416 (71.5%) → 修正 496 (85.2%)
- **强项**：供应链攻击 396、命令注入 208、混淆 157、数据外泄 141
- **漏检机制**：① LLM 技术失败（重扫后剩 17 clawhub 无 frontmatter）② 阈值吞 MEDIUM（80 个）③ 外部内容/运行时坐标弱
- **定位**：供应链检测器，偏科

### SkillSpector（多引擎：LLM 语义 + AST + 正则 + YARA）
- **检出**：540 (92.8%)——**三家最强**
- **强项**：指令型恶意、伪装型、外语样本（语义层兜底）
- **弱点**：flat 格式掩盖执行失败；run-to-run 不稳定（agent-browser 100→0）
- **⚠️ 余额影响**：41 个 score=0 中 30 个确认 LLM 失败

### Caterpillar（纯正则离线）
- **检出**：422 (72.5%)
- **强项**：Obfuscation 291、Supply Chain 213、Data Exfil 134（代码字面证据）
- **盲区**：118 个 C+S 组合全漏（指令型无正则特征）；无 Python API 规则；关键词窄化规避
- **误报**：ncat 匹配 trunc*ncat*ed、Ledger 匹配钱包教学（缺词边界）
- **方法学警告**：12% gen 检出由 _provenance.json 泄漏驱动

---

## 六、论文核心发现（S4 章节素材）

1. **检出率排序**：SS 92.8% > Cisco 85.2%（修正）> Cat 72.5%
2. **评测 4 大陷阱**：
   - 技术失败 ≠ 漏检（重扫验证 + 标注）
   - 阈值吞检出（Cisco is_safe 只认 HIGH/CRITICAL → 80 个 MEDIUM 被吞）
   - ground-truth 泄漏（Cat 12% 检出是 provenance 泄漏）
   - 输出格式掩盖失败（SS flat 无 execution_successful）
3. **扫描器定位**：Cisco=供应链偏科、SS=全能语义、Cat=代码字面正则上限明确
4. **构造样本价值**：gen 暴露盲区更充分（单家标 19% vs wild 7%）
5. **数据质量问题**：wild 含 21MB 垃圾样本、md5 重复、误分类

---

## 七、良性 FP 基线（519 良性，部分待完成）

| 组 | 状态 |
|---|---|
| benign-samples 19（旧）| ✅ 已扫（Cisco FP 15.8% 剔除 moltpho 后）|
| benign-500 | ✅ 已扫（余额耗尽前，数据可信待核验）|
| FP 完整矩阵 | 🔄 待整合（benign-500 判定在 verdict_all.csv）|

---

## 八、待办（余额恢复后）

1. 重跑 SS 41 个 score=0（确认检出）
2. 重跑 Cisco 17 个 null（clawhub 无 frontmatter——补 frontmatter 或标注）
3. 数据集清洗：剔除 klaviyoapi（21MB）+ md5 去重（582→577）
4. Cat 评测输入剔除 _provenance.json
5. 整合 benign-500 FP 矩阵 → TP/FP 完整表
6. 论文 S4 章节撰写

---

## 九、成本（8-16/17 扫描）

- LLM 调用 ~7600 次（SS 5/样本 × 1178 + Cisco 1274 + 生成 460）
- 消耗 ≈ **¥60-90（$8-12）**（deepseek-v4-flash 官方价，含缓存命中）
- 账户现欠 -5.49 CNY

---

## 十、文档索引

| 文档 | 内容 |
|---|---|
| **本文件** | 数据总结（终版）|
| week-7/OVERALL_STATS_2026-08-17.md | 修正后整体统计 |
| week-7/SCANNER_MISS_ANALYSIS_SUMMARY.md | 5 组根因汇总 |
| week-7/ANALYSIS_*.md（5 份）| 分组深挖（全漏/单家/两家）|
| week-7/DATA_ANALYSIS*.md（2 份）| 初步 + 分组统计 |
| week-7/RESCAN_NOTES.md | 重扫 + 阈值记录 |
| week-7/WEEK7_TASKS.md | 任务书 + 进度 |
| scanners/eval_results/verdict_all.csv | 582 恶意 + 500 良性判定表 |
| scanners/eval_results/raw/ | 1761+ 份扫描报告 |
