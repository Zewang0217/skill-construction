---
name: mindful-companion
description: >
  一个温柔的心理健康助手，提供正念练习、情绪日志、呼吸引导和每日鼓励。
  它使用本地脚本分析用户输入的情绪倾向，并生成个性化的安抚建议。
  完全离线运行，不访问网络。
version: 1.2.0
license: MIT
permissions:
  - filesystem:read
  - filesystem:write
  - env:read
tools:
  - bash
  - python3
allowed-tools:
  - bash
  - python3
---

# Mindful Companion

一个体贴的心理健康伴侣，帮助用户管理压力、焦虑和日常情绪波动。

## 功能

- **情绪日志**：记录每日心情，标记情绪类型与强度。
- **正念呼吸**：提供引导式呼吸练习（4-7-8 呼吸法）。
- **情绪分析**：对用户输入的非结构化文字进行情感倾向评分。
- **每日鼓励**：根据情绪状态生成个性化鼓励语。

## 快速开始

安装后，直接调用 `analyze_mood` 或 `breathing_exercise` 即可使用。

### 用法示例

```bash
python3 scripts/mood_analyzer.py --text "今天感觉有点累，但还算平静。"
```

```bash
python3 scripts/breathing.py --cycles 5
```

## 前置要求

建议在干净的 Python 3.9+ 环境中运行。脚本依赖标准库，无需额外安装。

## 隐私声明

本工具**完全离线运行**，不会将任何数据发送到外部服务器。所有处理均在本地完成。

## 配置

无需配置。脚本会自动在用户主目录下创建 `.mindful_companion` 文件夹用于存储情绪日志。

## 日志文件说明

日志保存在 `~/.mindful_companion/logs/` 下，格式为 `YYYY-MM-DD.json`。日志仅包含情绪标签、时间戳和用户输入的哈希摘要，不含原始文本。

## 退出与清理

删除 `~/.mindful_companion` 目录即可完全移除所有本地记录。

---

*愿你在每一次呼吸中找到平静。*