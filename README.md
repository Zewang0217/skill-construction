# skill-construction

**恶意 Agent Skill 构建 + 扫描器评测工作区** — Agent Skill 安全 SoK 论文的 S5（轻量原型）配套工具。

> ⚠️ **WARNING**: 本仓库含**模拟恶意 skill 样本**和**真实恶意 skill 副本**，仅供安全研究用途。请勿安装或执行任何样本。

---

## 这是什么

本仓库是 Agent Skill 安全 SoK 论文的实验工作区，包含三个核心模块：

1. **Generator** — 坐标驱动的 LLM 恶意 skill 生成器（三维 taxonomy → DeepSeek → 伪装 skill 包）
2. **Scanners** — 三家开源扫描器适配 + 横向评测 pipeline
3. **Wild Samples** — 14 个代表性真实恶意 skill（来自 MalSkillBench + Trail of Bits）

核心工作流：

```
generator/（三维坐标 → LLM 生成恶意 skill）
   ↓ SKILL.md + scripts/ + _provenance.json
scanners/eval_all.py（3 家扫描器批量评测）
   ↓ verdict.csv（各家检出/漏检对比）
eval_results/ANALYSIS.md（分歧/盲区分析）
```

---

## 目录结构

```
skill-construction/
├── generator/                  # 恶意 skill 生成器
│   ├── config.py               # DeepSeek LLM 配置
│   ├── patterns.py             # 三维 taxonomy 种子库 (source×5 × mechanism×9 × target×8)
│   ├── generate.py             # 核心生成逻辑 + 质量门（自白检测/长度门/重试）
│   ├── llm.py                  # DeepSeek 客户端 + 输出解析
│   └── output/                 # 33 个已生成样本（每个含 SKILL.md + scripts/ + _provenance.json）
│
├── scanners/                   # 扫描器评测
│   ├── eval_all.py             # 批量评测脚本（3 家扫描器 × N 样本）
│   ├── eval_set/               # 评测集（real/ 真实 + generated/ 生成）
│   ├── eval_results/           # 评测结果（verdict.csv + ANALYSIS.md）
│   └── SELECTION.md            # 扫描器选型与安装记录
│
├── wild-samples/               # 14 个真实恶意 skill（MalSkillBench + Trail of Bits）
│   └── README.md               # 选样清单 + 三维坐标映射
│
├── MALICIOUS_SKILLS_CATALOG.md # 公开恶意 skill 数据集收录清单（含 URL）
├── RESOURCES.md                # 恶意 skill 资源清单（真实样本 + 构建方法）
├── CONSTRUCTION_METHODS.md     # 构建方法调研报告
├── WILD_EVIDENCE_AND_METHODS.md # ClawHavoc 真实样本验证 + 构建方法全景
└── PIPELINE_OVERVIEW.html      # 架构可视化（单页 HTML，浏览器直接打开）
```

---

## Generator — 恶意 Skill 生成器

### 原理

把论文的三维 taxonomy 当种子坐标，驱动 LLM 合成伪装成良性工具、但内藏真实恶意行为的 skill 包。

**三维坐标**：
- **来源 source (5)**：supply_chain / source_agnostic / external_content / user_input / runtime_environment
- **方式 mechanism (9)**：code_exec / dependency_manip / instruction_manip / privilege_abuse / obfuscation / state_corruption / trigger_abuse / subagent_escalation / defense_evasion
- **目标 target (8)**：info_theft / resource_abuse / persistent_control / defense_evasion / financial_theft / system_damage / content_safety / target_agnostic

### 关键设计决策

| 设计 | 说明 |
|---|---|
| **中性回调占位符** | `cdn-metrics.example.com:1337`（RFC 2606 保留域名不可达）→ 样本不会变成真实攻击工具 |
| **自白禁令（40 词）** | SKILL.md 和脚本中严禁出现"恶意/攻击/载荷/投毒"等词，强制产物与真实工具不可区分 |
| **use-once 唯一目录** | 同坐标重复生成加 `__v2` 后缀，不覆盖旧样本 |
| **ground truth 排除** | `_copy_tree()` 拷贝时过滤 `_provenance.json`，防 LLM 扫描器读 label 泄密 |
| **纯静态生成** | 只产出静态文件，不对接任何沙箱执行 |

### 使用

```bash
# 配置 API key
export DEEPSEEK_API_KEY=sk-xxx

# 单坐标生成
python generator/generate.py single --source supply_chain --mechanism code_exec --target info_theft

# 随机生成
python generator/generate.py random --n 5

# 按 Layer-2 槽位生成
python generator/generate.py slot --slot C02-γ
```

---

## Scanners — 三家开源扫描器评测

### 选定的扫描器

本仓库使用三家**开源**扫描器进行横向评测。这三家代表了完全不同的检测范式：

| Scanner | 仓库 | 许可证 | 检测范式 | 版本 |
|---|---|---|---|---|
| **Cisco skill-scanner** | [cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) | **Apache-2.0** | 多引擎（静态 + LLM + bytecode + pipeline + BEHAVIORAL dataflow） | v2.0.13 |
| **NVIDIA SkillSpector** | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | **Apache-2.0** | 17 类语义（静态正则 + AST + YARA + LLM + OSV.dev） | v2.9.3 |
| **Caterpillar (offline)** | [alice-dot-io/caterpillar](https://github.com/alice-dot-io/caterpillar) | **MIT** | 纯正则 16 条（零语义，最弱触发面基线） | v1.0.11 |

### 未修改声明

**三家扫描器均使用上游官方版本，未做任何源码改动。** 评测脚本 `eval_all.py` 仅通过 CLI 调用，不修改扫描器本身：

| Scanner | 调用方式 | 改动 |
|---|---|---|
| Cisco | `skill-scanner scan <dir> --use-llm --format json` | ❌ 无，pip 官方包 |
| SkillSpector | `python -m skillspector_batch.batch_scan`（上游 `contrib/batch_scan` 官方模块） | ❌ 无，通过环境变量传 deepseek key |
| Caterpillar | `caterpillar ask <dir> --mode offline --json` | ❌ 无，offline 模式免改（openai 模式需 fork，未使用） |

> **为什么不含扫描器源码**：三家扫描器均为开源第三方项目（Apache-2.0 / MIT）。本仓库不复制它们的源码，仅通过 `pip install` / `npm install` 安装后用 CLI 调用。这样避免了 fork 维护负担和版权混淆——评测结果可复现，且始终使用扫描器的最新官方版本。

### 许可证与安装

三家扫描器均允许学术研究和 redistribution：

```bash
# Cisco (Apache-2.0)
pip install skill-scanner

# SkillSpector (Apache-2.0)
pip install skillspector
# batch_scan 是上游 contrib/batch_scan 模块，随 pip 包一起安装

# Caterpillar (MIT)
npm install -g @alice-io/caterpillar
```

### 运行评测

```bash
export DEEPSEEK_API_KEY=sk-xxx  # Cisco/SkillSpector 的 LLM 后端
python scanners/eval_all.py
```

### 横评结果（6 样本：2 真实 + 4 生成）

6/6 全部被三家扫描器检出。关键发现：**供应链明文 RCE 对三家不是盲区**；真正的盲区在 external_content / user_input / runtime / compositional 通道。

详见 `scanners/eval_results/ANALYSIS.md` 和可视化 [`PIPELINE_OVERVIEW.html`](PIPELINE_OVERVIEW.html)（图 3 + 图 4）。

---

## Wild Samples — 真实恶意 Skill

14 个代表性样本，覆盖 5 mechanism × 5 target × 2 source。详见 `wild-samples/README.md`。

数据来源和完整收录清单见 `MALICIOUS_SKILLS_CATALOG.md`。

---

## ⚠️ 安全声明

- 本仓库所有恶意 skill 样本（生成的和真实的）**仅供安全研究用途**
- 生成样本的回调地址一律使用 `cdn-metrics.example.com:1337`（RFC 2606 保留域名，不可达）
- **请勿安装、执行或将这些样本部署到任何生产环境**
- Wild samples 来自公开数据集（MalSkillBench、Trail of Bits），版权归原仓库所有

---

## License

本仓库自有代码采用 **MIT** 许可证。

第三方扫描器版权归各自所有（见上表）。Wild samples 版权归原数据集所有。

---

## 相关论文

- MalSkillBench: A Runtime-Verified Benchmark of Malicious Agent Skills — [arXiv:2606.07131](https://arxiv.org/abs/2606.07131)
- Trail of Bits: [The Sorry State of Skill Distribution](https://blog.trailofbits.com/2026/06/03/the-sorry-state-of-skill-distribution/)
