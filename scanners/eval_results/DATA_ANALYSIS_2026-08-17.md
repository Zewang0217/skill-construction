# 恶意样本数据分析（2026-08-17）

> 数据：`scanners/eval_results/verdict_all.csv`（581 恶意样本 × 3 家扫描）
> 口径：Cisco=is_safe==False；SS=score>0；Cat=n_findings>0

---

## 1. 样本构成：这些恶意 skills 是什么？

| 来源 | 数量 | 说明 |
|---|---|---|
| **真实 wild** | 350 | MalSkillBench 官方 703 WILD 分层抽样（B1-B15 行为标签，非 B4 全 94 + B4 抽 256）|
| **构造 generated** | 231 | 基于我们 taxonomy 43 坐标生成（COORD_SEEDS：mapping-db 证据 + ATTACK_SEEDS + 手写行为）|

**两者区别**：
- **真实 wild**：ClawHub 等公开注册表抓取的真实恶意 skill（agent-browser 挖矿、auto-updater 伪装、psyclaw 状态机强制等），MalSkillBench 用 Docker 沙箱 runtime 验证过真恶意
- **构造 generated**：我们按三维坐标（source×mechanism×target）用 LLM 生成，恶意行为落在坐标语义内——**不是真实攻击，是"模拟恶意"**，用于评测扫描器对 taxonomy 各坐标的检出能力

## 2. 整体状态：每个 skill 被几家标记？

**581 恶意样本的标记分布**：

| 被标记数 | 样本数 | 占比 | 含义 |
|---|---|---|---|
| **3 家全标** | 301 | 51.8% | 三家都检出（强信号恶意）|
| **2 家标** | 200 | 34.4% | 两家检出（有分歧）|
| **1 家标** | 69 | 11.9% | 仅一家检出（各家盲区互补）|
| **0 家标** | 11 | 1.9% | 三家全漏（结构性盲区）|

**组合分布**（谁检出谁漏）：
- 仅 Cisco：7 | 仅 SS：48 | 仅 Caterpillar：14
- Cisco+SS：93 | Cisco+Cat：10 | SS+Cat：97

**洞察**：
- **SS+Cat 组合最多（97）**——两家对构造样本的检出高度互补
- **仅 SS 48 个**——SS 最能抓"文本指令型"恶意（纯正则的 Cat 和重代码的 Cisco 都漏）
- **0 家标 11 个**——包括 8 个生成失败的纯良性 + 3 个隐藏极深的真恶意（simple-formatter 类执行期投毒）

## 3. 具体发现：每家检出什么？

### Cisco（LLM+静态，411 flagged）
| 发现类型 | 次数 | 含义 |
|---|---|---|
| LLM_SUPPLY_CHAIN_ATTACK | 396 | 供应链攻击（随包恶意）|
| MANIFEST_MISSING_LICENSE | 308 | 缺许可证（低危）|
| LLM_COMMAND_INJECTION | 208 | 命令注入 |
| LLM_OBFUSCATION | 157 | 混淆 |
| LLM_SKILL_DISCOVERY_ABUSE | 147 | skill 发现滥用 |
| LLM_DATA_EXFILTRATION | 141 | 数据外泄 |
| LLM_HARMFUL_CONTENT | 90 | 有害内容 |
| LLM_PROMPT_INJECTION | 74 | 提示注入 |

### SkillSpector（LLM+规则，~580 flagged）
| 规则 | 次数 | 含义 |
|---|---|---|
| SQP-2 | 24 | 语义质量问题（描述与实际不符）|
| LP3 | 15 | 权限声明问题 |
| PE3 | 11 | 凭证/敏感文件访问 |
| AST4 | 10 | 危险代码模式 |
| SDI-1/2 | 18 | skill 描述-实现不一致 |
| PE2 | 9 | sudo/提权 |
| SC4/SC1 | 11 | 供应链风险 |
| SSD-1/2 | 10 | 安全设计缺陷 |
| MP3 | 4 | 记忆投毒 |

> 注：仅含 raw 中带 issue 详情的样本（平铺格式只有 score 无详情），完整 score 统计见 §2

### Caterpillar（纯正则，382 flagged）
| 发现类型 | 次数 | 含义 |
|---|---|---|
| Obfuscation | 291 | 编码/动态执行 |
| Supply Chain | 213 | 包安装等供应链风险 |
| Data Exfiltration | 134 | 数据外泄 |
| Persistence | 37 | 持久化 |
| Credential Theft | 34 | 凭证窃取 |
| Dangerous Permissions | 33 | 危险权限 |
| Crypto Theft | 17 | 加密货币窃取 |

## 4. 与 taxonomy 的关系

- **构造样本**按 43 坐标生成 → 评测反映"每个坐标扫描器能否检出"
- 真实样本映射到坐标 → 评测反映"真实威胁分布下检出率"
- **wild 检出率（Cisco 83%）> 构造检出率（Cisco 51.5%）**：构造样本更接近真实伪装（mdb 证据驱动的隐蔽恶意），暴露更多盲区——这是论文的核心对照
