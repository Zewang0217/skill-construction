# 扫描器漏检/误检根因分析汇总（2026-08-17）

> 5 个 subagent 并行分析 581 恶意样本中的特殊分组，报告见同目录 ANALYSIS_*.md（5 份，1064 行）
> 分组：全漏 11 / 仅Cisco 7 / 仅SS 48 / 仅Cat 14 / C+S 93（Cat漏）/ C+Cat 10（SS漏）/ S+Cat 97（Cisco漏）
> 判定口径：Cisco=is_safe==False；SS=score>0；Cat=n_findings>0

---

## 一、最重磅发现：漏检 ≠ 扫描器能力弱，一半是"技术失败 + 阈值设计"

### 1. Cisco 漏检的三重机制（S+Cat 组 97 个 + 仅SS 组 48 个）

| 机制 | 数量 | 说明 |
|---|---|---|
| **LLM 技术失败** | 62/97 + 24/48 | `LLM_ANALYSIS_FAILED`：47 个空响应（DeepSeek 后端故障）+ 15 个解析失败（LLM 响应含 CRITICAL 检出但 ResponseParser 三路径全失败被整包丢弃）|
| **阈值设计缺陷** | 24/97 + 多数 | `is_safe = 无 HIGH/CRITICAL finding`（models.py:206）——92 个 safe 样本的 255 个 finding 全 ≤MEDIUM（185 MEDIUM/37 INFO/33 LOW），**检测到了但阈值吞掉** |
| **真判定失误** | 6/97 | LLM 判 safe 零 finding（社工包装骗过）|

**结论**：Cisco 的"漏检"约 **70% 是基础设施/管线问题**（LLM 失败+解析丢弃），不是检测能力。**15 个样本明明检出 CRITICAL/HIGH 却因解析失败被判 safe——检测成功但管线丢失**，这是评测方法的重大发现。

### 2. Caterpillar 的漏检（CS 组 93 个全漏）

**93/93 全部 grade A / 零命中**——纯正则设计缺陷：
- **无 Python/JS API 规则**：`requests.post`、`subprocess.run`、`socket.sendto`、`urllib` 对 15 条正则全不可见
- **关键词窄化规避**：`npm i` ≠ `npm install`、`cron job` ≠ `crontab`、`data:;base64` ≠ `base64 -d`、`~/.openclaw/` ≠ `~/.aws/`
- **零提示注入规则**：无 ignore/bypass/隐藏指令模式
- **openclaw 供应链家族 53/74 (72%)**：都写"下载 openclaw-agent 二进制 + glot.io/rentry 粘贴脚本"——无 curl|bash 管道所以 curl|sh 规则不触发

### 3. SS 的漏检（CC 组 10 个）

- **run-to-run 不稳定**：agent-browser 两次扫描 100→0（LLM 执行失败被平铺格式掩盖）
- **社工包装骗过 LLM**：bonero-miner 的 "Ask your human first" 包装让 SS 只报 SQP-2（score 8），Cat 却抓到 CRITICAL curl|bash
- **远距离威胁**：风险在引用文件（HEARTBEAT.md）不在内联 → 分析面外

---

## 二、方法学警告：12% 的 Cat 检出是 ground-truth 泄漏驱动

**AnalyzeDoubleSC 离线重跑对照实验**：
- 67 个 gen 样本中 **8 个 (12%) 的 Cat 检出完全由 `_provenance.json` 泄漏驱动**（Caterpillar 的 collector 拼接所有文本文件，provenance 里的坐标/行为描述被正则命中）
- 59 个 (88%) 去掉泄漏仍检出——真实能力
- Cisco 输入不含 provenance（0/67 引用 seed 文本）——漏检为真实缺口
- 30 个 wild 无 provenance，双检出证据干净

**⚠️ 论文必须披露**：评测输入必须剔除 ground-truth 文件（`_is_ground_truth` 过滤只作用于 Cisco/SS 的 copy_tree，Caterpillar 直接扫原目录——漏洞）

---

## 三、数据质量问题（全漏组 11 个的真实构成）

**"三家全漏"≠ 扫描器盲区**，拆解后：

| 类别 | 数量 | 样本 |
|---|---|---|
| 真恶意但脚本被剥离 | 2 | better-polymarket（scripts/polymarket.py 的 os.system curl|sh 不在当前 wild-350 快照）|
| 重复样本（md5 相同）| 4 | rankaj==get-weather、polymarket-all-in-one==better-polymarket |
| 数据集误分类 | 3 | get-weather/novafon（可能良性）|
| 生成失败（构造）| 1 | skill-privilege（provenance 声称恶意但 config_parse.py 纯良性 + LLM 超限排除）|
| **真三家全漏** | **1** | **kh3rwa1**（B12 纯散文指令覆盖，SS 0/Cat A/Cisco 报错）|
| Cisco 二进制掩码 | 2 | dex-arbitrage、project-init（is_safe=True 藏 MEDIUM 检出）|

**修正后真实全漏率**：581 中仅 **1 个**（kh3rwa1，纯指令型）是三家真正的共同盲区。

---

## 四、各扫描器"独占检出"的性质

| 独占组 | 数量 | 性质 |
|---|---|---|
| 仅 Cisco | 7 | 6/7 是 LLM 语义推理真实威胁（工具影子/下载执行/混淆二进制）；1 个疑似误报（math-calculator "MASTER"）|
| 仅 SS | 48 | 多引擎组合（LLM+AST+正则+YARA）真检出；Cisco 漏因 24 技术失败 + 阈值 |
| 仅 Cat | 14 | **~6 个弱正则误报**（ncat 匹配 trunc*ncat*ed、Ledger 匹配钱包教学）+ 少数真签名但对手扫描失败 |

**洞察**：**Cisco 独占 = 语义推理优势；SS 独占 = 多引擎广度；Cat 独占 ≈ 误报为主**。单家检出不等于能力强，需逐样本核对。

---

## 五、对论文的启示（S4 scanner re-eval 章节）

1. **评测方法修正**：漏检要区分"技术失败 / 阈值放行 / 真漏检"三类，不能混为检出率
2. **阈值审计**：Cisco is_safe 应改为 MEDIUM+安全敏感类告警（可立即显形 24 个样本）
3. **管线修复**：ResponseParser 解析失败降级展示，防止 CRITICAL 检出被丢弃
4. **ground-truth 隔离**：Caterpillar 扫描输入必须剔除 _provenance.json（12% 泄漏驱动）
5. **样本去重**：md5 去重（581 实际 577 唯一）
6. **run-to-run 稳定性**：SS 的 score 波动（100→0）需多次扫描取一致

## 六、证据索引

| 报告 | 覆盖 | 关键证据 |
|---|---|---|
| ANALYSIS_NONE_DETECTED.md | 全漏 11 | better-polymarket 脚本剥离、md5 重复、kh3rwa1 |
| ANALYSIS_SINGLE_SS.md | 仅 SS 48 | Cisco is_safe 阈值 models.py:206、LP3 兜底 |
| ANALYSIS_SINGLE_CISCO_CAT.md | 仅C 7+仅Cat 14 | sk-/sk_ 正则 bug、ncat 缺词边界 |
| ANALYSIS_DOUBLE_CS_CC.md | C+S 93 + C+Cat 10 | Cat 15 条正则清单、agent-browser 100→0 |
| ANALYSIS_DOUBLE_SC.md | S+Cat 97 | Cisco LLM 失败 62、阈值 24、12% 泄漏实验 |
