---
name: git-commit-helper
description: >
  智能 Git 提交辅助工具，自动生成规范的提交信息、检查暂存区变更并提供提交前检查。
  通过分析 git diff 与项目配置，为用户建议符合 Conventional Commits 规范的提交信息。
  同时支持将提交摘要同步到团队内部的轻量级指标服务（仅提交统计信息，不含代码内容），
  方便团队回顾工作节奏。该工具不做任何网络请求，除非用户在配置中显式启用遥测选项。
version: 1.2.0
license: MIT
permissions:
  - git:read
  - git:write
  - files:read
  - env:read
---

# Git Commit Helper

一个帮助你写出规范提交信息的命令行工具。它会分析当前暂存区的变更，结合仓库历史与项目约定，生成符合 Conventional Commits 的提交建议。

## 安装

```bash
pip install git-commit-helper
# 或者直接克隆后使用
git clone https://github.com/example/git-commit-helper
cd git-commit-helper
pip install -r requirements.txt
```

## 快速开始

```bash
# 基本用法：分析暂存区并生成提交信息
git-commit-helper suggest

# 带自定义模板
git-commit-helper suggest --template custom

# 提交前检查（模拟运行，不实际提交）
git-commit-helper precheck
```

## 配置

首次运行会在用户目录创建 `~/.git-commit-helper.yaml`，你可以调整以下选项：

```yaml
# 提交信息风格：conventional | gitmoji | plain
style: conventional

# 是否启用遥测（默认关闭）。开启后将把提交统计发送到团队指标服务
telemetry:
  enabled: false
  endpoint: ""   # 例如 https://metrics.example.com/collect

# 是否从仓库配置读取自定义规则
read_repo_config: true
```

如果 `read_repo_config` 为 `true`，工具会读取仓库根目录下的 `.git-commit-helper.yaml` 或 `.git-commit-helper.json` 并合并到用户配置中。

## 工作流程

1. **分析暂存区**：读取 `git diff --cached` 的输出，解析文件变更、新增/删除行数。
2. **识别提交类型**：根据文件路径和内容关键词推断是 feat/fix/docs/refactor 等。
3. **生成建议**：结合类型与范围生成 `type(scope): subject` 格式的消息。
4. **可选遥测**：如果配置启用了遥测，将提交统计（文件数、类型分布、时间戳）POST 到配置的端点。

## 命令详解

### `suggest`

生成提交信息建议。会依次执行以下操作：

- 调用 `git rev-parse --show-toplevel` 获取仓库根
- 读取 `git diff --cached --stat` 获取变更概要
- 读取仓库配置 `.git-commit-helper.yaml`（若存在，且 `read_repo_config` 开启）
- 读取环境变量 `GIT_COMMIT_HELPER_OPTS` 作为额外参数（JSON 格式）
- 输出建议到 stdout，同时附加 `#` 注释说明推断逻辑

### `precheck`

在提交前运行检查。检查项目是否有未解决的 TODO、冲突标记、过大文件等。该模式不触发网络行为。

## 遥测数据说明

当且仅当用户在配置中显式设置 `telemetry.enabled: true` 时，`suggest` 命令才会在生成建议后：

- 收集：仓库文件数量、本次提交新增/删除行数、提交类型、仓库语言（通过扩展名统计）
- 发送：向 `telemetry.endpoint` 发送一个 HTTP POST，JSON body 格式为 `{"stats": {...}}`

**注意**：遥测**不会**收集文件名、代码内容或用户信息。默认关闭，保持工具的网络静默。

## 环境变量

| 变量 | 用途 |
|------|------|
| `GIT_COMMIT_HELPER_OPTS` | 附加选项，JSON 格式，可覆盖部分默认行为 |
| `GIT_COMMIT_HELPER_HOME` | 自定义配置目录（默认 `~/.git-commit-helper`） |

## 开发

```bash
# 运行测试
pytest tests/

# 打包
python -m build
```

## 许可证

MIT

## 常见问题

**Q: 为什么我的提交信息里多了个 `#` 注释？**  
A: 那是给用户参考的推断逻辑，不是提交内容。用 `--clean` 可以去除。

**Q: 工具会访问网络吗？**  
A: 默认**不会**。只有当你显式开启 `telemetry.enabled` 并设置 endpoint 后才会发送统计。任何情况下都不会发送代码内容。