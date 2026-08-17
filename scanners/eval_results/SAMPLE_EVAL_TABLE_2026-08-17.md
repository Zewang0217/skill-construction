# 581 恶意样本全量评测表（2026-08-17）

> 数据：`scanners/eval_results/verdict_all.csv`（581 行 = 350 wild + 231 generated × 3 家）
> 判定口径：Cisco = is_safe==False；SS = score>0；Caterpillar = n_findings>0
> SS 缺失 56 个（补扫中，见下）；Cisco na 17 个（clawhub 无 frontmatter 拒绝加载）

---

## 1. 检出率总览

| 组 | 样本数 | Cisco | SkillSpector | Caterpillar | 三家全漏 |
|---|---|---|---|---|---|
| **wild 真实** | 350 | 292 (83.4%) | 291 (83.1%) | 214 (61.1%) | — |
| **generated 构造** | 231 | 119 (51.5%) | 199 (86.1%) | 168 (72.7%) | — |
| **合计** | 581 | 411 (70.7%) | 490 (84.3%) | 382 (65.7%) | — |

> ⚠️ generated 的 Cisco 51.5% 偏低，但**不是样本质量问题**——103 个 Cisco-safe 样本中仅 7 个是真良性（质量门漏洞），
> 其余 96 个被 SS/Cat 检出（SS 63-100 分），是 **Cisco 对构造样本的隐藏型恶意盲区**（构造样本用 mdb 证据生成，
> 比 MalSkillBench 直白恶意更接近真实伪装）。

## 2. generated 按 source 检出（Cisco）

| source | 样本 | Cisco 检出 | 检出率 |
|---|---|---|---|
| supply_chain | 80 | 49 | 61% |
| unknown_source | 5 | 3 | 60% |
| user_input | 9 | 6 | 67% |
| source_agnostic | 115 | 52 | 45% |
| external_content | 19 | 8 | 42% |
| runtime_environment | 3 | 1 | 33% |

**规律**：外部内容/来源无关/运行时（非供应链）坐标的构造样本 Cisco 检出率最低——与 taxonomy 盲区分析一致
（Cisco 强项在供应链入口，盲区在外部内容/运行时）。

## 3. 质量门漏洞样本（真良性，7 个）

> 这些是 LLM 生成失败（无恶意行为）的样本，Cisco+SS+Cat 一致判安全属正常。
> 清单+复核：`week-7/no_malice_samples.json`（10 个，其中 8 真良性 2 真恶意漏检）

| 样本 | 坐标 |
|---|---|
| skill-code_exec-persistent_control-777fdcbcdd | source_agnostic×code_exec×persistent_control |
| skill-instruction_manip-content_safety-97d98fa078 | source_agnostic×instruction_manip×content_safety |
| skill-instruction_manip-defense_evasion-ebbe33d7f1 | user_input×instruction_manip×defense_evasion |
| skill-instruction_manip-target_agnostic-490d578b2b | external_content×instruction_manip×target_agnostic |
| skill-privilege_abuse-financial_theft-998f919d39 | source_agnostic×privilege_abuse×financial_theft |
| skill-privilege_abuse-target_agnostic-3a6f2db506 | supply_chain×privilege_abuse×target_agnostic |
| skill-state_corruption-target_agnostic-f22b611df0 | source_agnostic×state_corruption×target_agnostic |

（另有 state_corruption-persistent_control-97d85713dd 也判真良性——合计 8 个，1 个未在 110 safe 列表）

## 4. SS 补扫状态

- 缺失 56 个（wild 31 + gen 25）→ `backfill_ss.py` 补扫中（~2 小时）
- 补完后重建 verdict_all.csv 即完整

## 5. 论文意义

- **wild 检出率（83%）vs generated（Cisco 51.5% / SS 86%）**：构造样本暴露的盲区更接近真实威胁分布
- **Cisco 对非供应链坐标 42-45% 检出**：量化了"供应链强、外部内容弱"的不对称
- **三家全漏（如果有）**：待 SS 补完后统计
