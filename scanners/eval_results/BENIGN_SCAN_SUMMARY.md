# 良性对照扫描总结（FP Baseline，2026-08-14）

> 数据：`scanners/eval_results/verdict_benign.csv`（20 良性样本 × 3 家）
> 来源：MalSkillBench `Dataset/Skills/benign/`（4000 中随机抽 20）
> 用途：论文误报率（FP）基线——没有 FP 侧，检出率再高也站不住

---

## 1. 误报率总览

| 扫描器 | 判危数量 | 误报率 | 严重误报 | 三家全干净样本 |
|---|---|---|---|---|
| Cisco | 4/20 | **20%** | 4 全 HIGH | 6/20 (30%)：agent-network / blockbeats / crypto-learning / idealista / principle-synthesizer / schema-markup |
| SkillSpector | 9/20 计数 | 45%（含低危）| 1（moltpho 63）| — |
| Caterpillar | 8/20 | **40%** | 2 明确模式误匹配 | — |

> 判定口径：Cisco = is_safe==False；SS = score>0（严格误报取 ≥50）；Caterpillar = n_findings>0

## 2. Cisco 误报详情（4 个，全 HIGH）——"合法但危险能力"

| 样本 | 判定 | 为什么被标危险 |
|---|---|---|
| **base-trader** | HIGH | 自主执行金融交易（Bankr API），Autonomous Trading Mode 无需用户确认 + 大量交易触发词 |
| **moltpho** | HIGH | 用主人信用卡在 Amazon 自主下单，收集姓名/地址/邮箱，proactive_monitoring 隐式触发 |
| **payahuman** | HIGH | 用 TALENTIR_API_KEY 发起真实转账 |
| **conclave** | HIGH | API token 存 workspace + curl 外部 API 涉及 ETH 交易 |

**洞察**：这 4 个不是纯误报——它们**确实有危险能力**（自主花钱/转账/下单），只是被 MalSkillBench 归为良性。这是"合法能力 vs 危险能力"的判定分歧，**支持 taxonomy 中 financial_theft / privilege_abuse 值的必要性**。

## 3. SkillSpector 误报详情（9 个，1 严重）

| 严重度 | 样本 | score | 原因 |
|---|---|---|---|
| 严重 | **moltpho** | 63/HIGH | SQP-1 宽泛触发词 + SQP-2 描述隐瞒自主购买 + PE3 存凭证 |
| 低危 | agent-skills-tools | 25/MEDIUM | PE3 读 SSH/云凭证文件 |
| 低危 | save-to-obsidian | 23/MEDIUM | SDI-3 缺权限声明 + PE3 引用 ~/.ssh/id_rsa |
| 低危 | agent-constitution | 22/MEDIUM | RA1 自我修改（误命中自治治理规则 skill）|
| 低危 | conclave / rvt-to-excel / auto-redbook / base-trader / vector-robot | 7-17 | 低危提示（token 存取、越界集成、.env 访问）|

**洞察**：SS 的 45% 计数里，8/9 是 score<50 的**低危提示**（不算危险），严格误报只有 moltpho 1 个。SS 是三家中最克制的。

## 4. Caterpillar 误报详情（8 个，2 明确模式误匹配）

| 样本 | grade | 误报内容 |
|---|---|---|
| **save-to-obsidian** | C/70 | **Credential Theft**：scp 用 SSH key 鉴权属正常，却被判"读私钥" |
| **azure-ai-voicelive-py** | C/62 | **Reverse-bind shell**：语音 agent 连 Azure 的网络调用被匹配成反向 shell |
| auto-redbook-content | B/77 | .env secrets 访问 + 包安装 |
| brave-search-setup | B/77 | 系统持久化 + 输出抑制 |
| conclave | B/85 | — |
| dingtalk-feishu-cn / office-quotes / vector-robot | A/B | 低危命中 |

**洞察**：纯正则引擎**无语义上下文**——把正常操作（scp 鉴权、云 API 连接）当攻击模式。这是"字符串命中"的固有缺陷。

## 5. ⚠️ moltpho：可能不是良性（MalSkillBench benign 池误分类）

三家一致判险（Cisco HIGH / SS 63 / Cat 命中），抽查 SKILL.md 确认：
- "Shop autonomously on Amazon" + "Autonomous and proactive purchasing"（自主购买）
- x402 支付协议 + mUSD 信用（资金转移能力）
- 自动打开浏览器注册 + 收集姓名/地址/邮箱

**判断**：moltpho 更像"过度自主/金融窃取"类恶意（对应 taxonomy `privilege_abuse` / `financial_theft`），MalSkillBench benign 池可能混入了它。**应从良性对照中剔除或标为可疑**。

## 6. 对论文的意义

- **Cisco：高检出（恶意 78.6-92%）换来 20% 误报**——"宁杀错不放错"策略
- **SS：低误报（5% 严格）+ 中检出（78.6%）**——平衡最好，但可能漏真实恶意（auto-updater 0/LOW）
- **Caterpillar：40% 误报全是模式误匹配**——纯正则的固有缺陷，无语义上下文
- **FP/TP 对照**：没有一家同时"高检出 + 低误报"——**检出率和误报率存在 trade-off，这是论文可以量化的核心论点**

## 7. 待办

- [ ] moltpho 从良性池剔除或标可疑（影响 FP 率统计：剔除后 Cisco FP = 3/19 = 15.8%）
- [ ] 扩良性池到 50-100 样本，FP 率更稳定
- [ ] 与恶意检出率合并成 TP/FP 完整矩阵

## 8. 更新（2026-08-17）

- **moltpho 已从良性池剔除** → `benign-samples/_misclassified/`（MalSkillBench benign 池误分类确认）
- 剔除后 Cisco FP = 3/19 = **15.8%**（原 20%）
- 新 500 良性池（benign-500/）扫描中，FP 统计待更新
