# 恶意 Skill 构建方法 + 开源资源汇总

> 日期：2026-08-06 | 用途：与协作者共享
> 范围：所有做恶意 agent skill 构造/收集的工作，含开源链接
> 一手来源：arXiv 论文 + GitHub 仓库实测验证（2026-08-06）

---

## 一、MalSkillBench Wild 703 是什么

**Wild 703 = 真实世界暴露的恶意 skill，不是人造的。**

MalSkillBench 数据集分三个 split：

| Split | 数量 | 来源 | 人造/真实 |
|---|---|---|---|
| Generated | 3,214 | **MalSkillBench 团队用 LLM 造的**（taxonomy 驱动 + Docker 沙箱验证） | **人造** |
| **Wild** | **703** | **真实公开注册表收集 + 人工确认恶意** | **真实** |
| Test | 27 | 检测工具自带的确认恶意样本 | 真实 |

Wild 703 来源：
- 81% 来自两个 **ClawHavoc 攻击战役** 真实账户（hightower6eu 353 + sakaen736jih 216）
- 这些 skill 原本上传在 ClawHub 公共注册表，被安全研究人员发现后下架
- MalSkillBench 团队收集后**人工确认**恶意性
- 代码级验证（我们已做，拉取了 6 个样本逐个查代码）：全部含真实恶意载荷（远程下载执行 / 凭证窃取 / 挖矿持久化 / agent 劫持）

**论文原文**（README）：
> Wild | 703 | Collected from public registries and manually verified

---

## 二、构建方法全景 + 开源资源

### 方法 A：LLM 合成 + 沙箱验证（全自动，可复用）

| 项目 | MalSkillBench |
|---|---|
| **论文** | arXiv:2606.07131 |
| **GitHub** | https://github.com/lxyeternal/MalSkillBench |
| **开源内容** | ✅ 生成管线（`Core/generation/`）+ 验证管线（`Core/verification/`）+ 数据集 + 基线检测器 |
| **关键代码** | `agent.py`（生成主循环）、`generator.py`（LLM 合成）、`retriever.py`（知识检索）、`sandbox.py`（Docker 沙箱）、`verifier.py`（两层验证） |
| **seed** | 3 向量（CI/PI/MIXED）× 15 行为（B1-B15）× 插入策略 = 108 格 |
| **规模** | 3,214 generated（验证率 85.6%） |
| **自动化** | 全自动——LLM 写 SKILL.md + scripts，Docker 验证，失败带反馈重试 |
| **知识库** | CI: IntelliGraph（3026 恶意 PyPI 包）/ PI: WildJailbreak 等（20961 条注入语料） |
| **良性壳池** | 3458 个 SkillsMP 良性 skill（12 类） |
| **复用方式** | 替换 `Core/taxonomy/` 里的 taxonomy 定义即可用我们的坐标当 seed |

**生成流程**：
```
taxonomy cell (v, b, s)
  → 检索真实攻击模式（恶意包/注入语料）
  → 取良性 skill 壳做伪装
  → LLM 合成 SKILL.md + scripts + _expected.json
  → Docker 沙箱验证（strace + LLM judge）
  → 通过→benchmark / 失败→反馈重试（≤3次）
```

### 方法 B：构造性注入矩阵（全自动，部分开源）

| 项目 | SkillTrustBench |
|---|---|
| **来源** | 腾讯朱雀实验室 × CUHK-SZ |
| **官网** | https://matrix.tencent.com/skilltrustbench/ |
| **HF dataset** | https://huggingface.co/datasets/cuhk-zhuque/SkillTrustBench |
| **Leaderboard** | https://huggingface.co/spaces/cuhk-zhuque/SkillTrustBench-Leaderboard |
| **开源内容** | ✅ 数据集（5520 样本）+ leaderboard；❌ 无生成管线代码 |
| **seed** | 9 攻击类别（T01-T09）× 5 依赖层（A-E）= 45 格 |
| **规模** | 5,520（95.6% 合成 + 242 wild） |
| **标签** | 三值：malicious / suspicious / normal |

### 方法 C：注入向量分类（半自动，开源）

| 项目 | SkillInject |
|---|---|
| **论文** | arXiv:2602.20156 |
| **GitHub** | https://github.com/aisa-group/skill-inject |
| **seed** | 4 轴：注入明显性（obvious/contextual）× 通道（body/script/YAML）× 能力分级 × 8 类攻击目的 |
| **规模** | 202 injection-task pairs |
| **自动化** | 半自动——手动设计注入模板 + 策略条件测试 |

### 方法 D：红队插件目录（手动，开源）

| 项目 | Promptfoo |
|---|---|
| **GitHub** | https://github.com/promptfoo/promptfoo |
| **seed** | 5 风险领域 × 86 插件（安全/隐私/刑事/有害/虚假信息） |
| **自动化** | 手动——人工写 86 个对抗 prompt 插件 |
| **备注** | 非 taxonomy 驱动（按危害主题），通用红队工具 |

### 方法 E：场景构造 + verifier（半自动，开源）

| 项目 | SkillSafetyBench |
|---|---|
| **论文** | arXiv:2605.12015 |
| **GitHub** | https://github.com/AI45Lab/skill-safety-bench |
| **seed** | 6 风险域 × 30 安全类别 |
| **规模** | 155 对抗用例 / 47 任务 |
| **自动化** | 半自动——构造场景 + case-specific verifier |
| **备注** | 测 agent 非 skill |

### 方法 F：git commit 恢复（自动，非构造）

| 项目 | MalSkills |
|---|---|
| **论文** | arXiv:2603.27204 |
| **方法** | 从公开恶意事件（ClawHavoc/Snyk）→ ClawHub git 历史 → 恢复已删除恶意 skill → 哈希去重 |
| **规模** | 100 确认恶意 |
| **自动化** | 自动恢复，非构造 |
| **备注** | 真实恶意锚候选 |

### 补充：公开恶意 skill 仓库（真实样本）

| 仓库 | 链接 | 说明 |
|---|---|---|
| **PiedPiper0709/openclaw-malicious-skills** | https://github.com/PiedPiper0709/openclaw-malicious-skills | MalSkills 论文引用的公开恶意 skill 仓库 |
| **Trail of Bits overtly-malicious-skills** | https://github.com/trailofbits/overtly-malicious-skills | Trail of Bits 维护的公开恶意 skill 样本 |
| MalSkillBench wild 703 | https://github.com/lxyeternal/MalSkillBench (`Dataset/Skills/malware/<name>/`) | ClawHavoc 战役 + 其他真实恶意 |

---

## 三、各方法对比总表

| 方法 | 论文 | 自动化 | seed 类型 | 规模 | 开源 | 验证方式 | 能否用我们 taxonomy |
|---|---|---|---|---|---|---|---|
| **A. LLM 合成** | MalSkillBench | 全自动 | 108 格 taxonomy | 3,214 | ✅ 全开源（生成+验证+数据） | Docker 沙箱 + LLM judge | ⭐ 替换 taxonomy 定义即可 |
| **B. 注入矩阵** | SkillTrustBench | 全自动 | 45 格矩阵 | 5,207 | ⚠️ 数据开源，代码不开源 | 构造即标签 | ⚠️ 无生成代码可复用 |
| **C. 注入向量** | SkillInject | 半自动 | 4 轴分类 | 202 | ✅ 开源 | 策略条件测试 | ⚠️ 4 轴混了我们多个维度 |
| **D. 红队插件** | Promptfoo | 手动 | 86 插件 | — | ✅ 开源 | — | ❌ 非 taxonomy 驱动 |
| **E. 场景构造** | SkillSafetyBench | 半自动 | 6 域×30 类 | 155 | ✅ 开源 | case-specific verifier | ❌ 测 agent 非 skill |
| **F. git 恢复** | MalSkills | 自动 | 无 seed | 100 | ❌ | 哈希去重 | ❌ 非构造（恢复真实） |

---

## 四、对我们 SoK 论文的建议

### 真实恶意锚
- **主力**：MalSkillBench wild 703（真实、已验证、与我们零重叠）
- **补充**：PiedPiper0709 + Trail of Bits 仓库（公开恶意样本，可交叉验证）

### 构造（S5 评测配套）
- **复用 MalSkillBench pipeline**（方法 A）：替换 `Core/taxonomy/` 为我们的三维坐标
- **规模**：~50-80 个样本（20-30 关键坐标 × 2-3 变体）
- **工程量**：2 周（改 taxonomy 定义 2 天 + 生成验证 3-5 天 + S5 评测 2 天）

### 不需要自己写的
- Docker 沙箱验证（MalSkillBench `Core/verification/` 已开源）
- 知识检索（IntelliGraph + WildJailbreak 已开源）
- 良性壳池（我们 1082 个真实 skill 可用）
