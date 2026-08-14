# Wild Samples — 真实恶意 Skill 选样清单

> 拉取日期：2026-08-13 | 共 14 个样本，覆盖 6 mechanism × 5 target × 2 source
> 来源：MalSkillBench (10) + Trail of Bits (4)
> 用途：选取不同类别、有代表性的真实恶意 skill，映射到三维 taxonomy
> 映射口径：source / mechanism / target 均支持多值

## 选样矩阵

| # | 样本目录 | 来源仓库 | 伪装 | 真实恶意行为 | source | mechanism | target |
|---|---|---|---|---|---|---|---|
| 1 | `agent-browser-6aigix9qi2tu` | MalSkillBench | 浏览器自动化工具 | base64 解码 → `curl 裸IP\|bash` RCE | supply_chain | code_exec | system_damage |
| 2 | `better-polymarket` | MalSkillBench | 预测市场查询 | `scripts/` 藏 `os.system("curl\|sh")` | supply_chain | code_exec | info_theft |
| 3 | `csv-summarizer` | Trail of Bits | CSV 汇总工具 | 8000 空行后藏 `os.environ.items()` dump | supply_chain | code_exec + obfuscation | info_theft |
| 4 | `aicash-miner` | MalSkillBench | 加密货币挖矿 | 挖矿 + systemd 持久化 + 6 实例并行 | supply_chain | code_exec | resource_abuse + persistent_control |
| 5 | `apify-keys` | MalSkillBench | API key 管理器 | 连攻击者 MySQL 偷 API key 池 | supply_chain | code_exec | info_theft |
| 6 | `token-saver-pro` | MalSkillBench | Token 节省器 | `autorun:true` + `intercept_all:true` 拦截全部请求 | supply_chain | trigger_abuse + instruction_manip | persistent_control |
| 7 | `polymarket-arb-bot` | MalSkillBench | 自动交易机器人 | Kelly 仓位自动下注 + Telegram 通知（69 个 .py 文件） | supply_chain | code_exec | financial_theft |
| 8 | `auto-updater` | MalSkillBench | 自动更新器 | Prerequisites 引导安装 `openclaw-agent`（恶意 zip，macOS 用短链） | supply_chain | trigger_abuse + code_exec | system_damage |
| 9 | `boot-persistence` | MalSkillBench | 启动持久化工具 | systemd/cron/bashrc 持久化 | supply_chain | code_exec + state_corruption | persistent_control |
| 10 | `base64-payload` | MalSkillBench | 数据处理器 | `exec(b64decode())` 解码执行 + hex 编码隐藏 | supply_chain | code_exec + obfuscation | system_damage |
| 11 | `bytecode-tamper` | MalSkillBench | 模块加载器 | zipimport 覆写标准模块 logging | supply_chain | code_exec + obfuscation | persistent_control |
| 12 | `simple-formatter` | Trail of Bits | 文本格式化 | `from utils import format_text` → 字节码投毒偷 env | supply_chain | code_exec + obfuscation | info_theft |
| 13 | `dev-env-setup` | Trail of Bits | 开发环境配置 | prompt injection 骗扫描器 + 劫持 npm registry | supply_chain | instruction_manip + dependency_manip | persistent_control |
| 14 | `context-loader` | Trail of Bits | 启动上下文同步 | .docx（zip）里藏 `sync1.sh` 脚本 | external_content + supply_chain | obfuscation + code_exec | target_agnostic |

## 扫描结果（2026-08-14，三家扫描器）

> 数据：`scanners/eval_results/verdict_wild.csv` + `raw_wild/`（42 次扫描全成功）
> 对比：生成样本基线 6/6 全检出 → 真实样本显著下降

| # | 样本 | Cisco | SkillSpector | Caterpillar | 联合 |
|---|---|---|---|---|---|
| 1 | agent-browser-6aigix9qi2tu | ✗ CRITICAL(8) | 100 CRITICAL | B/84 | 检出 |
| 2 | better-polymarket | ✗ CRITICAL(13) | 100 CRITICAL | C/70 | 检出 |
| 3 | csv-summarizer | **漏**(预算超限) | 97 CRITICAL | 漏 | 检出 |
| 4 | aicash-miner | ✗ HIGH(7) | 42 MEDIUM(弱) | A/92(弱) | 检出(皆弱) |
| 5 | apify-keys | ✗ CRITICAL(8) | 76 HIGH | 漏 | 检出 |
| 6 | token-saver-pro | ✗ HIGH(11) | 100 CRITICAL | 漏 | 检出 |
| 7 | polymarket-arb-bot | ✗ CRITICAL(85) | 100 CRITICAL | C/61 | 检出 |
| 8 | auto-updater | ✗ HIGH(4) | **漏**(0/LOW) | 漏 | 检出(仅Cisco) |
| 9 | boot-persistence | ✗ HIGH(6) | 100 CRITICAL | D/47 | 检出 |
| 10 | base64-payload | ✗ CRITICAL(9) | 100 CRITICAL | C/62 | 检出 |
| 11 | bytecode-tamper | ✗ HIGH(4) | 60 HIGH | 漏 | 检出 |
| 12 | simple-formatter | **漏**(SAFE) | **漏**(0/LOW) | **漏** | **三家全漏** |
| 13 | dev-env-setup | **漏**(误判safe) | 49 MEDIUM | C/61 | 检出 |
| 14 | context-loader | ✗ HIGH(11) | **漏**(0/LOW) | 漏 | 检出(仅Cisco) |

### 检出率
| 扫描器 | 生成样本基线 | 真实样本 |
|---|---|---|
| Cisco | 6/6 (100%) | **11/14 (78.6%)** |
| SkillSpector | 6/6 (100%) | **11/14 (78.6%)** |
| Caterpillar | 6/6 (100%) | **7/14 (50.0%)** |
| 联合（任一命中） | — | **13/14 (92.9%)** |

### ⚠️ 三家全漏：simple-formatter（#12）
执行期字节码投毒偷 env——静态快照全干净 ASCII，恶意在 `from utils import format_text` 导入时发生。静态+LLM+正则三类全不可见，是扫描器族结构性盲区。

### 真实样本更难检的原因（对照生成样本）
1. **大文件逃逸**：csv-summarizer 98KB 脚本超 Cisco 15k 字符 LLM 预算（`LLM_CONTEXT_BUDGET_EXCEEDED`）
2. **伪装良性**：auto-updater 用 "Prerequisites" 引导装恶意 zip，SS 判 0/LOW 无感
3. **二进制载体**：context-loader 恶意在 638KB docx(zip)；bytecode-tamper zipimport 覆写
4. **执行期投毒**：simple-formatter，静态不可见

## 维度覆盖

### mechanism
```
code_exec          ████████████ 9 个 (#1#2#3#4#7#8#9#10#11#12#14)
obfuscation        ██████ 5 个 (#3#10#11#12#14)
instruction_manip  ████ 3 个 (#6#13#14)
trigger_abuse      ████ 2 个 (#6#8)
dependency_manip   ████ 2 个 (#5#13)
state_corruption   ████ 2 个 (#4#9)
```

### target
```
info_theft         ████████ 4 个 (#2#3#5#12)
persistent_control ██████████ 5 个 (#4#6#9#11#13)
system_damage      ██████ 3 个 (#1#8#10)
resource_abuse     ██ 1 个 (#4)
financial_theft    ██ 1 个 (#7)
target_agnostic    ██ 1 个 (#14)
```

### source
```
supply_chain       14 个
external_content    1 个 (#14 context-loader)
```

## taxonomy 完备性分析：wild 样本未覆盖的 mechanism

> 定位：这是对 taxonomy 的检验，不是样本缺陷。wild 样本观测不到某机制 ≠ taxonomy 多定义了不存在的攻击，需要区分成因。

| mechanism | taxonomy 槽位数 | wild 观测 | 成因分析 |
|---|---|---|---|
| **权限滥用** | 19 | 0 独立出现 | **声明面机制**——攻击在权限声明（allowed-tools/过度授权），wild 样本多为载荷面（执行/挖矿），映射时被归到更表面的机制。实际存在：aicash-miner 写 /etc/systemd 即越权 |
| **状态污染** | 11 | 2 沾边（boot-persistence / aicash-miner 持久化）| 部分覆盖；记忆投毒（C07-α）等运行时状态类无对应 |
| **子agent提权** | 1 | 0 | **agent 运行时面机制**——攻击发生在 subagent 权限继承，静态 skill 文件无痕迹，任何静态样本都观测不到（除非动态执行）|
| **规避检测** | 1 | 0 | **检测时面机制**——攻击是感知扫描器后自适应绕过，发生在检测过程中，skill 文件无法体现 |

### 三种成因（决定 taxonomy 是否完备）

1. **声明面机制被载荷面掩盖**（权限滥用）→ taxonomy **完备**，但映射口径需改进：不能只看恶意载荷，要看"攻击依赖的权限/能力是否越界"
2. **运行时/检测时面机制**（子agent提权、规避检测）→ taxonomy 定义**超出静态 skill 观测域**——这些威胁真实存在，但需要动态执行才能观测。对"静态扫描器评测"而言它们是不可测的维度，需在论文中明确标注
3. **覆盖不足但存在**（状态污染的记忆投毒类）→ 样本选样需补充，不是 taxonomy 问题

### 对论文的意义
- taxonomy 的 mechanism 维度**混合了静态可测与静态不可测的攻击**——子agent提权/规避检测属于后者，评测时必须标注"仅动态可观测"，否则会被误读为扫描器漏检
- 权限滥用的高槽位数（19）与 wild 低观测形成反差，说明**映射方法比 taxonomy 更可能是瓶颈**——需要双人盲审时统一"声明面 vs 载荷面"的判定标准

## taxonomy 完备性分析：source 维度

| source | taxonomy 值 | wild 观测 | 成因分析 |
|---|---|---|---|
| **supply_chain** | ✅ 主流 | 14/14 | 真实恶意 skill 的天然主要来源——ClawHavoc 战役就是供应链投放，观测充分 |
| **external_content** | ✅ | 1（context-loader）| 真实存在但稀缺：docx 藏脚本是典型的间接注入载体 |
| **user_input** | ⚠️ | 0 | **条件触发类攻击**（contextual/dual-use）依赖运行时用户输入，静态样本可构造（X-UI 组生成样本已覆盖），但真实 wild 中少见——攻击者倾向供应链直接投放，而非等用户触发 |
| **runtime_environment** | ⚠️ | 0 | **运行时面 source**——攻击操作 env/MCP/记忆等运行时组件，skill 静态文件可声明（生成样本可构造），真实 wild 中未观测到独立案例 |
| **source_agnostic** | ✅ | 0（隐含）| 语义上是"来源无关"，wild 样本的实际投放仍是供应链，source_agnostic 是分析视角而非攻击者选择 |

### 结论
- **source 维度本身完备**——5 个值都有真实语义基础，没有凭空捏造
- user_input / runtime_environment 的 wild 低观测**不说明 taxonomy 多定义了不存在的来源**，而是说明攻击者的真实偏好（供应链）与 taxonomy 的分析视角（包含理论可能）存在差异
- 这正是论文的论证点：**taxonomy 覆盖攻击者"可能"做的，扫描器只防住了攻击者"实际"在做的——gap 是真实的攻击面**

## 来源仓库
- **MalSkillBench**: https://github.com/lxyeternal/MalSkillBench (`Dataset/Skills/malware/`)
- **Trail of Bits**: https://github.com/trailofbits/overtly-malicious-skills (`skills/`)

## 旧文件
- `agent-browser.md`（旧版单文件，已被目录版 `agent-browser-6aigix9qi2tu/` 替代并删除）
