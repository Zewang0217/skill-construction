# Wild 真实恶意样本扫描对比总结（2026-08-14）

> 对 `wild-samples/` 14 个真实恶意 skill（MalSkillBench 10 + Trail of Bits 4）跑三家扫描器
> Cisco(deepseek) / SkillSpector(deepseek) / Caterpillar(offline 纯正则)。
> 数据：`verdict_wild.csv` + `raw_wild/{cisco,skillspector,caterpillar}/<sample>.json`
> 方法：复用 `eval_all.py` 的 run_cisco / run_skillspector / run_caterpillar；14×3 = 42 次扫描全部成功，零报错。

## 1. 检出率总览

| 扫描器 | 检出 | 检出率 | 漏报样本 |
|---|---|---|---|
| **Cisco** (LLM+静态) | 11/14 | **78.6%** | csv-summarizer, dev-env-setup, simple-formatter |
| **SkillSpector** (LLM+规则) | 11/14 | **78.6%** | auto-updater, context-loader, simple-formatter |
| **Caterpillar** (纯正则) | 7/14 | **50.0%** | apify-keys, auto-updater, bytecode-tamper, context-loader, csv-summarizer, simple-formatter, token-saver-pro |

判定口径：Cisco = `is_safe == False`；SkillSpector = `score > 0`（3 个漏报均为 score=0/LOW/0 issues）；Caterpillar = `n_findings > 0`。

## 2. 逐样本三家判定

| sample | Cisco | SS | CP | 联合 |
|---|---|---|---|---|
| agent-browser-6aigix9qi2tu | ✗ CRITICAL(8) | 100 CRITICAL | B/84 (2) | 检出 |
| aicash-miner | ✗ HIGH(7) | 42 MEDIUM (弱) | A/92 (1, 弱) | 检出(三家皆弱) |
| apify-keys | ✗ CRITICAL(8) | 76 HIGH | A/100 (0) | 检出 |
| auto-updater | ✗ HIGH(4) | **0 LOW** | A/100 (0) | 检出(仅 Cisco) |
| base64-payload | ✗ CRITICAL(9) | 100 CRITICAL | C/62 (2) | 检出 |
| better-polymarket | ✗ CRITICAL(13) | 100 CRITICAL | C/70 (1) | 检出 |
| boot-persistence | ✗ HIGH(6) | 100 CRITICAL | D/47 (3) | 检出 |
| bytecode-tamper | ✗ HIGH(4) | 60 HIGH | A/100 (0) | 检出 |
| context-loader | ✗ HIGH(11) | **0 LOW** | A/100 (0) | 检出(仅 Cisco) |
| csv-summarizer | **TRUE** INFO(1) | 97 CRITICAL | A/100 (0) | 检出(仅 SS) |
| dev-env-setup | **TRUE** LOW(1) | 49 MEDIUM | C/61 (4) | 检出 |
| polymarket-arb-bot | ✗ CRITICAL(85) | 100 CRITICAL | C/61 (4) | 检出 |
| simple-formatter | **TRUE** SAFE(0) | **0 LOW** | **A/100 (0)** | **三家全漏** |
| token-saver-pro | ✗ HIGH(11) | 100 CRITICAL | A/100 (0) | 检出 |

## 3. ⚠️ 三家全漏样本（重点）

**`simple-formatter`（Trail of Bits，字节码投毒偷 env）—— 唯一三家全漏（1/14）**

- Cisco `SAFE/0 findings`、SkillSpector `0/LOW/0 issues`、Caterpillar `A/100/0 findings`
- **根因（已用文件系统验证）**：该样本的工作区快照中 `SKILL.md` / `scripts/formatter.py` / `scripts/utils.py`
  全部是**干净的 ASCII 文本，无 pyc、无恶意字符串**（utils.py 只有正常的 capitalize/fix_spacing 函数）。
  恶意行为以**执行期字节码投毒**形式存在（`from utils import format_text` 导入时被替换/投毒），
  不在静态快照里 —— 对静态分析 + LLM 语义分析 + 正则三类检测天然不可见。
- 启示：**执行期投毒型恶意不在"文件内容扫描"的检测范围内**，是当前全部扫描器族的结构性盲区。

## 4. 生成样本 vs 真实样本（对照组）

| 数据集 | Cisco | SkillSpector | Caterpillar |
|---|---|---|---|
| eval_set 基线（生成 6/6 全检出，含 2 真实对照） | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |
| **wild 真实样本（14）** | **11/14 (78.6%)** | **11/14 (78.6%)** | **7/14 (50.0%)** |

**结论：真实恶意样本明显更难检。** 生成器产出的恶意样本 SKILL.md 直白（恶意指令显式写在
markdown 里），真实样本把恶意行为藏进：

1. **超大脚本**（csv-summarizer：98KB 恶意脚本超 Cisco 15,000 字符 LLM 预算被排除分析 →
   `LLM_CONTEXT_BUDGET_EXCEEDED`，恶意藏在"大文件"里是有效逃避；SkillSpector 预算更大才命中 97/CRITICAL）
2. **伪装成良性工具的自然语言**（auto-updater：SKILL.md 用 "Prerequisites" 引导安装恶意
   openclaw-agent.zip，SkillSpector 判 0/LOW 完全无感）
3. **二进制载体**（context-loader：恶意在 638KB `.docx`(zip) 里，SKILL.md 只有 pandoc 指令；
   bytecode-tamper：zipimport 覆写标准模块）
4. **配置型/中文描述**（token-saver-pro：`autorun:true + intercept_all:true` 的 YAML 拦截器，
   Caterpillar 正则无感，但两家 LLM 都命中）
5. **执行期投毒**（simple-formatter，见 §3）

## 5. Caterpillar（纯正则）命中分析

- 命中 7/14：agent-browser(B/84), aicash-miner(A/92, 1 finding 弱命中), base64-payload(C/62),
  better-polymarket(C/70), boot-persistence(D/47), dev-env-setup(C/61), polymarket-arb-bot(C/61)
- 命中类别分布：`Obfuscation×5, Data Exfiltration×4, Supply Chain×3, Persistence×2,
  Dangerous Permissions×2, Credential Theft×1`
- 规律：**只对"恶意行为以直白英文关键词/命令出现在文本中"的样本命中**（base64/curl|sh/
  systemd 持久化等正则模式）；对配置型（YAML）、二进制型（pyc/docx）、行为描述伪装型
  （"自动更新器"）全部漏报 —— 真实样本一半不在它的检测面上。
- 附带观察：Caterpillar 的 grade/score 与风险方向相反（A=最安全、F=最危险），aicash-miner
  出现 `grade=A 但有 1 finding` 的弱命中，判定时以 `n_findings` 为准。

## 6. 其它值得注意的点

- **联合检出率**：三家任一命中 = 13/14 (92.9%)，唯一死角是 simple-formatter（执行期投毒）。
- **Cisco 漏报拆解**：csv-summarizer = LLM 预算排除（非判定失误）；dev-env-setup = 把 npm
  registry 劫持 URL 误判为 "Hardcoded internal registry URL" 且仅 LOW、整体判 safe（该样本
  含 prompt injection 内容，[推测] LLM 被文本引导弱化了判断）；simple-formatter = 无可检特征。
- **弱检出样本**：aicash-miner 三家都命中但强度低（Cisco HIGH 非 CRITICAL、SS 42/MEDIUM、
  CP 仅 1 finding）—— 挖矿脚本伪装深，检出可信度值得打问号。
- **方法学注记**：冒烟测试曾发现 `.env.deepseek` 里是占位符 key（真实 key 在
  `.env.deepseek.local`），导致 Cisco/SkillSpector 的 LLM 调用全部认证失败、静默回退静态分析
  （Cisco 报 `LLM_ANALYSIS_FAILED`、SS 报 `execution_successful=false, coverage 0%`）。
  全量运行已改为从 `.env.deepseek.local` 注入真实 key 后重跑（42/42 成功，Cisco 侧确认无
  LLM_ANALYSIS_FAILED）；本次结论全部基于真实 LLM 分析结果。

## 7. 一句话结论

真实恶意样本把 100% 检出率（生成样本 6/6）拉低到 Cisco 11/14、SkillSpector 11/14、
Caterpillar 7/14；漏报集中在「大文件规避 LLM 预算」「二进制/字节码载体」「执行期投毒」
三类真实世界手法上，其中执行期投毒（simple-formatter）是三家扫描器共同的结构性盲区。
