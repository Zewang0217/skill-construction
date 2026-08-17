# 设施失败重扫记录（2026-08-17）

## 问题
Cisco 扫描器 581 恶意样本中 **133 个设施失败**（116 LLM_ANALYSIS_FAILED + 17 is_safe=null），
加上良性样本共 193 个失败。这些"漏检"是基础设施问题（DeepSeek 瞬时故障/解析失败），**不是检测能力问题**。

## 错误类型（116 个恶意 LLM 失败）
| 错误 | 数量 | 性质 |
|---|---|---|
| Empty response from LLM | 86 | DeepSeek 瞬时故障，重扫可恢复 |
| JSON 解析失败（含 CRITICAL/HIGH findings）| 29 | LLM 返回了检出但格式坏，检测被丢弃 |
| 其他 | 1 | — |

## 重扫验证（rescan_failed.py，服务器后台）
- 已恢复样本：privilege-escalation-methods（safe=False CRITICAL，之前失败）
- 持续失败样本：novafon / klaviyoapi / rbtc（无 frontmatter 或 LLM 持续故障）

## 更新计划（重扫完成后）
1. 重建 verdict_all.csv（覆盖失败的 raw）
2. 重新统计检出率（去除设施失败）
3. 更新 5 份 ANALYSIS_*.md：把"LLM 失败导致漏检"从真漏检中剔除

---

## 重扫完成 + 阈值问题分析（2026-08-17 更新）

### 重扫结果
- Cisco 116 OK / 17 FAIL（193 个含良性）；SS solana-dddhn OK
- **恶意侧检出恢复：411 → 416**（恢复 wallet-tracker/deep-research/nano-banana-pro 等 CRITICAL）
- 17 个持续 FAIL 全是 clawhub 无 frontmatter（Cisco 拒绝加载，非 LLM 失败，重扫无效）

### ⚠️ 阈值问题（比设施失败影响更大）
**`models.py:226`: is_safe = not any(severity in (CRITICAL, HIGH))**

**80 个恶意样本 is_safe=True 但有 MEDIUM 危险 finding**（581 的 13.8%）：
- gen 70 / wild 10
- 主要规则：TOOL_ABUSE_UNDECLARED_NETWORK 58、DATA_EXFIL_NETWORK_REQUESTS 51、LLM_DATA_EXFILTRATION 19
- **gen 检出率 51.9% 的最大失真来源**：30% 的 gen 样本被阈值吞掉（网络外泄检测到了但判安全）

### 修正后检出率
| 组 | Cisco is_safe 口径 | +阈值放行(真实检测) |
|---|---|---|
| wild | 84.6% | +10 → ~87% |
| gen | 51.9% | +70 → **~82%** |
| 合计 | 71.6% | +80 → **~85%** |

**结论**：Cisco 的真实检测能力约 85%，is_safe 阈值设计把 13.8% 的检出吞成了 safe。
