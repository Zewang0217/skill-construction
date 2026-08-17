# D2 决策：mechanism 是否新增 `malicious_distribution`（2026-08-17）

## 问题
mechanism 维度是否新增"恶意分发/社工引导"值？触发证据：
- auto-updater 真实样本：Prerequisites 引导用户从恶意 zip 安装 openclaw-agent
- mdb AITech-15.1 Scams and Deception（VAGUE_DESCRIPTION / ANTHROPIC_IMPERSONATION）
- mdb AITech-2.1 Jailbreak（映射到 social_engineering）

## 决策：不新增独立值

**理由**：
1. **可被现有值多值表达**：
   - auto-updater 引导装恶意包 → `dependency_manip`（引导安装恶意依赖）+ `trigger_abuse`（Prerequisites 激活）
   - Scams/Impersonation（描述说谎）→ `instruction_manip`（文本误导 agent 信任）
   - 无任何样本需要独立值才能表达
2. **43 坐标一致性**：43 坐标基于现有 10 mech 值构建；加值需重建全部坐标 + COORD_SEEDS，破坏已生成的 231 样本与评测表
3. **多值机制已覆盖**：真实样本跨机制（source/mech/target 均可多值），社工引导作为"复合机制"可拆入现有值

## 落地
- taxonomy mechanism 保持 10 值不变
- auto-updater 的映射维持：trigger_abuse + code_exec（已在 wild-samples/README.md）
- Scams/Impersonation 类归入 instruction_manip（描述层误导）

## 关联
- D1（persistent_control 扩展覆盖目标劫持）已拍板
- 若未来出现"纯分发无其他机制"的样本再复议
