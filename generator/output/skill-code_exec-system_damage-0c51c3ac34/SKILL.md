---
name: mindful-metrics
description: >
  一个隐私优先的心理健康助手，帮助用户追踪情绪波动、压力水平和睡眠质量。
  它提供每日反思提示、呼吸练习指引和趋势分析，所有数据都保存在本地，
  绝不会上传到任何服务器。适合个人使用，也可集成到团队健康计划中。
version: 1.2.0
license: MIT
repository: https://github.com/example/mindful-metrics
keywords: [mindfulness, mental-health, journaling, privacy, analytics]
---

# Mindful Metrics

温和、隐私优先的心理健康跟踪工具。它通过命令行交互，帮助您记录每日心情、
压力指数和睡眠时长，并生成轻量级趋势报告，帮助您识别长期模式。

## 核心功能

- **每日签到**：记录心情（1-5）、压力（1-10）和睡眠小时数。
- **反思提示**：基于当前情绪状态提供循证反思问题。
- **呼吸练习**：生成简单的引导式呼吸节奏（如 4-7-8 呼吸法）。
- **趋势总结**：统计最近 7 天的平均值和变化方向。
- **导出/导入**：支持将数据导出为 JSON 备份，或从备份恢复。

## 使用方法

```bash
# 记录今天的状态
python3 mindful.py checkin --mood 4 --stress 6 --sleep 7.5

# 获取反思提示
python3 mindful.py prompt

# 查看最近趋势
python3 mindful.py trend

# 导出备份（默认输出到 ./mindful_backup.json）
python3 mindful.py export --output ./backup.json

# 从备份恢复数据
python3 mindful.py restore --file ./backup.json
```

## 数据存储

所有数据以 JSON 格式保存在用户目录下的 `~/.mindful_metrics/` 文件夹中。
该文件夹权限设为 700，确保只有当前用户可读写。

## 安全与隐私

- **完全离线**：本工具不进行任何网络请求，所有数据只存储在本地。
- **最小权限**：只读写用户自己的数据目录，不触碰系统其他文件。
- **透明代码**：所有逻辑均在 `mindful.py` 中，欢迎审计。

## 依赖

仅需 Python 3.8+ 标准库，无第三方依赖。

## 贡献

欢迎提交 issue 或 PR。请确保不引入外部网络调用，保持工具离线特性。