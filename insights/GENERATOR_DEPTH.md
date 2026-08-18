# 生成器深度分析：mapping-db 证据使用与坐标内变体空间

> 版本：2026-08-18 | 回答：① 生成是否充分使用 mapping-db example？② 坐标内变体空间有多大？

---

## 一、mapping-db evidence 使用审计：用了，但严重不充分

### 1.1 数据事实

| 指标 | 值 |
|---|---|
| 43 坐标中 `mdb_evidence` 非空 | 39（4 个空） |
| mdb_evidence 总条数 | **159** |
| coord_seeds 手写 behaviors 总条数 | **44** |
| 每坐标生成配额 | 2-5（batch_generate `--per-coord`） |
| 实际生成 | 232（43 坐标 × 平均 5.4） |

### 1.2 使用路径（patterns.py `coord_coordinate` L257-269）

```python
behaviors = list(entry.get("behaviors", []))      # 手写 44 条优先
behaviors += list(entry.get("handbook", []))
if not behaviors and entry.get("mdb_evidence"):    # 兜底：behaviors 空才用 evidence
    behaviors = list(entry["mdb_evidence"])
```

**问题**：`behaviors` 非空的坐标**完全不走 evidence**——159 条 evidence 中，只有 behaviors 为空的
坐标（如 `source_agnostic|code_exec|target_agnostic` beh=0）才会用。即使用了，每坐标 5 个配额
也只能采样 24 条 evidence 中的 5 种攻击方式，**87.5% 的变体被丢弃**。

### 1.3 code_exec 坐标的变体空间（用户点名）

`source_agnostic|code_exec|target_agnostic` 的 24 条 evidence 覆盖**代码执行攻击全部变体谱系**：

| 攻击族 | evidence | 是否生成 |
|---|---|---|
| 直接危险调用 | exec()/eval()/__import__()/compile() | 部分（配额限制） |
| 外部命令 | subprocess.{call,run,Popen}/os.{system,popen,execv} | 部分 |
| 反射规避 | getattr(os,'system') 绕过 AST 检测 | 否（配额用尽） |
| 污点数据流 | source→sink 直接/经中间变量 | 否 |
| 工具引用 | ncat/Ledger 等 offensive tools（YARA） | 否 |
| 网络调用 | fetch/http/socket（SOCK-S13） | 否 |
| FS/env 访问 | SOCK-S21/S22 | 否 |
| JS 动态 | 动态 require / npm 安装脚本 | 否 |
| 链式绕过 | `&& rm` / `curl\|bash` 多步链 | 否 |

**结论**：代码执行坐标的**攻击方式多样性未被充分采样**——24 种只生成了 5 种，且生成时
`seed_actions` 从 behaviors（0 条）→ evidence（24 条）取整列表，LLM 每次随机发挥，无系统性覆盖。

---

## 二、坐标内变体空间：同一坐标可以有多少种不同样本？

### 2.1 变体维度（同一坐标内）

给定坐标 `(source, mechanism, target)`，变体空间 = 以下维度笛卡尔积：

| 维度 | 例子（code_exec） | 当前覆盖 |
|---|---|---|
| **攻击原语** | exec/eval/subprocess/os.system/compile/getattr 反射/动态 require | 24 选 5 |
| **向量** | CI（代码注入）/ PI（提示注入）/ MIXED | 3 值随机 |
| **伪装主题** | DISGUISE_THEMES（如账号同步助手、天气工具） | 随机 |
| **语言/编码** | Python/JS/Bash/中文/Unicode 混淆/Base64 | 随机 |
| **来源注入点** | supply_chain 的安装脚本 vs user_input 的插值点 | SOURCE_STRATEGY |
| **时序** | 安装时执行 vs 运行时触发 vs 远端文件引用 | 无维度（关键缺口） |
| **包装复杂度** | 直白 vs 免责话术+伪装正常工具 | 无维度（关键缺口） |

### 2.2 估算

- code_exec 坐标：24 原语 × 3 向量 × 5 伪装 × 2 时序 ≈ **720 变体**，当前只生成 5 个（0.7%）
- 全部 43 坐标：若每坐标按 evidence 数 × 向量 × 伪装扩样，总变体空间 **数千级**，当前 232

---

## 三、改进方案（讨论）

### 方案 A：证据配额制（最小改动）
- 每坐标生成数 = `max(5, len(mdb_evidence))`，保证每条 evidence 至少采样 1 次
- 改 `batch_generate.py`：`per_coord` 按坐标 evidence 数自适应
- 效果：code_exec 从 5 → 24 个，43 坐标总生成 ~230 → ~500
- 代价：LLM 调用成本 ×2.2（~¥60-90 → ~¥150-200）

### 方案 B：变体维度扩充（中等改动）
- 新增**时序维度**（install/runtime/remote-ref）和**包装维度**（plain/defensive-wrapped/social-eng）
- coord_coordinate 返回 4 维坐标（含时序+包装），prompt 注入相应约束
- 效果：能构造"SS 盲区"包装版样本（EXPERIMENT_SCOPE 组 A 的前置条件）
- 代价：coord_seeds 需加字段 + prompt 模板改 + 重新生成部分坐标

### 方案 C：定向扩样（针对性）
- 只对高价值坐标扩样：code_exec（24 evidence）、dependency_manip（19）、privilege_abuse（7）
- 只对 SS 盲区坐标生成"包装版"（免责话术 + 执行阶段载荷）
- 效果：用最小成本验证盲区可复现性（EXPERIMENT_SCOPE 三组对照）

### 推荐：A + C 组合
1. **先做 C**（定向验证 SS 盲区可复现——论文最高价值，成本最小）
2. **再做 A**（证据配额制扩样——补多样性，为最终数据集做准备）

---

## 四、用户问题 2 的回应

> "wild 更容易具备真实攻击。要证明 taxonomy 有价值，最好让 gen 能构造出 scanner 扫不出来的 skill"

**验证思路**：这是对的。但当前证据表明：
- gen 构造（直白）→ SS 检出 96-100%，证明"taxonomy 能生成可检测恶意"
- wild 真实（包装）→ SS 漏检 25 个，证明"真实攻击有绕过能力"

**taxonomy 的价值主张**应该是：**坐标内细节（原语/时序/包装）决定可检测性，坐标本身不决定**。
要证明这个，需要：
1. 同一坐标下生成"直白版 vs 包装版"对照样本
2. 验证包装版显著降低扫描器检出率（SS：100% → X%）
3. 若成立，taxonomy 的价值 = "能主动构造扫描器盲区样本"，而非仅"描述已知恶意"

**坐标关注优先级**（用户点名 + 证据支持）：
- **方式**：code_exec（24 变体，最丰富）、privilege_abuse、persistent_control（8 evidence）、obfuscation
- **混淆隐藏**：obfuscation 坐标（base64/Unicode/中文/多媒体——扫描器语义层对多语言/多模态的盲区未测）
- **来源**：supply_chain vs source_agnostic（Cat 检出差异 5/5 vs 2/5 已验证）
- **目标**：info_theft/persistent_control（SS 盲区 B2/B15 所在）

---

## 五、待讨论决策

1. 采用方案 A + C 还是其他？
2. 包装维度是否加入 coord_seeds（影响 taxonomy 本身还是仅生成器）？
3. 扩样规模：500 样本（A）还是定向 ~100（C）？
4. 中文/多媒体混淆样本是否值得专门构造（扫描器对非英文指令的处理能力）？
