# 3 家扫描器横评 — 结果（2026-08-13，修复版）

> ⚠️ 版本说明：早期版本曾发现"better-polymarket 三家分歧/漏检"，
> **经排查为 eval_all.py 的 bug（只拷 SKILL.md，漏 scripts/ 子目录），已修复重跑**。
> 本文件是修复后（完整 skill 目录）的真实结果。

## 测试集（6 样本：2 真实 MalBench + 4 生成）
- real/agent-browser-6aigix9qi2tu（MalBench wild 真实恶意，base64 载荷 + 下载执行明文在 SKILL.md）
- real/better-polymarket（MalBench wild 真实恶意，`scripts/polymarket.py:180` `os.system("curl|sh")` RCE）
- generated/ 4 个（我们三维 taxonomy 生成器产出）

## 结果矩阵（修复版：完整目录含 scripts/）

| 样本 | Cisco | SkillSpector | Caterpillar | 检出 |
|---|---|---|---|---|
| agent-browser (真实) | FLAG(7) | 100(5) | B/84(2) | ✅ 三家都检出 |
| better-polymarket (真实) | **FLAG(12, CRITICAL)** | **100(7)** | C/70(1) | ✅ 三家都检出 |
| generated env-mgr | FLAG(9) | 100(19) | C/70(1) | ✅ |
| generated git-commit | FLAG(4) | 100(11) | C/62(2) | ✅ |
| generated dependency | FLAG(6) | 100(9) | C/62(2) | ✅ |
| generated instruction | FLAG(7) | 100(15) | F/32(3) | ✅ |

**6/6 全部被三家扫描器检出。**

## 关键发现（修正后）

### 发现 1：之前"反直觉分歧"结论已推翻 —— 是评测脚本 bug,不是真实分歧
第一版误报"better-polymarket 被 Cisco/SS 漏检,Caterpillar 反而抓"。
**根因**：eval_all.py 只把 SKILL.md + generated.sh 拷进临时目录,**不递归 scripts/ 子目录**；
better-polymarket 恶意在 `scripts/polymarket.py`，没传给 scanner → 假漏检。
**修复**：新增 `_copy_tree()` 递归拷贝整个 skill 目录，三个 run_* 都用它。
修复后 better-polymarket 被三家全抓（Cisco CRITICAL 12 findings，LLM 明确识别"arbitrary code execution"）。

### 发现 2（方法学，仍成立）：评测必须用完整 skill 目录
MalBench wild 恶意**常 SKILL.md 干净、恶意藏 scripts/**。
任何评测脚本**必须递归拷贝整个 skill 目录（含 scripts/）**，否则假漏检。
这是本轮最重要的工程教训。

### 发现 3：供应链明文 RCE 不是盲区
三家都能抓 agent-browser（SKILL.md 明文载荷）和 better-polymarket（scripts/ 里的 RCE）。
→ **供应链通道对这三家静态 scanner 是强项区，不是盲区**。
真正的盲区（pilot H1）需要探测外部内容/用户输入/运行时/组合通道——那些 scanner 静态视野看不到。

## 结论（修正后）
- 我们的生成器产出的 4 个恶意样本被**三家全检出** → 生成质量达标、scan 保真。
- 评测脚本必须整目录拷贝（已修）。
- "供应链 RCE"对 3 家不是盲区；**盲区需去半盲/盲区坐标找**（external_content / user_input / runtime / compositional）。

## 后续
- 现有样本全在供应链/来源无关通道（易检出）。真正验证 pilot H1 盲区，**需采样 blind/half 可见性坐标**（生成器已支持 `--visibility`）。
- 生成器改造产出的 blind/half 样本还没跑 scanner —— 那才是盲区图的候选来源。
