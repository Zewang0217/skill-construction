# 隐藏文件载荷实验（ARM7）：扫描器结构性盲区

> 版本：2026-08-19 | 样本：5（Arm7 隐藏文件载荷）× 3 扫描器
> 后端：ecnu-max | 数据：`scanners/eval_results/verdict_arm7.csv`、`arm7_raw/`、`arm7_sp_raw/`
> **结论：三家对隐藏文件载荷 4/5 真漏检——扫描器文件收集逻辑的结构性盲区，非随机。**

---

## 1. 动机：从扫描器本身找攻击面（用户方向）

前六个 arm 实验（Arm1-6）聚焦"恶意如何构造"，但 SS/Cisco 难绕的根因逐渐清晰：
**扫描器按自己的文件收集逻辑决定分析面**。若恶意位于扫描器不收集的文件，则语义/规则
引擎根本看不到——这是比"构造技巧"更根本的攻击面。

对 SS 源码（`skillspector/nodes/build_context.py:133-186`）的分析发现：
- `.env`/`.bashrc`/`.aws/credentials` 等 `.` 开头文件被 `_walk_skill_files` **直接跳过**
  （`if filename.startswith(".") and not filename.startswith(".claude"): continue`）
- 跳过目录：`.git`/`__pycache__`/`node_modules`/`.venv`/`venv`/`.tox`/`.pytest_cache`
- 单文件 >1MB 跳过（`MAX_FILE_BYTES`）
- OMS 签名文件（`skill.oms.sig`）排除出分析

## 2. 实验设计

构造 5 个"隐藏文件载荷"样本：恶意（凭证窃取/SSH 收集/持久化/敏感配置外发/缓存收集）
**只放在隐藏文件**（`.env`/`.ssh-check`/`.profile`/`.gitconfig`/`.cache-config`），
SKILL.md 为干净的正常工具描述（引用"配置文件"但不写恶意）。质量门验证：
- SKILL.md 5/5 无自白词、frontmatter 通过
- 隐藏文件 5/5 含恶意原语（curl/urllib/base64/subprocess）

## 3. 结果

| 扫描器 | 检出率 | 真漏检 | 技术失败 | 说明 |
|---|---|---|---|---|
| **Cisco** | **0/5** | **4** | 1 | LLM 只看到干净 SKILL.md 判安全 |
| **SS** | 1/5 | **4** | 0 | components 实证只含 SKILL.md |
| **Cat** | 1/5 | **4** | 0 | .env 的 curl 字面仅 1 例命中 |

**SS components 铁证**（raw 检查）：

| 样本 | SS components | score |
|---|---|---|
| arm7-01 env-creds | `['SKILL.md']` | 0 |
| arm7-02 ssh-collect | `['SKILL.md']` | 0 |
| arm7-03 persist | `['SKILL.md', 'startup-manager']` | 73（非隐藏文件泄漏）|
| arm7-04 git-secret | `['SKILL.md']` | 0 |
| arm7-05 cache-dump | `['SKILL.md']` | 0 |

arm7-03 检出是因为存在非隐藏的 `startup-manager/` 目录进了 components（SDI 从那里取证），
其余 4 个隐藏文件载荷完全不可见。

**Cisco 验证**：4 个漏检 `LLM_FAILED=False`（LLM 正常分析但判安全）——真漏检，
非技术失败。Cisco 语义推理再强，也看不到分析范围外的文件。

## 4. 三家漏检的机制对比

| 扫描器 | 隐藏文件处理 | 漏检机制 |
|---|---|---|
| SS | `_walk_skill_files` 跳过 `.` 文件 | 隐藏文件不在 components |
| Cisco | 文件收集类似（跳过隐藏）| LLM 只分析收集到的文件 |
| Cat | 扫原目录但正则只在 SKILL.md/可见文件匹配 | .env 的 curl 字面仅 1 例被正则命中 |

**三家盲区同源**：文件收集逻辑排除隐藏文件 → 恶意藏匿其中 → 所有引擎失明。
这是**架构级盲区**（文件收集层），比 Arm1 的原语级盲区更根本。

## 5. 与 Arm1-6 的关系

| 实验 | 盲区类型 | 稳定性 |
|---|---|---|
| Arm1 | 原语级（Cat 无字面命令/Cisco 间接执行）| 稳定（#06-09 复现）|
| Arm3 | 载荷时序（SS 无脚本+变量注入）| 单样本（arm3-02）|
| Arm4 | 代码规避 | SS 免疫 |
| Arm5 | 声明注入 | SS 反效果（SDI）|
| Arm6 | 描述一致性+变量注入 | SS 免疫（SDI 从代码取证）|
| **Arm7** | **文件收集级（隐藏文件）** | **三家 4/5 稳定漏** |

**Arm7 是首个三家同时稳定绕过的攻击面**，且机制是"扫描器自身设计"而非"攻击构造技巧"。

## 6. 局限与下一步

1. **样本量**：5 个，需扩样（10-15）验证稳定性
2. **真实攻击验证**：隐藏文件载荷是否真实可执行（`.env` 内容被 agent 读取执行的前提）
3. **混合攻击**：隐藏文件 + 间接执行（叠加 Cisco 两个盲区）效果如何
4. **SS prompt 注入**：SKILL.md 针对 SS LLM 的注入（"忽略配置文件"）是否增强绕过
5. **剥离版**：盲测分发前必须剥离目录名 arm 前缀 + `_provenance.json`

## 7. 证据索引

- 判定表：`scanners/eval_results/verdict_arm7.csv`
- Cisco raw：`scanners/eval_results/arm7_raw/cisco/`
- SS raw：`scanners/eval_results/arm7_sp_raw/`
- 样本：`generator/output/arm7-*/`
- SS 源码证据：`scanners/.venv/.../skillspector/nodes/build_context.py:133-186`
