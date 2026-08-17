# Agent Skill 扫描评测最终总结（2026-08-17）

> 本文件整合 week-6/week-7 全部工作：581 恶意样本 × 3 家扫描 + 520 良性对照 + 分组根因分析
> ⚠️ **数据可信度声明**：DeepSeek API 余额于 2026-08-17 晚耗尽，LLM 分析的部分样本（SS 41 个 score=0 中 30 个确认失败）标注为"余额不足失败"，非判定结果。余额充足期间扫描的 540 SS + 416 Cisco 检出可信。

---

## 一、数据集总览

| 数据集 | 数量 | 来源 | 状态 |
|---|---|---|---|
| 真实恶意 wild | 350 | MalSkillBench 官方 703 WILD 分层抽样（B1-B15）| ✅ 已扫 |
| 构造恶意 gen | 231 | 我们 taxonomy 43 坐标生成（COORD_SEEDS）| ✅ 已扫 |
| 良性 benign | 520 | MalSkillBench benign（20 旧 + 500 新）| ✅ 已扫（500）|
| **恶意合计** | **581** | — | 三家扫描完成 |

## 二、检出率（余额耗尽前口径）

| 组 | Cisco (is_safe) | SS (score>0) | Caterpillar (findings>0) |
|---|---|---|---|
| wild 350 | 296 (84.6%) | 319 (91.1%) | 248 (70.9%) |
| gen 231 | 120 (51.9%) | 221 (95.7%) | 174 (75.3%) |
| **total 581** | 416 (71.6%) | **540 (92.9%)** | 422 (72.6%) |

**修正口径（含阈值放行）**：Cisco 真实检测 = is_safe False OR MEDIUM 危险 finding → **496 (85.4%)**
- gen: 51.9% → **82.3%**（70 个阈值放行，占 gen 30%）
- wild: 84.6% → 87.4%

## 三、标记分布与组合

| 被标记数 | total | 占比 |
|---|---|---|
| 3 家 | 354 | 60.9% |
| 2 家 | 179 | 30.8% |
| 1 家 | 38 | 6.5% |
| 0 家 | 10 | 1.7% |

| 组合 | 数量 | 含义 |
|---|---|---|
| 三家全检出 | 354 | 强信号恶意 |
| C+S（Cat 漏）| 118 | Cat 纯正则盲区 |
| S+P（Cisco 漏）| 45 | Cisco 语义盲区 |
| C+P（SS 漏）| 16 | SS 最少漏 |
| S only | 23 | SS 独强（指令型）|
| C only / P only | 8 / 7 | 极少 |

## 四、扫描器机制与根因（5 份 subagent 报告）

### Cisco（LLM + 静态规则）
- **强项**：供应链攻击 396、命令注入 208、混淆 157、数据外泄 141——重代码/供应链
- **漏检三机制**：
  1. **LLM 技术失败**（余额耗尽前 116 个，重扫后 17 个残留全为 clawhub 无 frontmatter）
  2. **阈值设计缺陷**：`models.py:226` is_safe=无 HIGH/CRITICAL → **80 个 MEDIUM 危险 finding 被吞**
  3. 真漏检：外部内容/运行时坐标（42-45% 检出率）
- **发现类别**：LLM_SUPPLY_CHAIN_ATTACK 396 / MANIFEST_MISSING_LICENSE 308 / LLM_COMMAND_INJECTION 208 / LLM_OBFUSCATION 157 / LLM_DATA_EXFILTRATION 141

### SkillSpector（多引擎：LLM 语义 + AST + 正则 + YARA）
- **强项**：全面领先（wild 91% / gen 96%）——指令型恶意最强
- **规则**：SQP-2 语义质量 / LP3 MCP 权限 / PE3 凭证 / AST4 危险代码
- **弱点**：flat 格式掩盖执行失败（score=0 无法区分"真安全"和"LLM 失败"）；run-to-run 不稳定（agent-browser 100→0）
- **⚠️ 余额问题**：41 个 score=0 中 30 个确认 LLM 失败（非判定）

### Caterpillar（纯正则离线）
- **强项**：Obfuscation 291 / Supply Chain 213 / Data Exfil 134——代码型字面证据
- **盲区**：118 个 C+S 组合全漏（指令型文本/外语/无正则特征）；无 Python API 规则；关键词窄化规避（npm i≠install）
- **误报**：ncat 匹配 trunc*ncat*ed、Ledger 匹配钱包教学（缺词边界）
- **方法学警告**：12% 的 gen 检出由 _provenance.json 泄漏驱动（评测输入未剔除 ground-truth）

## 五、三家全漏 10 个的真实归因（复核后）

| 归因 | 数量 | 样本 |
|---|---|---|
| 数据污染（21MB 垃圾）| 1 | klaviyoapi |
| 数据质量（脚本剥离/重复/误分类/生成失败）| 5 | better-polymarket、polymarket-all-in-one、get-weather、rankaj、skill-privilege |
| 扫描执行失败（Cisco 空壳 + SS LLM 失败）| 2+ | novafon、rbtc、kh3rwa1（SS 确认余额失败）|
| 阈值放行 | 2 | dex-arbitrage、project-init |

**结论**：**无"三家真判安全且确认真恶意"的样本**。全漏可归因于：数据质量问题 + 扫描器技术失败（含余额不足）+ 阈值放行。唯一接近"真三家盲区"的是 kh3rwa1（纯指令型），但重跑证明 SS 是 LLM 失败非判定。

## 六、对论文的核心贡献（S4 scanner re-eval 章节）

1. **检出率排序**：SS 92.9% > Cisco 85.4%（修正后）> Cat 72.6%
2. **评测方法 4 大陷阱**：
   - 技术失败 ≠ 漏检（需重跑验证 + 标注）
   - 阈值设计吞检出（Cisco is_safe 只认 HIGH/CRITICAL，80 个 MEDIUM 被吞）
   - ground-truth 泄漏污染检出率（Cat 12% 泄漏驱动）
   - 输出格式掩盖失败（SS flat 无 execution_successful）
3. **扫描器定位**：Cisco=供应链检测器（偏科）、SS=全能语义（最平衡）、Cat=代码字面正则（上限明确）
4. **构造样本价值**：gen 暴露扫描器盲区更充分（单家标 19% vs wild 7%）——坐标级覆盖了真实样本缺的组合
5. **数据质量问题**：MalSkillBench wild 含 21MB 垃圾样本、md5 重复、误分类——评测需清洗

## 七、文档索引

| 文档 | 内容 |
|---|---|
| week-7/WEEK7_TASKS.md | 本周任务书 + 进度 |
| week-7/DATA_ANALYSIS_2026-08-17.md | 初步数据分析 |
| week-7/DATA_ANALYSIS_GROUPED_2026-08-17.md | wild/gen 分组统计 |
| week-7/OVERALL_STATS_2026-08-17.md | 修正后整体统计 |
| week-7/SCANNER_MISS_ANALYSIS_SUMMARY.md | 5 组根因汇总 |
| week-7/ANALYSIS_NONE_DETECTED.md | 全漏 11 根因（v2 修正）|
| week-7/ANALYSIS_SINGLE_SS.md | 仅 SS 检出 48 分析 |
| week-7/ANALYSIS_SINGLE_CISCO_CAT.md | 仅 C 7 + 仅 Cat 14 分析 |
| week-7/ANALYSIS_DOUBLE_SC.md | S+P 97（Cisco 漏）分析 |
| week-7/ANALYSIS_DOUBLE_CS_CC.md | C+S 93 + C+Cat 10 分析 |
| week-7/RESCAN_NOTES.md | 重扫 + 阈值问题记录 |
| scanners/eval_results/verdict_all.csv | 581 全量判定表 |

## 八、后续待办（余额恢复后）

1. 重跑 SS 41 个 score=0 样本（确认是否检出）
2. 重跑 Cisco 17 个 null（clawhub 无 frontmatter——需补 frontmatter 或标注）
3. 清洗数据集：剔除 klaviyoapi（21MB 垃圾）+ md5 去重（581→577）
4. 修正 Cat 评测输入（剔除 _provenance.json）
5. TP/FP 矩阵（良性 500 已扫，需校验 FP 数据可信度）
