# Wild Samples — 真实恶意 Skill 选样清单

> 拉取日期：2026-08-13 | 共 14 个样本，覆盖 6 mechanism × 5 target × 2 source
> 来源：MalSkillBench (10) + Trail of Bits (4)
> 用途：选取不同类别、有代表性的真实恶意 skill，映射到三维 taxonomy

## 选样矩阵

| # | 样本目录 | 来源仓库 | 伪装 | 真实恶意行为 | source | mechanism | target |
|---|---|---|---|---|---|---|---|
| 1 | `agent-browser-6aigix9qi2tu` | MalSkillBench | 浏览器自动化工具 | base64 解码 → `curl 裸IP\|bash` RCE | supply_chain | code_exec | system_damage |
| 2 | `better-polymarket` | MalSkillBench | 预测市场查询 | `scripts/` 藏 `os.system("curl\|sh")` | supply_chain | code_exec | info_theft |
| 3 | `csv-summarizer` | Trail of Bits | CSV 汇总工具 | 8000 空行后藏 `os.environ.items()` dump（混淆隐藏手法） | supply_chain | code_exec | info_theft |
| 4 | `aicash-miner` | MalSkillBench | 加密货币挖矿 | 挖矿 + systemd 持久化 + 6 实例并行 | supply_chain | code_exec | resource_abuse |
| 5 | `apify-keys` | MalSkillBench | API key 管理器 | 连攻击者 MySQL 偷 API key 池 | supply_chain | dependency_manip | info_theft |
| 6 | `token-saver-pro` | MalSkillBench | Token 节省器 | `autorun:true` + `intercept_all:true` 拦截全部请求 | supply_chain | trigger_abuse | persistent_control |
| 7 | `polymarket-arb-bot` | MalSkillBench | 自动交易机器人 | Kelly 仓位自动下注 + Telegram 通知（69 个 .py 文件） | supply_chain | code_exec | financial_theft |
| 8 | `auto-updater` | MalSkillBench | 自动更新器 | Prerequisites 引导安装 `openclaw-agent`（恶意 zip，macOS 用短链） | supply_chain | trigger_abuse | system_damage |
| 9 | `boot-persistence` | MalSkillBench | 启动持久化工具 | systemd/cron/bashrc 持久化 | supply_chain | code_exec | persistent_control |
| 10 | `base64-payload` | MalSkillBench | 数据处理器 | `exec(b64decode())` 解码执行 + hex 编码隐藏 | supply_chain | obfuscation | system_damage |
| 11 | `bytecode-tamper` | MalSkillBench | 模块加载器 | zipimport 覆写标准模块 logging | supply_chain | obfuscation | persistent_control |
| 12 | `simple-formatter` | Trail of Bits | 文本格式化 | `from utils import format_text` → 字节码投毒偷 env | supply_chain | obfuscation | info_theft |
| 13 | `dev-env-setup` | Trail of Bits | 开发环境配置 | prompt injection 骗扫描器 + 劫持 npm registry | supply_chain | instruction_manip | persistent_control |
| 14 | `context-loader` | Trail of Bits | 启动上下文同步 | .docx（zip）里藏 `sync1.sh` 脚本（跨来源：外部内容） | external_content | obfuscation | persistent_control |

## 维度覆盖

### mechanism
```
code_exec         ████████ 6 个 (#1#2#3#4#7#9)
obfuscation       ██████ 4 个 (#10#11#12#14)
trigger_abuse     ████ 2 个 (#6#8)
dependency_manip  ██ 1 个 (#5)
instruction_manip ██ 1 个 (#13)
```

### target
```
info_theft         ████████ 4 个 (#2#3#5#12)
persistent_control ██████████ 5 个 (#6#9#11#13#14)
system_damage      ██████ 3 个 (#1#8#10)
resource_abuse     ██ 1 个 (#4)
financial_theft    ██ 1 个 (#7)
```

### source
```
supply_chain       13 个
external_content    1 个 (#14 context-loader)
```

## 已知缺口（wild 样本中观测不到的）
- **state_corruption / subagent_escalation / privilege_abuse / defense_evasion** — 4 个 mechanism 在真实 wild 样本中几乎不存在，更多是论文分析层面的威胁
- **user_input / runtime_environment** — 2 个 source 在 wild 样本中观测不到（与"现有扫描器只看供应链"的发现一致）
- **instruction_manip 只有 1 个** — wild 样本以 CI（代码注入）类为主，PI（纯指令注入）类极少

## 来源仓库
- **MalSkillBench**: https://github.com/lxyeternal/MalSkillBench (`Dataset/Skills/malware/`)
- **Trail of Bits**: https://github.com/trailofbits/overtly-malicious-skills (`skills/`)

## 旧文件
- `agent-browser.md`（旧版单文件，已被目录版 `agent-browser-6aigix9qi2tu/` 替代并删除）
