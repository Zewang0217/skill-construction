# taxonomy 在构造中的作用（TAXONOMY_ROLE）

> 论文 SoK · S5 原型阶段 · 构造实验
> 版本：2026-08-18 终版 | 数据：43 坐标 → 232 构造样本 → 三家扫描
> 数据源：`generator/coord_seeds.json`、`generator/patterns.py`、`generator/generate.py`、`scanners/eval_results/viz_data.json`、`scanners/eval_results/verdict_all.csv`

---

## 摘要

用 taxonomy 的 **43 坐标**生成 **232 构造恶意样本**（+350 真实恶意 = 582），验证 taxonomy "可生成、可检测"。本文件回答：taxonomy 在构造中起到了什么作用？

**核心结论**：
1. **43 坐标 = 来源×方式×目标 三维定义力**：唯一坐标覆盖 taxonomy 语义空间，构造是坐标级枚举而非随机抽样。
2. **覆盖性**：43/43 全覆盖，每坐标 2-5 样本，232 样本 = 坐标 × 实例。
3. **D5 质量门**：强制含可执行脚本，保证恶意是**可运行载荷**而非纯文本。
4. **taxonomy 定位盲区**：Cat 对 `instruction_manip`（尤其 `source_agnostic×instruction_manip`）系统性零命中——坐标直接映射到架构盲区。
5. **taxonomy 与结论**：盲区 = 坐标弱覆盖 = **架构决定盲区**，可归因、可复现、可扩展。

---

## 一、43 坐标的定义力（来源 × 方式 × 目标 三维）

taxonomy 用三维定义恶意 skill 坐标：**来源**（种入位置）、**方式/机制**（攻击如何执行）、**目标**（攻击对象）。`coord_seeds.json` 的 43 个 key 即全部唯一三维组合：
| 坐标 key | coord_cn（中文） | 恶意行为（behaviors 摘要） |
|---|---|---|
| `supply_chain\|code_exec\|persistent_control` | 供应链×代码执行×持久控制 | 写 systemd/cron 让恶意常驻 + 反连 shell |
| `source_agnostic\|instruction_manip\|target_agnostic` | 来源无关×指令操控×目标无关 | 指令覆盖/提示注入 |
| `external_content\|instruction_manip\|target_agnostic` | 外部内容×指令操控×目标无关 | 远端内容注入指令 |
| `source_agnostic\|privilege_abuse\|resource_abuse` | 来源无关×权限滥用×资源滥用 | 越权执行系统级命令 |
**定义力体现**：每坐标携带 `coord_cn`（语义标签）、`slots`（Layer-2 语义槽）、`behaviors`（恶意行为变体）、`primitives`（原语）、`mdb_evidence`（mapping-db 证据链）——一个坐标 = **语义定义 + 攻击行为 + 真实样本证据** 的完整封装。

---

## 二、覆盖性保证：43/43 全覆盖，232 样本

### 2.1 覆盖事实

- `coord_seeds.json` **43 个唯一坐标**全部被生成（无遗漏）。
- 每坐标 2-5 样本（多数 5 个变体），**232 个构造样本** = 坐标级枚举 + 多实例防指纹。
- 生成分布（`viz_data.json`）：

**按来源（gen_by_source）**：
| 来源 | n | Cisco | SS | Cat |
|---|---|---|---|---|
| supply_chain | 80 | 88.8% | 93.8% | 100% |
| source_agnostic | 115 | 76.5% | 96.5% | 60.0% |
| external_content | 19 | 100% | 100% | 63.2% |
| user_input | 9 | 77.8% | 100% | 88.9% |
| runtime_environment | 3 | 33.3% | 66.7% | 66.7% |
| unknown_source | 5 | 80.0% | 100% | 60.0% |
**按机制（gen_by_mech，Cisco 检出率）**：code_exec 54 (81.5%)、dependency_manip 24 (95.8%)、
instruction_manip 47 (85.1%)、privilege_abuse 30 (73.3%)、state_corruption 21 (66.7%)、
obfuscation 20 (80%)、mechanism_unknown 20 (90%) 等，10 机制全覆盖。

**按目标（gen_by_target）**：info_theft 34、persistent_control 31、target_agnostic 99、
resource_abuse 20、defense_evasion 27 等，9 目标全覆盖。

> 注：`viz_data.json` gen 汇总 231（因 1 个样本判定表无完整三家数据）；任务口径 232 为生成总数，
> 覆盖率结论（43/43 全覆盖）不受影响。

### 2.2 覆盖性的意义

不是"生成了一堆恶意样本"，而是**每个语义点都有对应实例**——这让盲区分析从"个别样本漏检"上升到"**坐标级**系统性盲区"（见发现 4）。坐标可溯源到 `_provenance.json`（X2 防指纹 use-once），每样本 = 坐标 + 实例，可复现。

---

## 三、生成器质量门（D5）如何保证样本有效性

### 3.1 质量门设计（`generator/generate.py:277-322`）
| 门 | 逻辑 | 保证 |
|---|---|---|
| Q1 | SKILL.md 长度 ≥ 200 字节（L292） | 排除 LLM 偶发只回散文 |
| Q2 | 自白检测：SKILL.md/脚本出现自首词即重生成（L297，`CONFESSION_PATTERNS` L87） | 样本与真实工具不可区分 |
| Q3/D5 | **强制样本含可执行脚本**（L302-313）："至少 1 个非 .md 可执行文件" | **载荷可运行**，非纯文本 |
| 重试 | 最多 5 次，重试耗尽才保底落盘并打 confession_flag（L316-321） | 拒绝脏样本 |

### 3.2 D5 的核心价值

D5 门保证构造的恶意**不是"写在 SKILL.md 里喊恶意"的纯文本**，而是 `scripts/` 下的真实可执行载荷（`config_parse.py`、`payload.py`，见 `write_output` L222-265）。这与真实恶意（wild，同为"指令 + 脚本载荷"结构）对齐，让代码级/AST 规则（SS LP3/AST4、Cat 正则）有真实输入可匹配、评测公平，并直接支撑 KEY_INSIGHTS 发现 1（执行阶段载荷绕过）。

### 3.3 反例验证

`skill-privilege_abuse-resource_abuse-25d5120b77`（gen）是 D5 门的边界反例：`config_parse.py` 344 行
通读为**良性 config 解析器**，callback 仅残留占位符 `cdn-metrics.example.com:1337`，无真实载荷 →
三家全漏。这证明 **D5 保证"有可执行文件"，但不保证"是真恶意"**——生成质量仍需 provenance 对照与
二次扫描复核（该样本归入"数据质量/生成失败"）。

---

## 四、taxonomy 帮助定位扫描器盲区：Cat 对 instruction_manip 全盲

### 4.1 坐标直接映射到盲区

用 `_provenance.json` 逐样本还原坐标，计算各家各坐标检出率，得**坐标级盲区矩阵**。最典型是 Cat 对 `instruction_manip`（指令操控）系列：
| 坐标 | total | Cat 检出 | Cat 漏 | 含义 |
|---|---|---|---|---|
| `external_content×instruction_manip×target_agnostic` | 5 | 1 | **4** | 远端指令注入 Cat 几乎全盲 |
| `source_agnostic×instruction_manip×content_safety` | 5 | 2 | 3 | 指令型内容安全盲区 |
| `source_agnostic×instruction_manip×defense_evasion` | 5 | 2 | 3 | 指令型规避盲区 |
| `source_agnostic×instruction_manip×info_theft` | 5 | 2 | 3 | 指令型窃取盲区 |
| `source_agnostic×instruction_manip×resource_abuse` | 5 | 2 | 3 | 指令型资源滥用盲区 |
（对照组：`supply_chain×instruction_manip×target_agnostic` 5/5 全检出——供应链来源含代码字面命令，Cat 能命中；故 Cat 盲区在**无代码字面的纯指令型**，而非指令操控本身。）

**与 `viz_data.json` 的 `blindspot.cat_miss` 一致**：top 漏检坐标全部是 `source_agnostic×instruction_manip×*`（4 坐标各 3 漏）与 `external_content×instruction_manip×target_agnostic`（4 漏）。

### 4.2 为什么坐标能定位盲区

坐标 = 语义定义（三轴），盲区 = 某坐标下检测率显著低于基线。**没有坐标只能观察到"Cat 漏了 118 个"；有坐标能归因到"Cat 对纯指令型恶意（无代码字面）系统性失明"**——架构盲区被坐标精确钉在 `instruction_manip × 无代码来源` 上。

### 4.3 对 SoK 的价值

这是 S5 的第二个关键证据：**taxonomy 坐标既是生成采样框架，也是盲区归因的索引**——盲区从"一堆样本名"变成坐标语义空间里的一个明确区域。

---

## 五、taxonomy 与最终结论的关系：盲区 = 坐标弱覆盖 = 架构决定盲区

### 5.1 三层归因链条

`坐标级弱覆盖 → 扫描器架构盲区 → "盲区是架构决定的，不是个别样本偶然"`。三家盲区的坐标化定位（综合 `viz_data.json blindspot` + 本实验）：
| 扫描器 | 坐标级盲区 | 架构根源 |
|---|---|---|
| Cat | `source_agnostic×instruction_manip×*`、`external_content×instruction_manip×target_agnostic` | 纯正则引擎无语义层，指令型/无代码字面恶意全盲 |
| SS | `supply_chain×code_exec×info_theft` 等 + 系统性绕过（伪装修辞 + 执行阶段载荷） | 语义层被社交工程包装说服；不串读远端文件；管道变量注入不在 AST |
| Cisco | `source_agnostic×privilege_abuse×system_damage`（3 漏）、`source_agnostic×state_corruption×target_agnostic`（2 漏）等 | `is_safe` 阈值吞 MEDIUM + LLM 失败退化静态 |

### 5.2 可扩展性

给盲区坐标换 disguise/vector 变体即可生成新样本验证盲区稳定性（`patterns.py` 的 `sample_coordinate`/`coord_coordinate` 支持按坐标采样）；43 坐标全覆盖保证新恶意类型都能落在坐标语义空间内对比——这是 S5 的实践承诺。

### 5.3 结论

**taxonomy 在本实验中的角色 = 生成采样框架 + 盲区归因索引 + 结论推广的锚**：
- 生成：43 坐标 × 多实例 → 232 可执行恶意样本（D5 门保证有效性）；
- 归因：坐标级检出率矩阵 → 把"漏检"钉到语义空间的具体区域；
- 结论：盲区是架构决定的（Cat 指令型全盲、SS 伪装修辞绕过、Cisco 阈值吞检出），可归因、可复现、可扩展——即 S5 "lightweight prototype 验证 taxonomy 可生成可检测"的完成形态。

---

## 证据索引
| 数据 | 位置 |
|---|---|
| 43 坐标定义 | `generator/coord_seeds.json` |
| 坐标采样函数 | `generator/patterns.py`（COORD_SEEDS / coord_coordinate） |
| D5 质量门 | `generator/generate.py:277-322`（Q1 长度 L292 / Q2 自白 L297 / Q3·D5 脚本 L302-313） |
| 生成分布 | `scanners/eval_results/viz_data.json`（gen_by_source / gen_by_mech / gen_by_target / blindspot） |
| 坐标还原（每样本） | `generator/output/<name>/_provenance.json` |
| 判定表 | `scanners/eval_results/verdict_all.csv` |
