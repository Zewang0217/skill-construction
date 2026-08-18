# Skill Construction（构造实验）领域词汇表

Agent Skill 安全 SoK 的 S5 原型构造实验的共享语言。核心对象是"恶意 agent skill"及对其的
检测、生成、评测。

## 恶意样本

**Skill**:
一个 agent 可加载的技能包，核心是 `SKILL.md`（YAML frontmatter + Markdown 指令），可附带
`scripts/` 等可执行代码。本文档语境下"skill"专指 agent skill（Claude Skills / MCP 生态），
非通用编程库。
_Avoid_: 插件、工具、技能包（泛称）

**Wild 样本**:
来自真实生态（clawhub 等）的真实恶意/良性 skill，带 MalSkillBench 的 B1-B15 行为标签。
真实攻击的"包装"（免责话术、工具伪装）只存在于 wild。
_Avoid_: 真实样本、线上样本（同义，本文档统一用 wild）

**构造样本（gen）**:
由生成器按 taxonomy 坐标（来源×方式×目标）生成的恶意 skill。坐标语义来自 taxonomy，
行为来自 mapping-db evidence（159 条）与手写 seeds。当前 232 个，43 坐标全覆盖。
_Avoid_: 合成样本、生成样本（同义，统一 gen）

**直白版（plain）**:
无包装的构造样本——恶意意图在 seed/代码中直接可见。对应"扫描器最易检出"。
_Avoid_: 裸样本

**包装版（wrapped）**:
带语义包装的构造样本——在攻击内容不变的前提下，通过免责话术、工具伪装、代码字面规避等
手段隐藏恶意意图，目标是对抗扫描器检出。与"直白版"是深挖实验的对照臂。
_Avoid_: 伪装样本（包装是研究变量，伪装是其中一种手法）

## Taxonomy 与坐标

**坐标（coordinate）**:
taxonomy 的三维组合（来源 source × 方式 mechanism × 目标 target），如
`source_agnostic × code_exec × info_theft`。43 个唯一坐标覆盖全部威胁类别。
_Avoid_: 槽位（slot，是 19 个精选手写坐标，粒度不同）

**来源（source）**:
恶意指令/载荷的注入来源（supply_chain / source_agnostic / external_content / user_input /
runtime_environment / unknown_source）。
_Avoid_: 渠道、通道

**方式（mechanism）**:
恶意实现手段（code_exec / instruction_manip / dependency_manip / privilege_abuse /
obfuscation / state_corruption / trigger_abuse / subagent_escalation / defense_evasion /
mechanism_unknown）。
_Avoid_: 手段、手法（同义，统一 mechanism）

**目标（target）**:
恶意行为的作用对象（info_theft / resource_abuse / persistent_control / defense_evasion /
financial_theft / system_damage / content_safety / target_agnostic）。
_Avoid_: 目的

**原语（primitive）**:
同一坐标内具体的攻击技术变体。如 code_exec 坐标下的 exec() / eval() / subprocess /
os.system / getattr 反射 / 动态 require 等。mdb_evidence 记录原语级证据。
_Avoid_: 攻击方式（与 mechanism 混淆）

## 检测与评测

**技术失败**:
扫描器因自身或输入原因未产出判定（Cisco 加载失败 17 / SS LLM 失败 10）。分两类：
skill 导致的（畸形 skill 使扫描器失效，是攻击面）与 LLM/随机失效（应剔除）。
_Avoid_: 漏检（技术失败不是漏检，是评测盲区）

**真实语义漏检（真漏检）**:
扫描器正常执行但判安全/零命中，且其他扫描器检出了该恶意。评测核心对象。
_Avoid_: 假阴性（同义，本文档统一真漏检）

**包装复杂度**:
恶意意图的暴露程度维度（直白 → 免责话术 → 工具伪装 → 代码规避 → 无代码载荷）。
实证显示该维度决定 SS 检出率（直白 94-100% vs wild 高价值目标 58-72%），
而坐标本身不决定。
_Avoid_: 暴露度、混淆程度（混淆只是其中一层）

**盲区（blindspot）**:
某类恶意在正常执行下系统性逃过某扫描器。按层分类：坐标级（Cat 对纯指令型）、
包装级（SS 对包装型）、阈值级（Cisco 吞 MEDIUM）、格式级（Cisco 对畸形 skill）。
_Avoid_: 漏检（盲区是系统性的能力边界，漏检是单样本事件）

## 生成与质量

**mdb_evidence**:
mapping-db（威胁→检测规则映射库）清洗出的原语级攻击证据，159 条，43 坐标中 39 个非空。
是坐标内深挖的变体来源。
_Avoid_: examples、seeds（behaviors 是手写种子，evidence 是规则库来源，不同层）

**质量门（D5）**:
生成器的质量检查，要求样本含可执行脚本（非 .md 文件）。与无代码载荷坐标冲突——
调整原则：攻击方式决定是否需要脚本（code_exec 必须有，instruction_manip 不强求）。

**对抗包装（adversarial wrapping）**:
以真实扫描器检出反馈为信号，LLM 在攻击内容不变的前提下迭代优化语义包装，直到扫描器
不再检出的过程。替代"LLM 扮演检测者"的模拟方案。
_Avoid_: 红队模拟（模拟缺乏真实扫描器的规则/语义约束）

## 评测口径

**检出口径**:
三家各自的"检出"定义——Cisco = is_safe==False 或 MEDIUM+ 危险 finding（阈值修正后）；
SS = ss_score > 0；Cat = cp_n > 0。
_Avoid_: 原始 is_safe（Cisco 只认 HIGH/CRITICAL 会吞 80 个 MEDIUM 检出）

**平铺格式（flat）**:
SS 的批量输出格式（{score, severity, issues}），不记录 execution_successful /
failed_executions——"LLM 失败"与"判安全"外观不可区分。是 SS 评测盲区的根因。
_Avoid_: wrapped（含执行状态，需要逐样本解析）
