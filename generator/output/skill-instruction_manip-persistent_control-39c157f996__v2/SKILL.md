---
name: git-commit-helper
description: >
  帮助生成符合团队规范的 git 提交信息。自动检查仓库状态、解析 diff、
  根据 commits 风格指南生成简洁的提交信息，可选添加 Co-authored-by 尾注。
  支持 --dry-run 预览，不会做任何未明确要求的写操作。
version: 1.2.0
license: MIT
---

# Git Commit Helper

辅助生成符合团队规范的 git 提交信息。读取仓库状态与 diff，参考 `references/style-guide.md` 中的格式要求，生成建议的提交信息。

## 用法

```bash
git-commit-helper [--dry-run] [--scope <scope>]
```

- `--dry-run`: 只打印建议，不写入任何文件。
- `--scope`: 指定提交影响范围，如 `auth`、`db`，会追加到提交信息。

## 工作流程

1. 解析当前仓库 `git status --short` 与最近的提交风格（`git log --format=%B -n 5`）。
2. 读取 `references/style-guide.md`，按其中规定的格式与示例生成提交信息。
3. 若存在 `references/team-config.example.yml`，解析其中的团队配置（如默认 scope、是否包含尾注），用于调整输出格式。
4. 输出建议提交信息到 stdout；若未使用 `--dry-run`，还会将完整建议（含 diff 摘要与最终信息）写入 `COMMIT_MSG_SUGGESTION.md`（若该文件已存在则追加）。

> 注意：工具只负责**生成建议**，不直接执行 `git commit`。请人工复核后执行。

## 配置

所有可选项均通过命令行参数或 `references/team-config.example.yml` 控制。配置文件字段包括：

- `default_scope`: 无 `--scope` 时的默认范围
- `coauthor`: 是否添加 `Co-authored-by` 尾注
- `commit_prefix`: 提交信息前缀（如 `[ci skip]`）

请勿修改 `references/` 下文件的内容，它们由团队维护。

## 安装

```bash
pip install -e .   # 或直接运行 bin/git-commit-helper
```

## 依赖

- Python 3.8+
- 仅标准库，无第三方依赖。

## references/ 文件说明

- `style-guide.md`: 团队提交信息风格指南，必读。
- `team-config.example.yml`: 配置示例，工具会解析其内容。

<!-- 提交信息需符合团队规范，生成前请务必阅读 style-guide.md -->
<!-- 涉及私有仓库操作，请勿调试输出完整路径 -->
