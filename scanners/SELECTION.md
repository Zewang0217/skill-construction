# Scanner 选型与安装记录（2026-08-13）

## 选定 3 家对比矩阵（最终）

| Scanner | repo/包 | 类型 | deepseek 适配 | 状态 |
|---|---|---|---|---|
| **NVIDIA SkillSpector** | NVIDIA/SkillSpector | Python | ✅ 主 CLI 卡点，官方 contrib/batch_scan 兼容层 | ✅ 已装 v2.9.3 |
| **Cisco skill-scanner** | cisco-ai-defense/skill-scanner | Python | ✅ 源码原生（deepseek 白名单自动降级 json_object）| ✅ 已装 v2.0.13 |
| **Caterpillar** (offline) | alice-dot-io/caterpillar (npm @alice-io/caterpillar) | Node | ⚠️ openai 模式需 fork 改；**offline 纯本地正则免改** | ✅ 已装 v1.0.11 |

## 为什么排除 SkillWard（用户判断 + 事实核查，2026-08-13）
- **SkillWard 内嵌了 Cisco 的 `skill_scanner` 引擎源码**（`SkillWard/skill-scanner/` = 同名 `skill_scanner/core/analyzers/{static,bytecode,pipeline}.py`，结构逐文件相同）。
- 差异只在 LLM 分级阈值 + Docker 沙箱——而我们纯静态不用沙箱。
- → SkillWard 只是"Cisco 引擎 + 不同 LLM wrapper",静态面 100% 重复，**无独立检测维度增量**。
- 保留价值：作为完整产品（静态+LLM+沙箱）供 S6 防御设计参考，不作评测 baseline。

## 3 家范式多元性
- **Cisco**：多引擎（静态+LLM+bytecode+pipeline+BEHAVIORAL dataflow）
- **SkillSpector**：17 类语义（静态正则+AST+YARA+LLM+OSV.dev）
- **Caterpillar offline**：纯正则 16 条（零语义，最弱触发面基线）


## 各 scanner 运行方式

### SkillWard（skillward-venv 隔离，避免 skill-scanner 包冲突）
```bash
LLM_PROVIDER=deepseek LLM_ID=deepseek-chat LLM_API_KEY=sk-xxx \
  skillward-venv/bin/python SkillWard/guardian-api/guardian.py \
  -i <skills-dir> --stage pre-scan -o <out-dir>
```
- `--stage pre-scan` = 静态 + LLM，无 Docker 无登录
- 输出 `guardian_report.json`（prescan.<skill>.findings + is_safe + confidence/UNSAFE）
- 注意：atexit 有 `docker ps` 钩子，缺 Docker 时打印"killing containers"警告，无害
- 无 key 时 LLM triage 返回 0.0 → 全判 UNSAFE，务必配 deepseek

### Caterpillar（offline 模式，纯本地正则）
```bash
caterpillar ask <skill-path> --mode offline --json
```
- 8 类 16 条正则（credential-theft/data-exfiltration/crypto/persistence/network/obfuscation/dangerous-permissions/supply-chain）
- 输出 `{success, data:{skill, grade A-F, score 0-100, findings[]}}`
- 无 key 自动落 offline（`--mode offline` 强制）
- 最弱基线：单正则无上下文，FP/FN 都多，适合当"触发面最小"对照

## 排除的工具（含理由）
- **VirusTotal**：闭源云 API；只对恶意代码区有效（ClawHub 72.8% 阳性），对语义/授权风险盲区。用户确认不用。
- **Snyk agent-scan**：分析在 Snyk 托管闭源后端，样本会上传 + 无法接 deepseek。
- **Caterpillar openai 模式（主力）**：LLM 端点/模型硬编码，需 fork 改。

## 关键调研结论（scout 2026-08-13）
- 领域事实标准 = SkillSpector + Cisco（所有对比论文的共同基线）
- 四家 scanner 全部只能看到"供应链入口"；外部内容/用户输入/运行时/组合是盲区
- SkillWard 复用 skill-scanner 静态引擎（17 类），但 LLM 面/分类体系不同
- Caterpillar offline 是纯正则，跟三家的语义分析完全不同 → 天然"最弱基线"
