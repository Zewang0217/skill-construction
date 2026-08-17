# WEEK-7 任务书：500+ 恶意样本规模化评测（2026-08-16）

> 用途：本文件是本周全部任务的唯一权威记录。记忆压缩后凭此文件恢复全部上下文与步骤。
> 上一轮：week-6（2026-08-14 收官，四线并行完成：19 槽生成/19 真实/20 良性/扫描评测）

---

## 0. 本周目标

把恶意样本池从 53 个扩到 **500+（构造 200 + 真实 350）**，良性 500，完成三家扫描器全量评测，
产出论文可用的 TP/FP 完整矩阵。

## 1. 已拍板决策（勿改，除非用户重新决策）

| # | 决策 | 内容 |
|---|---|---|
| D1 | 构造覆盖单位 | **43 坐标 × 每坐标 2-4 样本**（≈86-172 个）。43 = source×mech×target 唯一坐标组合（s4-slots-full.csv 174 行去重）。83 是槽数（坐标内按检测信号细分），评测维度不是生成维度。 |
| D2 | behaviors 来源 | mapping-db evidence/notes 真实例子 + 现有 SLOT_SEEDS 手写行为 → 合并成模板库 |
| D3 | 服务器分工 | `/opt/skill-bench/` 独立目录（不碰 /opt 其他东西）：拉真实样本 + 三家扫描 + 报告落盘 |
| D4 | 真实样本分层 | MalSkillBench 官方 703 WILD，按 B1-B15 行为标签分层抽样 ~350（每行为 ~23 个）|
| D5 | 生成样本必须有脚本 | 每个生成样本必须含可执行脚本/文件（不能只有 SKILL.md 文本）|
| D6 | 槽位向量 | source/mechanism/target 均支持多值（用户既定）|
| D7 | 危险等级 | 先落盘不做（从扫描结果反推）|

## 2. 数据源与关键路径（已验证）

| 数据 | 位置/方式 | 状态 |
|---|---|---|
| MalSkillBench 官方划分清单 | `/tmp/malskill_splits.json`（GENERATED 3076 / WILD 703 / TEST 27，来自 `_source_inventory.txt`）| ✅ 已拉 |
| MalSkillBench 仓库 | `github.com/lxyeternal/MalSkillBench`，raw 路径 `Dataset/Skills/malware/<name>/SKILL.md` | ✅ 可拉 |
| mapping-db API | `http://117.72.100.212:3000/api/*`（3000 反代后端；**8001 外部不通**）| ✅ 已验 |
| mapping-db 全量 export | `GET /api/export/csv` → 172 条（168 threat），字段含 source_dim/mech_dim/target_dim/vuln_tags/carrier_tags/evidence/notes | ✅ 已拉 `/tmp/mdb_export.csv` |
| mapping-db 维度值 | `GET /api/dim-values` → 46 条（carrier 8 / mech 10 / source 6 / target 8 / vuln 14），带 examples/counter_examples/decision_rules | ✅ 已拉 `generator/dim_values.json` |
| mapping-db 统计 | `GET /api/stats` → 6 家分布（SS 90/Socket 29/Cisco 18/AARTS 14/Snyk 11/ATR 10）| ✅ 已拉 |
| 43 坐标清单 | 本地 `hermes-work/week-5/s4-slots-full.csv`（174 行）| ✅ 已确认 |
| 坐标可行性 | `hermes-work/week-5/COORDINATE_FEASIBILITY.csv`（400 行）| ✅ 已确认 |
| 服务器 | `ssh jdcloud`（Python 3.12 + Docker 29 + 18G 磁盘 + 2.9G 内存）| ✅ 已通 |
| 服务器现状 | docker: mapping-db 三容器(3000/8001/5432) + searxng + mihomo 等；**勿动** | ✅ 已查 |
| 扫描器 | 本地 `skill-construction/scanners/`：Cisco v2.0.13 / SkillSpector v2.9.3 / Caterpillar v1.0.11（均未修改）| ✅ |
| DEEPSEEK key | 本地 `generator/.env.deepseek.local`（真实 key `sk-eeb5c3...`）；**`.env.deepseek` 是占位符勿用** | ✅ |

## 3. 两条工作线（并行）

### 线 1（本地）：taxonomy 指导的恶意构造 200

**步骤**：
1. **坐标清单生成**：从 s4-slots-full.csv 提取 43 唯一坐标 → 每坐标补 behaviors（mapping-db evidence + SLOT_SEEDS）
2. **生成器改造**（generator/）：
   - `patterns.py` SLOT_SEEDS → 43 坐标驱动（保留下划线：模板组合而非全手写）
   - 坐标模板 = source 策略（5 注入面）× mech 骨架（10 行为）× target 动作（8 目的），`itertools.product` 生成
   - **D5 强制**：每样本必须含脚本文件（scripts/ 或内联代码块拆出），质量门检查"无脚本→重生成"
   - 每坐标 2-4 变体防指纹（LLM 从 behaviors 池随机选/组合）
3. **生成 200 样本**：`generate.py slot` 批量 + 自白质量门
4. **增量扫描**：生成一批 → 扫一批 → 结果进 `eval_results/slot_eval_clean.csv` 或新表
5. **产物**：200 构造恶意样本 + 评测表

**验收**：43 坐标全部有样本；每样本有脚本；自白率为 0；200 个全扫完

### 线 2（服务器）：真实恶意 350 扫描

**步骤**：
1. **建目录**：`/opt/skill-bench/`（独立，不碰 /opt 其他）
2. **部署扫描器**：从本地拷贝三个扫描器 + venv（或服务器重装）→ `/opt/skill-bench/scanners/`
3. **样本拉取**：脚本按 B1-B15 分层抽 350 WILD → `/opt/skill-bench/wild-350/`
   - B1-B15 行为 ID 在官方 `_source_inventory.txt` 每条 WILD 后带
   - 每行为均匀抽 ~23 个；跳过已测的（本地已有 19 个的对应）
4. **扫描 runner**：串行/并行（建议 4 路）跑三家 → `/opt/skill-bench/results/`（JSON + CSV）
   - 预计 350×3 = 1050 次扫描，4 路并行 ~7-15 小时
5. **报告落盘**：`verdict_wild350.csv` + raw JSON + 摘要 md

**验收**：350 样本全扫完，报告可下载回本地分析

## 4. 合并产物（两条线完成后）

- **500+ 恶意**（构造 200 + 真实 350）× 3 家 = 1500+ 次扫描的完整判定表
- **500 良性**（MalSkillBench benign 拉 500，补足现有 20）→ FP 基线
- 论文矩阵：TP/FP/F1 × 3 家 × (构造/真实/良性) 三组对照
- 已知待办顺带：moltpho 良性池剔除、X-UI-β 槽数据、D2 决策

## 5. 停机规则（沿用 week-6）

- scanner/pipeline 出错 → 停所有扫描，先修
- 定期抽样检查生成样本质量（自白/偏离槽位）
- 坏样本：重生成 ≤3 次，仍失败 → 记录 GENERATOR_FINDINGS 并标记 dropped

## 6. 风险

- **WSL 跨盘 I/O 慢**：本地 find/grep 全盘会超时 → 限定目录或走服务器
- **deepseek 速率限制**：8 路并行可能触发 → 保守 4 路
- **MalSkillBench raw 拉取失败**：样本名含空格/特殊字符 → urllib.parse.quote 处理（已验证可行）
- **mapping-db 数据版本**：83 槽基于 2026-08-13 export；构造以最新 export 为准（今天已拉）

## 7. 本文件配套

- `week-6/WEEK6_PIPELINE.md`：上轮完整记录
- `week-7/`：本周新增报告放这里
- `skill-construction/`：代码与数据（已 git 管理，每次里程碑 commit）

---

## 执行进度（2026-08-16 晚间）

### 已完成
- ✅ 43 坐标提取（s4-slots → coords43.json）
- ✅ behaviors 模板库（mdb evidence 清洗 + ATTACK_SEEDS + 手写 = 211 条，43 坐标全覆盖）
- ✅ 生成器改造：coord 子命令 + COORD_SEEDS 加载 + D5 强制脚本门（强化：非 .md 可执行文件）
- ✅ batch_generate.py（断点续跑 + 进度落盘 + 失败记录）
- ✅ 服务器 /opt/skill-bench 建好（scanners/wild-350/results/scripts）
- ✅ 三家扫描器部署（Cisco venv + SS + caterpillar npm）——**踩坑记录见下**
- ✅ 350 真实样本分层拉取（非 B4 全 94 + B4 抽 256 = 350，0 失败）
- ✅ 服务器 3 路并行扫描启动（shard 0/1/2，resume 模式）

### 服务器部署踩坑（重要，供后续参考）
1. **ssh 限速**：连续 ssh 会 Connection reset——间隔 30-60s，合并操作到少次数大连接
2. **模型名变更**：deepseek API 现在只有 v4-flash/v4-pro，deepseek-chat 是别名（chat/completions 仍通）；
   **Cisco skill-scanner 用 deepseek-chat 会 LLM_ANALYSIS_FAILED** → 必须显式 deepseek-v4-flash
3. **.so 缺失链**：rsync 排除 *.so 导致 litellm 链断裂（pydantic_core→tiktoken→fastuuid→cryptography→numpy.libs）——
   逐个补太慢，**最终全量 tar .so 传（75MB + numpy.libs 7.5MB）一次解决**
4. **skillspector_batch 模块**：在 scanners/ 目录（非 site-packages），首次 rsync 断连漏传 → 补传
5. **caterpillar 是 npm 包**（@alice-io/caterpillar@1.0.11），不是 pip！sudo npm install -g
6. **skill-scanner 正常判定**：LLM_ANALYSIS_FAILED 消失 + findings 含 LLM_* 规则 = LLM 生效

### 进行中
- 本地生成：176/215 样本（43 坐标，~26 完成）
- 服务器扫描：3 路并行 350 样本（~4-5 小时）
- 待办：2 个坏样本重生成（external_content 坐标，纯 references 无代码）、batch 完成后清理

### 关键路径（再次确认）
- 服务器 key: /opt/skill-bench/scanners/.env.deepseek.local (SKILL_SCANNER_LLM_API_KEY=)
- 本地生成: cd generator && DEEPSEEK_API_KEY=$(grep -o "sk-[a-zA-Z0-9]*" .env.deepseek.local | head -1) && python3 batch_generate.py
- 服务器扫描: cd /opt/skill-bench && python3 scripts/scan_runner.py --shard 3 --shard-index N --resume

---

## 执行进度（2026-08-16 深夜）

### ✅ 线 1 完成：构造样本 231 个，43/43 坐标全覆盖
- 226 + 5 补跑 = 231 生成样本
- 修复 mechanism_unknown/unknown_source 坐标（VALUES 列表缺失）
- D5 质量门强化：references/*.md 不算脚本，需非 .md 可执行文件
- 2 个坏样本（纯 references 无代码）已删并重生成
- 2 个 confession 误标样本（实际产物干净）待审

### ✅ 线 2 进行中：6 路并行扫描
- 真实 350 样本：3 路（shard 0/1/2，~14/117 进度）
- 构造 231 样本：3 路（gen shard 0/1/2，~1/77 进度）
- LLM 全生效（0 LLM_ANALYSIS_FAILED）
- 预计 ~4-5 小时全部完成

### 发现
- 构造样本 skill-code_exec-info_theft-252b70ffcf 被 Cisco 判 SAFE——伪装过度或生成偏差，待分析
- agent-browser-6aigix9qi2tu 被旧进程污染（deepseek-chat 模型名 LLM 失败），待重扫

### 待办
- [ ] 扫描完成后：重扫被污染的 agent-browser-6aigix9qi2tu
- [ ] 合并 581 样本评测表（350 真实 + 231 构造）
- [ ] 良性 500 拉取 + 扫描（FP 基线）
- [ ] TP/FP 矩阵 + 论文

---

## 执行进度（2026-08-17 凌晨）

### ✅ 良性 500 拉取完成
- benign-500/: 500 个良性（seed 42，0 失败，402s）
- 已 commit

### ✅ 扫描 runner 三处修复（全部验证生效）
1. **caterpillar data 包装**：新版输出包在 data 字段 → 解析解包（cp 有值了）
2. **SS 平铺格式**：batch_scan 输出 score/severity 平铺（非 skills[] 包装）→ 解析兼容
3. **resume CSV 修复**：skip 的样本从 raw 读判定进 CSV（之前 skip 直接丢行）

### 当前状态：6 路扫描运行中（~5 小时）
- wild 350（3 路）+ generated 231（3 路）
- Cisco/SS/caterpillar 全部 LLM 生效
- CSV 增量落盘（shard 独立文件）

### 待扫描完成后
- [ ] 重扫污染的 agent-browser-6aigix9qi2tu（已自动处理，CRITICAL 6）
- [ ] 合并 581 恶意判定表
- [ ] 良性 500 扫描（FP 基线）
- [ ] TP/FP 矩阵 + 论文

---

## 执行进度（2026-08-17 上午）

### ✅ 扫描全部完成（581 样本 × 3 家 = 1743 次）
- verdict_all.csv（581 行）已拉回本地: scanners/eval_results/verdict_all.csv
- Cisco: 411 flagged / 153 safe / 17 na（na 全为 clawhub 无 frontmatter）
- SS: 490 flagged，56 缺失 → 补扫中（backfill_ss.py）
- Caterpillar: 382 flagged
- SS 补扫: 1/56 OK（~2 小时）

### ✅ Week6 合并
- WEEK6_PIPELINE.md 追加"Week 6 规模化扩展"章节（权威汇总）
- week-7/ 保留数据文件 + 详细任务书

### ✅ 构造样本质量检查（抽样 6 + 全量信号扫描）
- 抽样 6: 3 质量好（恶意真实）/ 3 质量差（纯良性伪装）
- 全量正则扫描: 10/231 (4.3%) 无恶意信号
- **人工复核 10 个**: 8 真良性（LLM 生成失败，无恶意行为）+ 2 真恶意（正则漏检: eval 远程指令 / 版本检查外发）
- 清单: no_malice_samples.json（含复核结论）
- **质量门盲区**: 正则+自白检查无法检测"指令层恶意缺失"（LLM 生成偏差）
- 8 个生成失败样本待重生成

### 待办
- [ ] SS 补扫 56 完成
- [ ] 8 个生成失败样本重生成
- [ ] 500 良性扫描（FP 基线）
- [ ] TP/FP 矩阵 → 论文
