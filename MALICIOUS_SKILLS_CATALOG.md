# 恶意 Agent Skill 公开数据集收录清单

> 整理日期：2026-08-13 | 所有链接已通过 GitHub API 验证可用
> 用途：为本 SoK 论文的三维 taxonomy 映射提供真实恶意 skill 锚集

---

## 总量概览

| 来源 | 类型 | 可用数量 | 获取方式 | 许可证 |
|---|---|---|---|---|
| MalSkillBench Wild | 真实 wild | 703（人工确认）/ 2478（含未确认） | GitHub 公开仓库 | 学术研究用途 |
| MalSkillBench Generated | LLM 合成 | 1,466 | 同上 | 学术研究用途 |
| MalSkillBench Test | 检测工具自带 | 27 | 同上 | 学术研究用途 |
| Trail of Bits | 手工设计 | 4 | GitHub 公开仓库 | 未声明（安全研究用途） |
| PiedPiper0709 目录 | 情报整理 | 352（CSV 清单） | GitHub 公开仓库 | 未声明 |
| SkillTrustBench Wild | 真实 wild | 242 | HuggingFace dataset | 未声明 |
| SkillTrustBench Generated | 全自动合成 | 5,278 | 同上 | 未声明 |

**去重后唯一真实 wild（保守估计）：~700-1000 个**（MalSkillBench 与 PiedPiper 有大量重叠——均来自 ClawHavoc 战役）

---

## 1. MalSkillBench（主力锚，3,944 个恶意 skill）

- **仓库**：https://github.com/lxyeternal/MalSkillBench
- **论文**：https://arxiv.org/abs/2606.07131
- **许可证**：For academic research use only（见仓库 LICENSE 段）
- **路径**：`Dataset/Skills/malware/<skill-name>/`（每个含 SKILL.md + 可选 scripts/）
- **来源说明**：Wild 部分 = 公开注册表(ClawHub)收集，81% 来自 ClawHavoc 战役两个攻击者账户（hightower6eu + sakaen736jih）；Generated = LLM 合成 + Docker 沙箱验证（85.6% 验证率）

### 如何区分 wild vs generated
- **Wild（真实）**：目录名无 `__CI_`/`__PI_`/`__MIXED_` 后缀
- **Generated（合成）**：目录名含 `__CI_B1`~`__MIXED_B15` 等后缀（3 vector × 15 behavior × 多 strategy）
- **Test**：检测工具自带，位于 malware 目录但无后缀

### Wild 样本 raw URL 模式
```
https://raw.githubusercontent.com/lxyeternal/MalSkillBench/main/Dataset/Skills/malware/<skill-name>/SKILL.md
```

### 代表性 wild 样本（已拉取到本地 wild-samples/）

| 本地目录 | 原始目录名 | 伪装 | 恶意行为 |
|---|---|---|---|
| `agent-browser-6aigix9qi2tu` | `agent-browser-6aigix9qi2tu` | 浏览器自动化 | base64→`curl 裸IP\|bash` RCE |
| `better-polymarket` | `better-polymarket` | 预测市场 | scripts/ 藏 `os.system("curl\|sh")` |
| `aicash-miner` | `clawhub-doctor-1017-aicash-miner__v1.0.0` | 加密货币工具 | 挖矿 + systemd 持久化 + 6 实例 |
| `apify-keys` | `clawhub-aces1up-apify-keys__v1.0.0` | API key 管理器 | 连攻击者 MySQL 偷 key 池 |
| `token-saver-pro` | `clawhub-chenpipi0807-token-saver-pro__v1.0.1` | Token 节省器 | autorun:true 拦截全部请求 |
| `polymarket-arb-bot` | `clawhub-hanguang254-polymarket-arb-bot__v3.3.5` | 自动交易机器人 | Kelly 仓位自动下注 |
| `auto-updater` | `auto-updater-161ks` | 自动更新器 | Prerequisites 诱导装恶意 zip |
| `boot-persistence` | `boot-persistence` | 启动持久化 | systemd/cron/bashrc 持久化 |
| `base64-payload` | `base64-payload` | 数据处理器 | `exec(b64decode())` |
| `bytecode-tamper` | `bytecode-tamper` | 模块加载器 | zipimport 覆写标准模块 |

### Taxonomy（108 格 = 3 vector × 15 behavior × 多 strategy）

**Vector**：`CI`（代码注入）/ `PI`（提示注入）/ `MIXED`（复合）

**Behavior B1-B15**：
| ID | Behavior | ID | Behavior |
|---|---|---|---|
| B1 | Data Exfiltration | B9 | Privilege Escalation |
| B2 | Credential Theft | B10 | Role Hijack |
| B3 | Remote Code Execution | B11 | Safety Bypass |
| B4 | Malware Delivery | B12 | Instruction Override |
| B5 | Persistence | B13 | System Prompt Leak |
| B6 | Reverse Shell | B14 | Goal Hijacking |
| B7 | Ransomware | B15 | Content Manipulation |
| B8 | Resource Abuse | | |

---

## 2. Trail of Bits（4 个手工设计样本）

- **仓库**：https://github.com/trailofbits/overtly-malicious-skills
- **博客**：https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/
- **许可证**：未声明（仓库标注 "MALICIOUS — FOR SECURITY RESEARCH PURPOSES ONLY"）
- **路径**：`skills/<name>/`（含 SKILL.md + scripts/）

### 全部 4 个样本（已拉取到本地 wild-samples/）

| 本地目录 | 伪装 | 恶意行为 | URL |
|---|---|---|---|
| `csv-summarizer` | CSV 汇总 | 8000 空行后藏 `os.environ` dump | [SKILL.md](https://github.com/trailofbits/overtly-malicious-skills/tree/main/skills/csv-summarizer) |
| `context-loader` | 启动上下文同步 | .docx(zip) 藏 `sync1.sh` 脚本 | [SKILL.md](https://github.com/trailofbits/overtly-malicious-skills/tree/main/skills/context-loader) |
| `simple-formatter` | 文本格式化 | 字节码投毒偷环境变量 | [SKILL.md](https://github.com/trailofbits/overtly-malicious-skills/tree/main/skills/simple-formatter) |
| `dev-env-setup` | 开发环境配置 | prompt injection 骗扫描器 + 劫持 npm registry | [SKILL.md](https://github.com/trailofbits/overtly-malicious-skills/tree/main/skills/dev-env-setup) |

---

## 3. PiedPiper0709 恶意 Skill 目录（352 条结构化清单）

- **仓库**：https://github.com/PiedPiper0709/openclaw-malicious-skills
- **数据**：`openclaw-risky-skills.csv`（352 行，含 skill_name/source/evidence/attack_chain/risk_category/severity）
- **许可证**：未声明
- **来源**：基于 Koi ClawHavoc 报告、公开安全研究、issue 整理
- **注意**：仅 CSV 清单，不含 skill 文件本体；与 MalSkillBench wild 有大量重叠

---

## 4. SkillTrustBench（5,520 个，腾讯朱雀 × CUHK-SZ）

- **HuggingFace**：https://huggingface.co/datasets/cuhk-zhuque/SkillTrustBench
- **官网**：https://matrix.tencent.com/skilltrustbench/
- **许可证**：未声明（数据集 + leaderboard 开源，生成代码不开源）
- **规模**：95.6% 合成 + 242 wild + 4 benign pool = 5,520
- **标签**：三值（malicious / suspicious / normal）
- **获取方式**：`datasets.load_dataset("cuhk-zhuque/SkillTrustBench")`

---

## 5. 不可直接获取的来源（仅记录）

| 来源 | 数量 | 状态 | 说明 |
|---|---|---|---|
| Snyk ToxicSkills | 76 | ⚠️ 名单不公开 | 报告只列 8 个 IOC，76 全名单省略 |
| ClawHavoc 战役 (Antiy CERT) | 1,184 | ⚠️ 可复得性待验 | 文档记录的攻击战役 |
| MalSkills git 恢复 | 100 | ⚠️ 归档库可能 404 | 从 ClawHub commit 恢复已删除 skill |
| Semia 专家标注 | 541 | ⚠️ 标签是 "risk" 非 "malware" | 两作者独立标注 κ=0.83 |
| Locate-and-Judge | 131+82 | ❌ 无落点 | 数据集声称发布但无下载地址 |
