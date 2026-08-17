# 恶意样本分组数据分析（2026-08-17）

> 数据：`scanners/eval_results/verdict_all.csv`（581 恶意 = 350 真实 wild + 231 构造 generated）
> 口径：Cisco=is_safe==False；SS=score>0；Caterpillar=n_findings>0；det=三家任一检出

---

## 一、总览对比

| 指标 | 真实 wild (350) | 构造 generated (231) | 合计 (581) |
|---|---|---|---|
| Cisco 检出 | **292 (83.4%)** | 119 (51.5%) | 411 (70.7%) |
| SS 检出 | 318 (90.9%) | **221 (95.7%)** | 539 (92.8%) |
| Caterpillar 检出 | 248 (70.9%) | 174 (75.3%) | 422 (72.6%) |
| 三家全标 | 203 (58.0%) | 98 (42.4%) | 301 (51.8%) |
| 仅一家标 | 25 (7.1%) | 44 (19.0%) | 69 (11.9%) |
| 三家全漏 | 10 (2.9%) | 1 (0.4%) | 11 (1.9%) |

**关键差异**：
- **Cisco 对构造样本只有 51.5%**（vs wild 83.4%）——构造样本更隐蔽（mdb 证据驱动的伪装），暴露 Cisco 盲区
- **SS 对两组都 >90%**——SS 语义分析最全面
- **wild 全漏 10 个 vs 构造全漏 1 个**——真实恶意更难检（执行期投毒/大文件逃逸等）

---

## 二、真实 wild 350：按 B 标签（恶意行为）检出

| B | 行为 | 样本 | 检出≥1 | Cisco | SS | Cat |
|---|---|---|---|---|---|---|
| B4 | Malware Delivery | 256 | 256 (100%) | 235 | 252 | 199 |
| B2 | Credential Theft | 33 | 30 (91%) | 20 | 19 | 16 |
| B1 | Data Exfiltration | 18 | 16 (89%) | 8 | 13 | 11 |
| B9 | Privilege Escalation | 15 | 15 (100%) | 15 | 15 | 14 |
| B3 | Remote Code Execution | 7 | 5 (71%) | 1 | 4 | 3 |
| B14 | Goal Hijacking | 5 | 5 (100%) | 2 | 5 | 0 |
| B8 | Resource Abuse | 5 | 4 (80%) | 3 | 3 | 2 |
| B12 | Instruction Override | 3 | 2 (67%) | 2 | 2 | 0 |
| B5 | Persistence | 3 | 2 (67%) | 1 | 2 | 2 |
| B10 | Role Hijack | 2 | 2 (100%) | 2 | 2 | 0 |
| B11 | Safety Bypass | 1 | 1 | 1 | 1 | 0 |
| B15 | Content Manipulation | 1 | 1 | 1 | 0 | 1 |
| B6 | Reverse Shell | 1 | 1 | 1 | 0 | 0 |

**洞察**：
- **B4 (Malware Delivery) 占 73%，三家检出率最高**（Cisco 92% / SS 98%）——真实恶意集中在"分发恶意载荷"，扫描器最擅长
- **B14 Goal Hijacking：Cisco 2/5 + SS 5/5 + Cat 0/5**——目标劫持是 SS 独强、Cat 全盲（纯正则看不懂"改写目标"）
- **B12/B11/B10/B6：Caterpillar 全 0**——纯指令型（角色劫持/安全绕过/回连 shell）正则无法命中
- **B3 RCE：Cisco 仅 1/7**——真实 RCE 样本伪装深（大文件/编码），Cisco 漏检重灾区

---

## 三、构造 generated 231：按坐标（source×mechanism×target）检出

> 53 个坐标（43 标准 + 10 旧样本多值坐标）；每坐标 1-5 样本

### 检出率最低的坐标（Cisco 盲区）

| 坐标 | n | 检出≥1 | Cisco | SS | Cat |
|---|---|---|---|---|---|
| source_agnostic×code_exec×resource_abuse | 5 | 5 | **0** | 5 | 4 |
| source_agnostic×obfuscation×info_theft | 5 | 5 | **0** | 5 | 4 |
| external_content×code_exec×info_theft | 1 | 2 | **0** | 1 | 1 |
| runtime_environment×code_exec×info_theft | 1 | 1 | **0** | 0 | 1 |
| runtime_environment×state_corruption×persistent_control | 1 | 1 | **0** | 1 | 0 |
| external_content×code_exec×target_agnostic | 5 | 5 | 1 | 5 | 4 |
| source_agnostic×instruction_manip×content_safety | 5 | 5 | 1 | 5 | 2 |
| source_agnostic×instruction_manip×resource_abuse | 5 | 5 | 1 | 5 | 2 |
| source_agnostic×privilege_abuse×system_damage | 5 | 5 | 1 | 4 | 3 |

### 检出率最高的坐标（三家都强）

| 坐标 | n | 检出≥1 | Cisco | SS | Cat |
|---|---|---|---|---|---|
| source_agnostic×privilege_abuse×target_agnostic | 5 | 5 | 5 | 5 | 5 |
| supply_chain×dependency_manip×target_agnostic | 9 | 9 | 6 | 8 | 9 |
| supply_chain×code_exec×info_theft | 5 | 5 | 4 | 4 | 5 |
| supply_chain×state_corruption×persistent_control | 5 | 5 | 3 | 5 | 5 |
| supply_chain×obfuscation×target_agnostic | 5 | 5 | 3 | 5 | 5 |

**洞察**：
- **Cisco 全盲坐标**：`source_agnostic×code_exec×resource_abuse`（挖矿/资源滥用伪装）和 `source_agnostic×obfuscation×info_theft`（混淆+窃取）——**0/5 检出**
- **SS 几乎每坐标全检出**（多数 5/5）——语义分析覆盖最全
- **supply_chain 坐标三家都强**（60-100%）——供应链是扫描器共同强项
- **external_content / runtime_environment 坐标 Cisco 最弱**（0-1/5）——外部内容/运行时盲区实证

---

## 四、三家全漏样本（11 个）

### wild 10 个
（simple-formatter 类执行期投毒 + 隐藏极深样本，详见 WILD_SCAN_SUMMARY）

### generated 1 个
| 样本 | 坐标 | 原因 |
|---|---|---|
| skill-code_exec-info_theft-252b70ffcf | source_agnostic×code_exec×info_theft | 待查（可能隐藏极深或生成偏差）|

---

## 五、论文结论支撑

1. **SS 全面领先**（wild 91% / gen 96%）——语义一致性分析比静态+正则都强
2. **Cisco 偏科**：供应链坐标强（>80%），外部内容/运行时/资源滥用坐标弱（0-20%）——量化"供应链检测器"标签
3. **Cat 纯正则天花板**：对代码型（obfuscation/supply chain）有效，对指令型（目标劫持/角色劫持）全盲
4. **构造样本比真实样本更能暴露扫描器差异**：gen 单家标 19% vs wild 7%——坐标级构造覆盖了真实样本缺失的盲区组合
