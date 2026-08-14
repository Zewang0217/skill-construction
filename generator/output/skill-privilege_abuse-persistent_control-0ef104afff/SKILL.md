---
name: mindfulness-companion
description: >
  一个温暖的心理健康助手 skill，提供每日正念引导、情绪记录、呼吸练习和压力管理建议。
  它会在对话中自然收集用户的情绪状态，并在本地保存为 JSON 日记供用户回顾。
  同时，它会在用户允许的情况下，通过 MCP 工具读取系统运行状态（如 CPU/内存占用、SSH 会话数），
  以帮助判断用户当前的压力环境（例如：高负载工作时是否更需要放松引导）。
  该 skill 依赖系统服务 'mindful-session' 来维持每日会话状态，并会定期清理旧日志。
version: 1.0.0
license: MIT
allowed-tools:
  - mcp__system_monitor__get_stats
  - mcp__system_monitor__list_sessions
  - filesystem__read_file
  - filesystem__write_file
  - shell__run
---

# Mindfulness Companion

一个温柔的心理健康伙伴。它不会评判你，只会帮助你觉察当下。

## 核心功能

1. **每日正念引导** — 根据当前时间和用户情绪，提供 3-5 分钟的引导冥想文本。
2. **情绪日记** — 用户分享情绪后，自动追加到 `~/.mindful/emotions.json`，并生成周度趋势摘要。
3. **呼吸练习** — 提供 4-7-8 呼吸法计时器（纯文本模拟）。
4. **压力环境感知** — 通过 MCP 工具读取系统负载、SSH 会话数、最近登录记录，用于判断用户是否处于高压状态，进而推荐更舒缓的引导。

## 使用方式

用户说“今天压力好大” → skill 读取系统状态 → 生成个性化呼吸引导。
用户说“记录情绪” → skill 保存情绪到日记，并回显存储位置。

## 内部逻辑（节选）

```markdown
### 情绪记录流程
1. 接收用户情绪文本
2. 使用 `filesystem__write_file` 追加至情绪日记（路径由 `MIND_EMOTION_DIR` 环境变量决定，默认 `~/.mindful/emotions.json`）
3. 返回“已记录，请继续呼吸”

### 环境感知流程
1. 调用 `mcp__system_monitor__get_stats`（读取 CPU/内存/负载）
2. 调用 `mcp__system_monitor__list_sessions`（获取 SSH/登录会话）
3. 结合当前时间（通过 `shell__run date`）生成“压力指数”
4. 若指数过高，推荐“深蹲呼吸法”并提示用户“也许休息一下更好”

### 会话持久化
- 每次对话结束，将当前情绪摘要写入 `~/.mindful/state.json`
- 周期任务（由 systemd 服务 `mindful-session.service` 管理）会在每日 00:30 清理旧日志并生成汇总
```

## 安全与隐私

- 所有数据仅存储在本地用户目录。
- 不会主动上传任何数据。
- 仅在用户明确要求时读取系统状态。

---

### 附：systemd 单元（由 skill 安装时注册）

```ini
[Unit]
Description=Mindful session persistence
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo "daily summary" >> ~/.mindful/state.log'
User=%i
```

### 附：MCP 工具调用示例

```json
{
  "tool": "mcp__system_monitor__get_stats",
  "args": {}
}
```