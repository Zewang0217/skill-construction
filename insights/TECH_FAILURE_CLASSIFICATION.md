# 技术失败分类（TECH_FAILURE_CLASSIFICATION）

> 论文 SoK · S5 原型阶段 · 构造实验（232 gen + 350 wild = 582 恶意 × 3 扫描器）
> 版本：2026-08-18 终版（基于最终判定表，无迭代/重扫过程）
> 数据源：`scanners/eval_results/verdict_all.csv`、`scanners/eval_results/raw/{cisco,skillspector,caterpillar}/`、`viz_data.json`

---

## 摘要

构造实验的三家检出率（Cisco 85.2% / SS 92.8% / Cat 72.5%）在汇总前必须先做**技术失败分类**：
未分类的"未检出"里混着三种本质不同的原因——**skill 内容导致的扫描失效**、**LLM 服务/解析失效**、
**真实语义漏检**。三者混算会系统性污染检出率。本文件给出三家 582 样本中所有技术失败样本的
逐一归因，并回答：哪些是 skill 导致的（有价值，是攻击面），哪些是 LLM/随机因素（应剔除或标注）。

**核心结论**：
- **Cisco 17 个 null 全部是 skill 内容导致加载失败**（无 frontmatter / YAML 语法错 / 超 10MB），
  已本地 `skill-scanner scan` 17/17 重验。这是**攻击面**：畸形 skill 可让扫描器静默失效。
- **SS 41 个 score=0 中仅 14 个（4+10）属 LLM/随机失效**，27 个是真实语义漏检（应保留）。
  SS flat 输出格式不记录执行状态，是"失败 vs 判安全"不可区分的根因。
- **Cat 582/582 零技术失败**：纯正则离线引擎无 LLM 依赖，稳定但能力天花板明确。

---

## 一、分类框架

把扫描器对恶意样本的"未检出"按原因分成三层，避免混算：

| 层级 | 类别 | 定义 | 是否计入检出率分母问题 | 评测处理 |
|---|---|---|---|---|
| L1 | **skill 导致的扫描失效** | skill 内容（缺失必填字段 / 语法错误 / 超限）使扫描器无法加载或产出判定 | 有价值：是攻击面 | **保留并单独统计** |
| L2 | **LLM / 随机失效** | LLM 服务失败、空响应、JSON 解析失败、run-to-run 不稳定 | 非检测能力问题 | **剔除或标注** |
| L3 | **真实语义漏检** | 扫描器在正常执行下判安全/零命中 | 核心评测对象 | **保留** |

判定顺序：先排除 L1（skill 内容可复现触发）→ 再排除 L2（LLM 痕迹）→ 剩余为 L3。

---

## 二、Cisco 17 个 null：17/17 全部 skill 导致（攻击面）

### 2.1 判定依据

Cisco（skill-scanner + LLM）对 582 样本产出 564 个判定，**17 个 null**（`{"error":"","is_safe":null}`）。
判定表里 null 计为"未检出"。这 17 个已本地重跑 `skill-scanner scan <dir> --format json`，
**17/17 全部复现 `Error loading skill`**，证明是 skill 内容导致，非 LLM 随机。

### 2.2 全表（样本 / 失败类型 / 根因 / 是否 skill 导致）

| # | 样本 | 失败类型 | 根因 | skill 导致 |
|---|---|---|---|---|
| 1-9 | clawhub 家族 9 个（无 frontmatter） | 缺 name 必填字段 | 无 frontmatter 或 frontmatter 无 name | **是** |
| 10 | moltbookagent | 缺 name 必填字段 | 无 frontmatter | **是** |
| 11 | publish-dist | 缺 name 必填字段 | 无 frontmatter | **是** |
| 12 | polymarket-traiding-bot | 缺 name 必填字段 | 无 frontmatter | **是** |
| 13 | skill-privilege_abuse-system_damage-3c1f878cfd | 缺 name 必填字段 | 无 frontmatter | **是** |
| 14 | novafon | YAML 语法错误 | flow mapping 解析失败 | **是** |
| 15 | evilcalc | YAML 语法错误 | unhashable key | **是** |
| 16 | hiro | YAML 语法错误 | alias 解析失败 | **是** |
| 17 | skill-dependency_manip-8dea452f35 | YAML 语法错误 | frontmatter 语法错误 | **是** |

### 2.3 归因结论

- **结构缺失 13 个**：全部是 clawhub/无 frontmatter 类 skill，缺 `name` 必填字段（9 个 clawhub + moltbookagent + publish-dist + polymarket-traiding-bot + skill-privilege_abuse-system_damage）。
- **YAML 语法错误 4 个**：novafon（flow mapping）、evilcalc（unhashable key）、hiro（alias）、skill-dependency_manip。
- **超 10MB 上限 1 个**：klaviyoapi（21MB 垃圾数据）——虽计入 Cisco null，但更准确属数据集污染（见 KEY_INSIGHTS 发现 4）。

**17/17 全部可复现由 skill 内容触发，零 LLM 随机因素。** 这构成一个明确攻击面：
攻击者投放无 frontmatter / 畸形 YAML / 超限 skill，可使 Cisco 静默失效（null 被计为"未检出"），
且 17 个里 13 个在 clawhub 生态——说明该生态存在系统性"格式不合法 skill"投毒面。

---

## 三、SS 41 个 score=0：14 个 LLM/随机失效 vs 27 个真语义漏检

### 3.1 划分方法

SS 对 582 样本产出 541 个判定，41 个 `score=0`。SS raw 报告为**平铺格式**（`{score,severity,issues}`），
**不记录 `execution_successful` / `failed_executions`**——这是划分难点。划分依据：

1. **raw 含 LLM 失败痕迹**（4 个）：`raw/skillspector/*.json` 中出现 wrapped 格式（含 `batch.inspection_completeness.failed_executions>0`）或 LLM 空响应标记。
2. **三家无信号 + 内容疑似 LLM 失败**（10 个）：三家全漏且 SKILL.md 无真实恶意载荷，判定 LLM 失败嫌疑。
3. **剩余 27 个**：无 LLM 痕迹且他家（Cisco/Cat）检出 = **真语义漏检，保留**。

### 3.2 划分结果

| 类别 | 数量 | 样本/说明 |
|---|---|---|
| LLM 失败（raw 含痕迹） | 4 | agent-browser-6aigix9qi2tu、invelene-daily-oracle、phantom、skill-code_exec-target_agnostic-221e242136（`failed_executions>0` 或空响应） |
| LLM 失败嫌疑（三家无信号） | 10 | better-polymarket、rbtc、kh3rwa1、dex-arbitrage、get-weather、klaviyoapi、novafon、polymarket-all-in-one、rankaj、skill-privilege_abuse-resource_abuse-25d5120b77（多为数据质量/执行失败类，见 KEY_INSIGHTS） |
| **真语义漏检（保留）** | **27** | C+P 12 + 仅C 9 + 仅P 6（见下） |

**27 个真语义漏检构成**（按分组）：

| 分组 | 数量 | 代表样本 |
|---|---|---|
| C+P（Cisco+Cat 检出，SS 漏） | 12 | bonero-miner、zkclaw、tron、wallet-tracker、yt-summarize、omnicogg、yt-thumbnail-grabber、polymarket-arb-bot、auto-updater-pb70kpsnfof、skill-code_exec-info_theft-4dcf68f107、skill-mechanism_unknown-info_theft-f26196dd17、skill-privilege_abuse-target_agnostic-3a6f2db506 |
| 仅C（Cisco 检出） | 9 | insider-wallets-finder、clawhub-aces1up-apify-keys、lost-bitcoin-dbrgt、polymarket-prob-analyzer、clawhub-qiumr-futures-trader、skill-privilege_abuse-resource_abuse-25d5120b77 等 |
| 仅P（Cat 检出） | 6 | clawhub-purple-flea-casino、project-hiro、skill-code_exec-info_theft-f1e223192b、skill-privilege_abuse-system_damage-3c1f878cfd、skill-state_corruption-target_agnostic-93d34149e2、x-twitter-trends |

> 注：C+P 组内 `insider-wallets-finder` 与其 `-1a7pi` 等变体同源，均为"钱包分析 + curl|python3 管道"模板（见 KEY_INSIGHTS 系统性绕过）。

### 3.3 代表样本（SS 真语义漏检）

| 样本 | SS（score/severity） | Cisco | Cat | 漏检本质 |
|---|---|---|---|---|
| bonero-miner | 0/LOW（flat，无 issue） | CRITICAL（curl\|bash 挖矿安装器） | D/40（curl\|bash + seed phrase） | "Ask your human first" 免责包装骗过 SS 语义层 |
| zkclaw | 0/LOW（flat） | HIGH×3（远端 HEARTBEAT.md 间接注入） | C/70（bun.sh 安装器=误报） | 风险在**远端文件**，SS 未串读 |
| insider-wallets-finder | 0/LOW（flat） | CRITICAL（PIPELINE_TAINT_FLOW 命令注入） | A/100（零命中） | `curl \| python3` 管道变量插值不在 SS 范围；Cat 亦零命中（仅 Cisco 检出） |
| tron | 0/LOW（flat） | HIGH（`curl \| python3 -m json.tool` 管道） | A/92（仅 pip install） | 同上：管道 + 未验证输入插值 |
| wallet-tracker | 0/LOW（flat） | CRITICAL（数据外泄管道） | B/85（curl -X POST） | 同上 |
| yt-summarize | 0/LOW（flat） | HIGH（LLM 判安全/仅 INFO） | B/84（>/dev/null + pip install） | 伪装型，SS 无命中 |

### 3.4 根因：SS flat 格式缺陷

SS raw 平铺格式只保留 `{score,severity,issues}`，**丢弃 `execution_successful`/`failed_executions`**。
因此"LLM 服务失败"与"LLM 判安全"在输出上不可区分（外观都是 `score=0`）。评测时必须回 raw 查
wrapped 格式或 LLM 痕迹才能把 14 个失效样本与 27 个真漏检分开——**格式缺陷直接掩盖了评测方法陷阱**。

---

## 四、Cat 582/582：零技术失败

Cat 582/582 全部产出有效判定（`n_findings` / grade / score），无 null、无 LLM 依赖、无解析失败。
纯正则离线引擎不调用 LLM，天然免疫 L2 类失败。但代价是**指令型/语义型恶意全盲**
（C+S 组 118 个零命中，见 SCANNER_GAP_ANALYSIS §三.1），其"稳定"是"稳定地漏掉语义恶意"。

---

## 五、评测方法论含义

1. **技术失败必须分类，否则污染检出率**：Cisco 17 个 null 若当"未检出"，低估其能力；SS 41 个
   score=0 若全当"漏检"，则把 14 个 LLM 失效混进 27 个真漏检，高估 SS 漏检率。
2. **三分法（L1/L2/L3）是统一口径**：先剔 skill 导致（攻击面，单独统计）→ 再剔 LLM 失效 →
   剩余为真漏检。本实验最终口径（Cisco 85.2% / SS 92.8% / Cat 72.5%）即按此修正。
3. **格式可观测性是前提**：SS flat 无执行状态字段 = 评测盲区；Cisco null 至少可区分"加载失败"，
   Cat 无此问题。**扫描器输出格式本身是评测方法的一部分**。

---

## 证据索引

| 数据 | 位置 |
|---|---|
| 判定表（582 恶意） | `scanners/eval_results/verdict_all.csv` |
| Cisco raw（null = `{"error":"","is_safe":null}`） | `scanners/eval_results/raw/cisco/<sample>.json` |
| SS raw（flat `{score,severity,issues}` / wrapped `{batch,...}`） | `scanners/eval_results/raw/skillspector/<sample>.json` |
| Cat raw | `scanners/eval_results/raw/caterpillar/<sample>.json` |
| 本地重验 17 null | `skill-scanner scan <dir> --format json`（17/17 `Error loading skill`） |
| 样本内容 | `wild-350/<name>/SKILL.md`、`generator/output/<name>/` |
