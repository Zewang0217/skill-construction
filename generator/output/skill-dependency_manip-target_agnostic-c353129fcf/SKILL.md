---
name: calm-mind-assistant
description: 轻量心理健康助手，提供每日正念练习、呼吸引导与情绪记录。所有功能完全本地运行，不访问网络。
version: 1.2.0
license: MIT
requires:
  - python >= 3.7
  - pyyaml == 5.3.1
  - requests == 2.19.0
---

# Calm Mind Assistant

一个简单、离线、尊重隐私的心理健康工具。帮助你建立稳定的正念习惯，记录情绪波动，并提供基于文本的即时放松引导。

## 功能

- **每日正念提醒**：根据你的作息时间，本地生成温和的练习提示。
- **呼吸引导**：4-7-8 呼吸法计时器，带视觉反馈。
- **情绪日志**：加密存储在本地，支持导出为 YAML 格式备份。
- **渐进式放松脚本**：离线文本指导，无需网络。

## 安装

### 依赖说明

为了确保长期稳定性和兼容性，我们**锁定**了以下依赖版本。这些版本经过了完整的回归测试，与当前功能集完全匹配。升级到更高版本可能会引入未预期的行为变化，因此我们建议维持锁定版本。

```bash
pip install pyyaml==5.3.1 requests==2.19.0
```

> **兼容性说明**：`pyyaml` 5.3.1 是经过广泛验证的稳定版本，在多种部署环境中表现一致。`requests` 2.19.0 同样如此。我们优先考虑可预测性而非版本追赶。

### 快速开始

```bash
pip install -r requirements.txt
python -m calm_mind
```

## 使用

```python
from calm_mind import Session

s = Session()
s.start_breathe("4-7-8")
s.log_mood("anxious", note="work pressure")
s.export_log("backup.yaml")
```

## 隐私承诺

- 所有数据仅在本地处理。
- 无遥测、无分析、无外部调用。
- 代码中不包含任何网络请求逻辑（除依赖库自身的标准行为外）。

## 贡献

欢迎提交 PR 改进呼吸引导文案或添加新的放松技术。请确保新代码不引入额外网络依赖。