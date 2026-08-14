# Scanner 适配 + H1 盲区 pilot 初测小结（2026-08-13）

> ⚠️ **本文是最早的 2-scanner 适配验证（2026-08-13 上午）。**
> 后续已扩展为 **3 家（+Caterpillar）+ 横评 + 修复脚本 bug**，详见：
> - `WORKLOG_2026-08-13.md`（完整工作+发现+修复）
> - `eval_results/ANALYSIS.md`（修复后横评结果）
> - `SELECTION.md`（最终选型）
> 本文的适配方法仍有效，但扫描结果/工具清单已过时，以更新文档为准。

## 目标
把两个开源 scanner 适配到 deepseek，扫生成器产出的恶意 skill 样本，验证 pilot H1
（盲区坐标样本检出率）能否实测。

## Scanner 选择（3 个 scout 调研结论）
| Scanner | DeepSeek 适配 | 判定 |
|---|---|---|
| **cisco-ai-defense/skill-scanner** v2.0.13 | ✅ 源码原生（`['deepseek','minimax']` 白名单自动降级 json_object）| **用** |
| **NVIDIA/SkillSpector** v2.9.3 | ⚠️ 主 CLI 卡点（json_schema vs json_object），官方 `contrib/batch_scan` 兼容层解决 | **用** |
| **snyk/agent-scan** | ❌ 瘦客户端，分析在 Snyk 托管闭源后端，样本会上传 + 无法接 deepseek | **排除**（数据出境）|

两者恰是我们 taxonomy 的两大来源 scanner（SS + Cisco），适配 deepseek 后能实测生成样本检出率。

## 适配方式
- **Cisco**：4 个 env 指向 deepseek（openai-compatible）：
  `SKILL_SCANNER_LLM_API_KEY / _PROVIDER=openai-compatible / _MODEL=deepseek-chat / _BASE_URL=https://api.deepseek.com/v1`
  + `--use-llm --format json --enable-meta`
- **SkillSpector**：主 CLI 语义分析对 deepseek 400 失败（json_schema 不支持）；用官方
  `contrib/batch_scan`（7 个 monkey-patch 关 structured output + 手动 JSON 解析），
  env `SKILLSPECTOR_API_KEYS="key|https://api.deepseek.com|deepseek-chat"` + `PROVIDER=openai`。

## 扫描结果（3 个规范恶意样本）
| 样本 | 坐标 (src/mech/tgt) | 载体 | Cisco (is_safe/sev/findings) | SkillSpector (score/sev/issues) |
|---|---|---|---|---|
| env-mgr | runtime_environment/code_exec/info_theft | CI | False / CRITICAL / 8 | 100 / CRITICAL / 24 |
| git-commit-helper | supply_chain/dependency_manip/info_theft | MIXED | False / CRITICAL / 6 | 100 / CRITICAL / 11 |
| markdown-toc | external_content/instruction_manip/defense_evasion | PI | False / CRITICAL / 7 | 100 / CRITICAL / 16 |

## 关键观察
1. **生成器产出质量达标**：3 个恶意样本全被两家 scanner 识别为 CRITICAL —— 恶意行为真实、可执行、贴近真实攻击模式。
2. **H1 pilot 真正含义浮现**：这三个坐标**不是盲区**（两家都爆 CRITICAL），因为它们含
   `code_exec`/`instruction_manip` 等**已被 scanner 静态+LLM 全覆盖的机制**。真正盲区是
   `runtime_environment` 来源 **结合** 未被覆盖的机制组合——需要更多样本来 hit 盲区。
3. **工具链已打通**：生成器 → Cisco(deepseek) + SkillSpector(deepseek) → verdict.csv 全自动，
   可扩展批量测 40 样本。

## 工具位置
- 生成器：`../generator/`（generate.py / patterns.py / llm.py）
- 扫描器：`./scan_all.py` + `.env.deepseek` + `skillspector_batch/`（官方 batch_scan 副本）
- 结果：`./results/`（verdict.csv + 每样本 cisco_raw.json + skillspector_batch.json）

## 下一步（待用户）
1. **扩展盲区坐标采样**：这三个坐标太"容易"被检出，需精细采样真盲区（如
   `source_agnostic × 低频 mechanism(subagent_escalation/defense_evasion) × target_agnostic`）。
2. **批量化**：用修好的生成器批量生成 40 样本（含盲区/覆盖 split），全自动扫描出 verdict。
3. **良性与误报集**：需生成良性对照样本，Else scanner 精度无法评估。
